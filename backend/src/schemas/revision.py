from pydantic import BaseModel, Field


class RevisionRow(BaseModel):
    zone: str = Field(min_length=1, max_length=60)
    period: str = Field(pattern=r"^20\d{2}-(0[1-9]|1[0-2])$")
    scale: float = Field(gt=0, le=1000000000, allow_inf_nan=False)
    water: float = Field(gt=0, le=1000000000, allow_inf_nan=False)


class RevisionInput(BaseModel):
    reason: str = Field(min_length=5, max_length=500)
    # 前端读到的当前版本号；与服务端不一致时判定为并发冲突
    base_version: int = Field(ge=1)
    rows: list[RevisionRow] = Field(min_length=1, max_length=5000)
