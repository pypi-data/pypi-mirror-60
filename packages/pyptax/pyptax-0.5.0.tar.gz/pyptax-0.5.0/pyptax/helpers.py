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


class BulletinTypeParser:
    BULLETIN_TYPES = {
        "Abertura": "open",
        "Intermediário": "intermediary",
        "Fechamento PTAX": "close",
    }

    def __init__(self, bulletin_type):
        self.bulletin_type = bulletin_type

    def parse(self):
        return self.BULLETIN_TYPES.get(self.bulletin_type)
