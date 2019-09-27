import numpy as np
from pydantic import BaseModel

from core.config import TIME_DOMAIN_SUB_SAMPLED_RATIO, TIME_DOMAIN_DECIMAL


class SubSampledBinaryArray(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        raw = np.fromstring(v, dtype=np.float32)
        axis = np.linspace(0, raw.size, int(raw.size / TIME_DOMAIN_SUB_SAMPLED_RATIO), endpoint=False)
        return [round(float(item), TIME_DOMAIN_DECIMAL) for item in np.take(raw, axis.astype(np.int))]


class Msg(BaseModel):
    msg: str