from dataclasses import dataclass
from typing import List


@dataclass
class Archive:
    bots: bool
    users: bool
    groups: bool
    pinned: bool


@dataclass
class Unread:
    folder_id: int
    add_bots: bool
    lifetime: int
    ignore: List[str]


@dataclass
class Config:
    unread: Unread
    archive: Archive
