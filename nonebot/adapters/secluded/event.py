from typing import Literal, Optional
from typing_extensions import override

from pydantic import BaseModel
from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump

from .message import Message, MessageSegment

class Event(BaseEvent):
    pass

class MessageEvent(Event):
    def __init__(
        self,
        message: Message,
        account_id: str,
        user_id: str,
        user_name: str,
        user_group_name: str,
        group_id: Optional[str],
        group_name: Optional[str],
        msg_id: str
    ):
        super().__init__()
        self.message = message
        self.account_id = account_id
        self.user_id = user_id
        self.user_name = user_name
        self.user_group_name = user_group_name
        self.group_id = group_id
        self.group_name = group_name
        self.msg_id = msg_id

    @override
    def get_type(self) -> Literal['message']:
        return 'message'
    
    @override
    def get_event_name(self) -> str:
        return self.account_id
    
    @override
    def get_event_description(self) -> str:
        return ''
    
    @override
    def get_message(self) -> Message:
        return self.message
    
    @override
    def get_plaintext(self) -> str:
        plaintext: str = ''
        for i in self.message:
            if i.type == 'text':
                plaintext += i.data['text']
        return plaintext
    
    @override
    def get_user_id(self) -> str:
        return self.user_id
    
    @override
    def get_session_id(self) -> str:
        return f'{self.account_id}/{self.group_id}/{self.user_id}'
    
    @override
    def is_tome(self) -> bool:
        for i in self.message:
            if i.type == 'at':
                if i.data['user_id'] == self.account_id:
                    return True
        return False
    
    def is_group(self) -> bool:
        return not self.group_id is None

    def get_group_id(self) -> str:
        return self.group_id if not self.group_id is None else ''
    
    def get_group_name(self) -> str:
        return self.group_name if not self.group_name is None else ''
    
    def get_user_name(self) -> str:
        return self.user_name
    
    def get_user_group_name(self) -> str:
        return self.user_group_name
    
    def get_msg_id(self) -> str:
        return self.msg_id

class RequestEvent(Event):
    def __init__(
        self,
        description: MessageSegment
    ):
        super().__init__()
        self.description = description
    
    @override
    def get_type(self) -> Literal['request']:
        return 'request'
    
    @override
    def get_event_name(self) -> str:
        return self.description.type
    
    @override
    def get_event_description(self) -> str:
        return str(self.description)
    
    def get_request(self) -> MessageSegment:
        return self.description

    @override
    def get_message(self) -> Message:
        return Message([self.description])
    
    @override
    def get_plaintext(self) -> str:
        return str(self.description)
        
    @override
    def is_tome(self) -> Literal[False]:
        return False
    
    @override
    def get_user_id(self) -> str:
        return self.description.data['user_id'] if 'user_id' in self.description.data.keys() else ''
    
    @override
    def get_session_id(self) -> Literal['']:
        return ''

class NoticeEvent(Event):
    def __init__(
        self,
        description: MessageSegment
    ):
        super().__init__()
        self.description: MessageSegment = description
    
    @override
    def get_type(self) -> Literal['notice']:
        return 'notice'
    
    @override
    def get_event_name(self) -> str:
        return self.description.type
    
    @override
    def get_event_description(self) -> str:
        return str(self.description)
    
    def get_request(self) -> MessageSegment:
        return self.description

    @override
    def get_message(self) -> Message:
        return Message([self.description])
    
    @override
    def get_plaintext(self) -> str:
        return str(self.description)
        
    @override
    def is_tome(self) -> Literal[False]:
        return False
    
    @override
    def get_user_id(self) -> str:
        return self.description.data['user_id'] if 'user_id' in self.description.data.keys() else ''
    
    @override
    def get_session_id(self) -> Literal['']:
        return ''

class MetaEvent(Event):
    def __init__(
        self,
        description: MessageSegment
    ):
        super().__init__()
        self.description = description
    
    @override
    def get_type(self) -> Literal['meta_event']:
        return 'meta_event'
    
    @override
    def get_event_name(self) -> str:
        return self.description.type
    
    @override
    def get_event_description(self) -> str:
        return str(self.description)
    
    def get_request(self) -> MessageSegment:
        return self.description

    @override
    def get_message(self) -> Message:
        return Message([self.description])
    
    @override
    def get_plaintext(self) -> str:
        return str(self.description)
        
    @override
    def is_tome(self) -> Literal[False]:
        return False
    
    @override
    def get_user_id(self) -> str:
        return self.description.data['user_id'] if 'user_id' in self.description.data.keys() else ''
    
    @override
    def get_session_id(self) -> Literal['']:
        return ''

class OtherEvent(Event):
    def __init__(
        self,
        description: MessageSegment
    ):
        super().__init__()
        self.description = description
    
    @override
    def get_type(self) -> Literal['other_event']:
        return 'other_event'
    
    @override
    def get_event_name(self) -> str:
        return self.description.type
    
    @override
    def get_event_description(self) -> str:
        return str(self.description)
    
    def get_request(self) -> MessageSegment:
        return self.description

    @override
    def get_message(self) -> Message:
        return Message([self.description])
    
    @override
    def get_plaintext(self) -> str:
        return str(self.description)
        
    @override
    def is_tome(self) -> Literal[False]:
        return False
    
    @override
    def get_user_id(self) -> str:
        return self.description.data['user_id'] if 'user_id' in self.description.data.keys() else ''
    
    @override
    def get_session_id(self) -> Literal['']:
        return ''