from typing import TYPE_CHECKING, Union, Any
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot
from nonebot.message import handle_event

from .event import Event, MessageEvent
from .message import Message, MessageSegment

if TYPE_CHECKING:
    from .adapter import Adapter

class Bot(BaseBot):
    adapter: 'Adapter' # type: ignore

    @override
    async def send( # type: ignore
        self,
        event: MessageEvent,
        message: Union[str, Message, MessageSegment],
        reply: bool = False,
        **kwargs: Any,
    ) -> Any:
        if not event.group_id is None:
            if type(message) == str:
                await self.adapter.send(
                    event, 
                    Message([
                        MessageSegment('text', {'text': message})
                    ]),
                    reply
                )
            elif type(message) == MessageSegment:
                await self.adapter.send(
                    event,
                    Message([
                        message
                    ]),
                    reply
                )
            elif type(message) == Message:
                await self.adapter.send(event, message, reply)
        else:
            pass
    
    async def handle_event(self, event: Event):
        await handle_event(self, event)
