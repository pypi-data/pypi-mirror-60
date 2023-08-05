from .helpers import DateParser
from .models import CloseReport
from pyptax import settings


class CloseResource:
    path = settings.CLOSE_RESOURCE

    def __init__(self, date):
        self.date = DateParser(date).parse()

    @property
    def params(self):
        return f"@dataCotacao={self.date!r}&$format=json"

    @staticmethod
    def parse(raw_data):
        data = raw_data["value"][0]
        datetime = data["dataHoraCotacao"]
        bid = f"{data['cotacaoCompra']:.4f}"
        ask = f"{data['cotacaoVenda']:.4f}"
        return CloseReport(datetime, bid, ask)
