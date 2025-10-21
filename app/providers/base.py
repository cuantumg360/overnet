from dataclasses import dataclass

@dataclass
class ProviderResult:
    provider: str
    model: str
    text: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_est_eur: float

class ProviderError(Exception):
    pass
