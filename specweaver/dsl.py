import yaml
from .schema import ProtocolDSL

def load_protocol(path: str) -> ProtocolDSL:
    raw = yaml.safe_load(open(path, "r", encoding="utf-8"))
    return ProtocolDSL(**raw)
