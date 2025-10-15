from transformers import pipeline
import time

_GEN = None
_CLS = None

def load_models():
    global _GEN, _CLS
    if _GEN is None:
        _GEN = pipeline("text-generation", model="gpt2")
    if _CLS is None:
        _CLS = pipeline("sentiment-analysis")

def route_task(task: str, text: str):
    load_models()
    start = time.time()

    if task == "generate":
        out = _GEN(text, max_new_tokens=50, do_sample=False)[0]["generated_text"]
        model_name = "gpt2"
        tokens = len(out.split())
    elif task == "sentiment":
        out = _CLS(text)[0]
        model_name = "distilbert-sst2"
        tokens = len(text.split())
    else:
        return {"error": "unknown_task"}, None

    latency_ms = int((time.time() - start) * 1000)
    cost = 0.0
    return {"task": task, "model": model_name, "output": out}, {"latency_ms": latency_ms, "cost": cost, "tokens": tokens}
