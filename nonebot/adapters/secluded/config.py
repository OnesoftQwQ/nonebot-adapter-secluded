from pydantic import Field, BaseModel


class Config(BaseModel):
    secluded_host: str
    secluded_token: str | int
    secluded_plugin_id: str | int = 'nonebot'
    secluded_plugin_name: str | int = 'nonebot'
