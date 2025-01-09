import asyncio
import json
from typing import Any, Literal, Optional
from typing_extensions import override

from nonebot import get_plugin_config
from nonebot.exception import WebSocketClosed
from nonebot.utils import DataclassEncoder, escape_tag
from nonebot.drivers import (
    URL,
    Driver,
    Request,
    Response,
    WebSocket,
    ForwardDriver,
    ReverseDriver,
    HTTPServerSetup,
    WebSocketServerSetup
)
import nonebot.drivers.websockets

from nonebot.adapters import Adapter as BaseAdapter
import websockets.asyncio
import websockets.asyncio.client

from .bot import Bot
from .event import Event, MessageEvent, OtherEvent, RequestEvent, NoticeEvent, MetaEvent
from .config import Config
from .message import Message, MessageSegment
from .log import log

import websockets

class Adapter(BaseAdapter):

    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.adapter_config = get_plugin_config(Config)
        self.task: Optional[asyncio.Task] = None
        self.ws: Optional[websockets.asyncio.client.ClientConnection] = None
        self.seq: int = 1
        self.account_id: Optional[str] = None
        self.setup()

    def setup(self):
        # if not isinstance(self.driver, nonebot.drivers.websockets):
        #     # 判断用户配置的Driver类型是否符合适配器要求，不符合时应抛出异常
        #     raise RuntimeError(
        #         f"Current driver {self.config.driver} doesn't support websocket client connections!"
        #         f"{self.get_name()} Adapter need a WebSocket Client Driver to work."
        #     )
        # 在 NoneBot 启动和关闭时进行相关操作
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self):
        self.task = asyncio.create_task(self._forward_ws())
    
    async def shutdown(self):
        pass

    async def _forward_ws(self):
        log(
            'INFO',
            '开始建立连接'
        )
        while True:
            try:
                self.ws = await websockets.asyncio.client.connect(self.adapter_config.secluded_host)
                log(
                    'INFO',
                    '连接成功! 开始发送上线包'
                )
                send: Message.OriginMessage.Send = {
                    'seq': self.seq,
                    'cmd': 'SyncOicq',
                    'rsp': True,
                    'data': {
                        'pid': str(self.adapter_config.secluded_plugin_id),
                        'name': str(self.adapter_config.secluded_plugin_name),
                        'token': str(self.adapter_config.secluded_token)
                    }
                }
                await self.ws.send(
                    json.dumps(send)
                )
                self.seq += 1
                recv: Message.OriginMessage.Recv = json.loads(await self.ws.recv(True))
                if recv['data']['status'] == True: # type: ignore
                    log(
                        'INFO',
                        '上线成功!'
                    )
                else:
                    raise self.TokenIncorrentError(f'Token错误! 错误Token: {self.adapter_config.secluded_token}')

                try:
                    log(
                        'INFO',
                        '等待获取账号ID'
                    )
                    while True:
                        recv = json.loads(await self.ws.recv(True))
                        if recv['cmd'] == 'PushOicqMsg' and 'Account' in recv['data'][0].keys():
                            self.account_id = recv['data'][0]['Account']
                            log(
                                'INFO',
                                f'获取账号ID成功: {self.account_id}'
                            )
                            break
                    self._handle_connect()
                    if 'Uin' in recv['data'][0].keys():
                        await self._forward(recv)
                    
                    while True:
                        recv = json.loads(await self.ws.recv(True))
                        if 'Uin' in recv['data'][0].keys():
                            await self._forward(recv)
                except json.JSONDecodeError as e:
                    log(
                        'WARNING',
                        'JSON解析失败!',
                        e
                    )
            except websockets.exceptions.ConnectionClosedError as e:
                if self.ws is None:
                    log(
                        'ERROR',
                        '连接失败, 5秒后重试',
                        e
                    )
                else:
                    log(
                        'ERROR',
                        '连接中断, 5秒后重试',
                        e
                    )
                await asyncio.sleep(5)
            finally:
                if not self.ws is None:
                    await self.ws.close()
                self._handle_disconnect()
                self.ws = None

    async def _forward(self, recv: Message.OriginMessage.Recv):
        log(
            'INFO',
            str(recv)
        )
        event = self.payload_to_event(recv)
        asyncio.create_task(self.bot.handle_event(event))

    @classmethod
    def payload_to_event(cls, payload: Message.OriginMessage.Recv) -> Event:
        """根据平台事件的特性，转换平台 payload 为具体 Event

        Event 模型继承自 pydantic.BaseModel，具体请参考 pydantic 文档
        """

        # 做一层异常处理，以应对平台事件数据的变更
        try:
            keys = []
            for i in payload['data']:
                for x in i.keys():
                    keys.append(x)
            event_type: Literal['message', 'request', 'notice', 'meta_event', 'other_event'] | None = None

            for i in keys:
                i = str(i)
                if i in (
                    'AtAll',
                    'AtUin',
                    'AtName',
                    'Gif',
                    'Img',
                    'Text',
                    'Audio',
                    'Video',
                    'GroupFileUpload'
                ):
                    event_type = 'message'
                elif i in (
                    'NewFriendNotify',
                    'GroupNotify',
                ):
                    event_type = 'request'
                elif i in (
                    'GroupNewMember',
                    'GroupMemberSignout',
                    'GroupMemverNickModify',
                    'GroupModifyAdmin',
                    'GroupModifyNickModify',
                    'GroupProhibitAll',
                    'GroupProhibitMember',
                    'GroupBeatABeat',
                    'GroupEssence',
                    'GroupDissolut'
                ):
                    event_type = 'notice'
                elif i in (
                    'Heartbeat',
                    'Heartbeating',
                    'Offline',
                    'Goline',
                    'GolineWindows',
                    'OfflineWindows',
                    'System',
                    'Online'
                ):
                    event_type = 'meta_event'
            if event_type is None:
                event_type = 'other_event'
            
            first_data = payload['data'][0]
            event_group = 'Group' in first_data.keys()
            event_group_id = first_data['GroupId'] if event_group else None
            account_id = first_data['Account']            

            messages: list[MessageSegment] = []
            
            match event_type:
                case 'message':
                    for i in payload['data'][1:]:
                        items = list(i.items())
                        first_item = items[0]
                        if first_item[0] == 'Text':
                            messages.append(MessageSegment('text', {'text': first_item[1]}))
                        elif first_item[0] == 'AtName':
                            messages.append(MessageSegment('at', {'user_name': items[0][1], 'user_id': items[1][1], 'text': f'@{items[0][1]}'}))
                        elif first_item[0] == 'AtAll':
                            messages.append(MessageSegment('at_all', {}))
                        elif first_item[0] == 'Img':
                            messages.append(MessageSegment('img', {'type': 'img', 'url': items[0][1]}))
                        elif first_item[0] == 'Gif':
                            messages.append(MessageSegment('img', {'type': 'gif', 'url': items[0][1]}))
                    return MessageEvent(
                        message=Message(messages),
                        account_id=first_data['Account'],
                        user_id=first_data['Uin'],
                        user_name=first_data['UinName'],
                        user_group_name=first_data['OpName'],
                        group_id=first_data['GroupId'] if 'Group' in first_data.keys() else None,
                        group_name=first_data['GroupName'] if 'Group' in first_data.keys() else None,
                        msg_id=first_data['MsgId']
                    )
                case 'request':
                    if 'GroupNotify' in first_data.keys():
                        return RequestEvent(
                            MessageSegment(
                                'group_new_member_request',
                                {
                                    'user_id': first_data['Uin'],
                                    'user_name': first_data['UinName']
                                }
                            )
                        )
                    elif 'NewFriendNotify' in first_data.keys():
                        return RequestEvent(
                            MessageSegment(
                                'new_friend_request',
                                {
                                    'user_id': first_data['Uin'],
                                    'user_name': first_data['UinName']
                                }
                            )
                        )
                case 'notice':
                    if 'GroupNewMember' in first_data.keys():
                        return NoticeEvent(
                            MessageSegment(
                                'group_new_member',
                                {
                                    'user_id': first_data['Uin'],
                                    'user_name': first_data['UinName']
                                }
                            )
                        )
                    elif 'GroupMemberSignout' in first_data.keys():
                        return NoticeEvent(
                            MessageSegment(
                                'group_member_signout',
                                {
                                    'user_id': first_data['Uin'],
                                    'user_name': first_data['UinName']
                                }
                            )
                        )
                case 'meta_event':
                    if 'Heartbeat' in first_data.keys():
                        return MetaEvent(
                            MessageSegment(
                                'Heartbeat'
                            )
                        )
            
            return OtherEvent(
                MessageSegment(
                    ''
                )
            )
        except Exception as e:
            # 无法正常解析为具体 Event 时，给出日志提示
            log(
                "WARNING",
                f"Parse event error: {str(payload)}",
                e
            )
            # 也可以尝试转为基础 Event 进行处理
            raise Exception

    def message_to_origin(self, event: MessageEvent, message: Message, reply: bool = False) -> Message.OriginMessage.Send:
        data: list[MessageSegment.OriginSegment.Send] = [
            MessageSegment.OriginSegment.Send({
                'Account': self.account_id if not self.account_id is None else '',
            })
        ]
        if not event.group_id is None:
            data[0]['Group'] = 'Group'
            data[0]['GroupId'] = event.group_id if not event.group_id is None else ''
        if reply:
            data[0]['Reply'] = event.get_msg_id()
        for i in message:
            match i.type:
                case 'text':
                    data.append(
                        MessageSegment.OriginSegment.Send({
                            'Text': i.data['text']
                        })
                    )
                case 'img':
                    data.append(
                        MessageSegment.OriginSegment.Send({
                            'Img': i.data['url']
                        })
                    )
                case 'gif':
                    data.append(
                        MessageSegment.OriginSegment.Send({
                            'Gif': i.data['url']
                        })
                    )
                case 'at':
                    data.append(
                        MessageSegment.OriginSegment.Send({
                            'AtName': i.data['user_name'],
                            'AtUin': i.data['user_id']
                        })
                    )
                case 'at_all':
                    data.append(
                        MessageSegment.OriginSegment.Send({
                            'AtAll': 'AtAll'
                        })
                    )
        
        send: Message.OriginMessage.Send = {
            'cmd': 'SendOicqMsg',
            'rsp': True,
            'seq': self.seq,
            'data':data
        }
        return send
    
    class TokenIncorrentError(Exception):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)

    def _handle_connect(self):
        self.bot = Bot(self, self_id=self.account_id)  # 实例化 Bot  # type: ignore
        self.bot_connect(self.bot)  # 建立 Bot 连接

    def _handle_disconnect(self):
        self.bot_disconnect(self.bot)  # 断开 Bot 连接

    @classmethod
    @override
    def get_name(cls) -> str:
        return 'secluded'

    @override
    async def _call_api(self, data: Message.OriginMessage.Send) -> Any: # type: ignore
        while True:
            if not self.ws is None:
                await self.ws.send(json.dumps(data))
                break
            else:
                await asyncio.sleep(5)

    async def send(self, event: MessageEvent, message: Message, reply: bool = False):
        origin_message = self.message_to_origin(event, message, reply)
        print(origin_message)
        await self._call_api(origin_message)