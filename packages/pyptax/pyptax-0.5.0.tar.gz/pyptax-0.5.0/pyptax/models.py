from dataclasses import asdict, dataclass
from typing import List, Optional

from tabulate import tabulate


class BaseBulletin:
    bulletins = None

    @property
    def as_dict(self):
        return asdict(self)

    def display(self, fmt: Optional[str] = "psql") -> str:
        rows = (
            (bulletin.datetime, bulletin.bid, bulletin.ask, bulletin.bulletin_type)
            for bulletin in self.bulletins
        )
        return tabulate(rows, headers=self.bulletins[0].as_dict.keys(), tablefmt=fmt)


@dataclass
class Bulletin(BaseBulletin):
    datetime: str
    bid: float
    ask: float
    bulletin_type: str

    def display(self, fmt: Optional[str] = "psql") -> str:
        return tabulate(self.as_dict.items(), tablefmt=fmt)


@dataclass
class HistoricalBulletin(BaseBulletin):
    start_date: str
    end_date: str
    bulletins: List[Bulletin]


@dataclass
class IntermediaryBulletin(BaseBulletin):
    date: str
    bulletins: List[Bulletin]
