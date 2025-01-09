from typing import Any, Literal, Type, TypedDict, Union, Mapping, Iterable
from typing_extensions import override

from nonebot.adapters import Message as BaseMessage, MessageSegment as BaseMessageSegment


class MessageSegment(BaseMessageSegment["Message"]):
    type: Literal['text', 'at', 'at_all', 'img', 'gif'] # type: ignore
    data: dict[Literal['text', 'url', 'user_id', 'user_name', 'user_group_name'], Any] # type: ignore

    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def __str__(self) -> str:
        match self.type:
            case 'text':
                return self.data['text']
            case 'at':
                return f'@{self.data['user_group_name']}'
            case 'at_all':
                return '@全体成员'
            case _:
                return ''
        

    @override
    def is_text(self) -> bool:
        return self.type == 'text'
    
    class OriginSegment:
        class Recv(
            dict[
                Literal['AtAll', 'AtUin', 'AtName', 'Id', 'Ok', 'No', 'Op', 'OpUid', 'All', 'Get', 'Gif', 'Img', 'Ptt', 'Uid', 'Uin', 'Url', 'Xml', 'Code', 'Info', 'Json', 'Text', 'Temp', 'Time', 'Type', 'Emoid', 'Flash', 'MsgId', 'Reply', 'Title', 'Value', 'Audio', 'Video', 'Width', 'Bubble', 'Heigth', 'Notice', 'People', 'Refresh', 'UinName', 'UinNick', 'Typeface', 'Withdraw', 'OpName', 'OpNick', 'Agree', 'Refuse', 'Ignore', 'Account', 'Open', 'Close', 'MD5', 'Size', 'Offset', 'Add', 'Remove', 'Seq', 'EmojiFace', 'EmojiSuper', 'EmojiSuperQQ', 'ProgressPush', 'PokeID', 'PokeIDSub', 'PokeMsg', 'PokeSize', 'Dice', 'WindowJitter', 'FlashWord', 'FingerGuess', 'HeadPortrait', 'AppId', 'MultiMsg', 'MultiMsgGet', 'MultiMsgPut', 'Friend', 'FriendListDisable', 'FriendListGet', 'FriendListGetName', 'FriendListGetNick', 'FriendBeatABeat', 'FriendMsgCacheGet', 'Group', 'Owner', 'GroupId', 'GroupName', 'GroupListDisable', 'GroupListGet', 'GroupListGetName', 'GroupMemberListGet', 'GroupMemberListGetAdmin', 'GroupMemberListGetInactive', 'GroupMemberListGetProhibit', 'GroupMemberListGetInfo', 'GroupMemberSignout', 'GroupMemberNickModify', 'GroupModifyAdmin', 'GroupModifySpecialTitle', 'GroupNotify', 'GroupProhibitAll', 'GroupProhibitMember', 'GroupMsgCacheGet', 'GroupMsgAnonymous', 'GroupMsgSetNotDisturb', 'GroupAnonymous', 'GroupEnterState', 'GroupInvitationFriend', 'GroupNewMember', 'GroupMusic', 'GroupBeatABeat', 'GroupEssence', 'GroupDissolut', 'GroupClockin', 'GroupFile', 'GroupFileListGet', 'GroupFileUpload', 'GroupFileCreate', 'GroupFileRemove', 'GroupFileRemoveFolder', 'GroupFileMove', 'GroupFileRename', 'GroupStick', 'Guild', 'TinyId', 'GuildId', 'GuildCode', 'ChannelId', 'GuildType', 'GuildName', 'ChannelName', 'GuildMsgCacheGet', 'GuildMemberSignout', 'GuildEssence', 'System', 'Online', 'Goline', 'GolineRetry', 'Offline', 'GolineWindows', 'OfflineWindows', 'Heartbeat', 'HeartbeatLong', 'FavoriteCard', 'FavoriteCardListGet', 'FavoritePersonSign', 'NewFriendNotify', 'UserSearch', 'UserInfoGet', 'UserInfoModify', 'UserGroupJoin', 'UserGroupSignout', 'UserFriendAdd', 'UserFriendRemove', 'UserSigninDay', 'UserSigninNight', 'UserGolineMode', 'OntimeTask', 'Qzone', 'SaySay', 'Skey', 'Age', 'Gender', 'Nick', 'Name', 'MemberLevel', 'JoinTime', 'LastSpeakTime', 'SpecialTitle', 'Level', 'Location', 'Debug', 'CacheNewFile', 'Unauthorized', 'OicqWebScanCodeLogin', 'SignJson', 'CustomJson', 'JSON_KG', 'JSON_WY', 'JSON_QQ', 'JSON_KW', 'JSON_JSHU', 'JSON_BAIDU', 'JSON_YK', 'JSON_IQY', 'JSON_BD', 'JSON_BL', 'JSON_KS', 'JSON_MG', 'JSON_QQLLQ', 'JSON_QQKJ', 'JSON_5SING', 'GM_Unknown', 'GM_Official', 'GM_Android', 'GM_AndroidPad', 'GM_AndroidWatch'],
                str
            ]
        ):
            pass

        class RecvFirst(TypedDict):
            Account: str
            Bubble: str
            Debug: str
            Group: str
            GroupId: str
            GroupName: str
            MsgId: str
            MsgType: str
            Op: str
            OpName: str
            OpUid: str
            Title: str
            Typeface: str
            Uid: str
            Uin: str
            UinName: str
            UserGolineMode: str
            Heartbeat: int

        class RecvOnline(TypedDict):
            status: bool

        class Send(dict[Literal['Account', 'Group', 'GroupId', 'Reply', 'MsgId', 'Text', 'AtUin', 'AtName', 'AtAll', 'Reply', 'Img', 'Gif'], str]):
            pass


class Message(BaseMessage[MessageSegment]):

    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        raise NotImplementedError
    
    class OriginMessage:
        class Recv(TypedDict):
            """
            seq: 对应发包序号
            cmd: 应答包标识
            data: 消息内容
            """
            seq: int
            cmd: Literal['Response', 'PushOicqMsg']
            data: list[Union['MessageSegment.OriginSegment.RecvFirst', 'MessageSegment.OriginSegment.Recv']] | Any

        class Send(TypedDict):
            """
            seq: 包序号, 每次发包+1
            cmd: 发送消息的命令
            rsp: 是否需要应答包
            data: 消息内容
            """
            seq: int
            cmd: Literal['SendOicqMsg', 'SyncOicq']
            rsp: bool
            data: list['MessageSegment.OriginSegment.Send'] | dict[Literal['pid', 'name', 'token'], str]
