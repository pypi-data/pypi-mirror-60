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
