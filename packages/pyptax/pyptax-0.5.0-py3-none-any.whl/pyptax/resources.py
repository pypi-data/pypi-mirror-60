from pyptax import settings
from pyptax.exceptions import UnavailableDataError
from pyptax.helpers import BulletinTypeParser, DateParser
from pyptax.models import Bulletin, HistoricalBulletin, IntermediaryBulletin


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
        bid = data["cotacaoCompra"]
        ask = data["cotacaoVenda"]
        return Bulletin(datetime, bid, ask, "close")


class HistoricalResource:
    path = settings.HISTORICAL_RESOURCE

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.parsed_start = DateParser(start_date).parse()
        self.parsed_end = DateParser(end_date).parse()

    @property
    def params(self):
        return f"@dataInicial={self.parsed_start!r}&@dataFinalCotacao={self.parsed_end!r}&$format=json"

    def parse(self, raw_data):
        bulletins_list = raw_data["value"]
        if not bulletins_list:
            raise UnavailableDataError(
                f"Unavailable rates for the requested range: {self.start_date!r} - {self.end_date!r}"
            )

        close_bulletins = [
            Bulletin(
                bulletin["dataHoraCotacao"],
                bulletin["cotacaoCompra"],
                bulletin["cotacaoVenda"],
                "close",
            )
            for bulletin in bulletins_list
        ]

        return HistoricalBulletin(self.start_date, self.end_date, close_bulletins)


class IntermediaryResource:
    path = settings.INTERMEDIARY_RESOURCE

    def __init__(self, date):
        self.date = date
        self.parsed_date = DateParser(date).parse()

    @property
    def params(self):
        return f"@moeda='USD'&@dataCotacao={self.parsed_date!r}&$format=json"

    def parse(self, raw_data):
        bulletin_list = raw_data["value"]
        if not bulletin_list:
            raise UnavailableDataError(
                f"Unavailable rates for the requested date:{self.date!r}"
            )

        bulletins = [
            Bulletin(
                report["dataHoraCotacao"],
                report["cotacaoCompra"],
                report["cotacaoVenda"],
                BulletinTypeParser(report["tipoBoletim"]).parse(),
            )
            for report in bulletin_list
        ]
        return IntermediaryBulletin(self.date, bulletins)
