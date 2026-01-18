from datetime import datetime

from sqlmodel import SQLModel


class BaseModel(SQLModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(timespec="seconds") + "Z"
            if v.tzinfo is None
            else v.astimezone().isoformat(timespec="seconds")
        }
