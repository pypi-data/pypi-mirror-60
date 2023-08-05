from .helpers import DateParser
from .models import CloseReport
from pyptax import settings
from pyptax.exceptions import UnavailableDataError


class CloseResource:
    path = settings.CLOSE_RESOURCE

    def __init__(self, date):
        self.date = date
        self.parsed_date = DateParser(date).parse()

    @property
    def params(self):
        return f"@dataCotacao={self.parsed_date!r}&$format=json"

    def parse(self, raw_data):
        try:
            data = raw_data["value"][0]
        except IndexError:
            raise UnavailableDataError(
                f"Unavailable rates for the requested date:{self.date!r}"
            )
        datetime = data["dataHoraCotacao"]
        bid = f"{data['cotacaoCompra']:.4f}"
        ask = f"{data['cotacaoVenda']:.4f}"
        return CloseReport(datetime, bid, ask)
