from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    url: str
    summary: str = ""
    source: str = ""
    score: int = 0
    metrics: dict = field(default_factory=dict)
