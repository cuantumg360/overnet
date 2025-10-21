import time
from .base import ProviderResult

def call_openai(prompt: str, max_tokens: int = 256) -> ProviderResult:
    t0 = time.time()
    # MOCK: devuelve eco. Sustituir por SDK oficial cuando quieras.
    text = f"[OPENAI MOCK] {prompt[:200]}"
    latency_ms = int((time.time() - t0) * 1000) or 5
    # estimaciones simples
    tokens_in = max(1, len(prompt)//4)
    tokens_out = min(max_tokens, 64)
    cost_per_1k = 0.5  # EUR aprox
    cost = ((tokens_in + tokens_out)/1000.0) * cost_per_1k
    return ProviderResult(
        provider="openai",
        model="gpt-4o-mini",
        text=text,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        cost_est_eur=round(cost, 4),
    )
