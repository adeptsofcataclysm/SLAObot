from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Raider:
    name: str
    class_: str
    spec: str
    raider_id: int
    gear: List[Dict] = field(default_factory=list)
    total: float = field(default_factory=lambda: float('+inf'))
