SERVICE_URL = "https://olinda.bcb.gov.br/olinda/service/PTAX/version/v1/odata/"

CLOSE_RESOURCE = "DollarRateDate(dataCotacao=@dataCotacao)"

HISTORICAL_RESOURCE = (
    "DollarRatePeriod(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
)

INTERMEDIARY_RESOURCE = "ExchangeRateDate(moeda=@moeda,dataCotacao=@dataCotacao)"
