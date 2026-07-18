import random


def sample(topics: list[str], n: int = 3) -> list[str]:
    return random.sample(topics, min(n, len(topics)))
