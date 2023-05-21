from dataclasses import dataclass
from typing import List
from typing import Dict, Union


@dataclass
class Archive:
    bots: bool
    users: bool
    groups: bool
    pinned: bool

    @staticmethod
    def from_dict(d: Union[Dict, None]) -> 'Archive':
        bots = d.get("bots", None)
        users = d.get("users", None)
        groups = d.get("groups", None)
        pinned = d.get("pinned", None)

        return Archive(bots, users, groups, pinned)


@dataclass
class Unread:
    folder_id: int
    add_bots: bool
    lifetime: int
    ignore: List[str]

    @staticmethod
    def from_dict(d: Union[Dict, None]) -> 'Unread':
        folder_id = d.get("folder_id", None)
        add_bots = d.get("add_bots", None)
        lifetime = d.get("lifetime", None)
        ignore = d.get("ignore", None)

        return Unread(folder_id, add_bots, lifetime, ignore)


@dataclass
class Config:
    unread: Unread
    archive: Archive

    @staticmethod
    def from_dict(d: Union[Dict, None]) -> 'Config':
        unread = Unread.from_dict(d.get("unread", None))
        archive = Archive.from_dict(d.get("archive", None))

        return Config(unread, archive)
