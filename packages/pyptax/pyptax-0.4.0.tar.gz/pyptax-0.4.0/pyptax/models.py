from typing import Optional

from tabulate import tabulate


class CloseReport:
    def __init__(self, datetime, bid, ask):
        self.datetime = datetime
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f"{self.datetime} - bid: {self.bid} - ask: {self.ask}"

    def __repr__(self):
        return f"CloseReport(datetime={self.datetime}, bid={self.bid}, ask={self.ask})"

    @property
    def as_dict(self):
        return self.__dict__

    def display(self, fmt: Optional[str] = "psql") -> str:
        return tabulate(map(list, self.as_dict.items()), tablefmt=fmt)
