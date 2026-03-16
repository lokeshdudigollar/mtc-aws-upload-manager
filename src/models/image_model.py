from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Image:
    userId: str
    imageId: str
    createdAt: str
    status: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    s3Key: Optional[str] = None
    idempotencyKey: Optional[str] = None

    def to_dict(self):
        return asdict(self)