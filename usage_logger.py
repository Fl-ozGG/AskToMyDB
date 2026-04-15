from dataclasses import dataclass
import json
import time


@dataclass
class LLMUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def log_usage(step: str, usage: LLMUsage):
    data = {
        "step": step,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "timestamp": time.time()
    }

    print(json.dumps(data))