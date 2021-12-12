from dataclasses import dataclass, field


@dataclass
class Raider:
    name: str
    class_: str
    spec: str
    total: float = field(default_factory=lambda: float('+inf'))
