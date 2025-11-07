from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

Handshake = Literal["axi_valid_ready", "wishbone_classic"]
Addressing = Literal["byte", "word"]

class ProtocolDSL(BaseModel):
    protocol: str
    data_width: int = Field(..., gt=0)
    addr_width: int = Field(..., gt=0)
    addressing: Addressing
    handshake: Handshake
    byte_enable: Optional[str] = None
    byte_enable_width: Optional[int] = None
    max_outstanding: int = 1
    description: Optional[str] = None

    @validator("byte_enable_width")
    def _be_width_ok(cls, v, values):
        if values.get("data_width") and v:
            assert v * 8 <= values["data_width"], "byte_enable_width * 8 must be ≤ data_width"
        return v
