from datetime import datetime

from pyptax.exceptions import DateFormatError


class DateParser:
    def __init__(self, date):
        self.date = date
        self.datetime = self._datetime()

    def _datetime(self):
        try:
            return datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise DateFormatError(
                f"{self.date!r} does not match the required format YYYY-MM-DD"
            )

    def parse(self, fmt="%m-%d-%Y"):
        return self.datetime.strftime(fmt)
