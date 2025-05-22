from enum import Enum

from pydantic import BaseModel, Field


class SettingType(str, Enum):
    int = "int"
    float = "float"
    str = "str"
    bool = "bool"


class SettingPatchWithKey(BaseModel):
    key: str = Field(..., title="Setting key")
    value: str | None = Field(..., title="Setting value")
    type: SettingType | None = Field(None, title="Setting type")

    class Config:
        from_attributes = True
