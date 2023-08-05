from .client import Ptax
from .resources import CloseResource
from pyptax.models import CloseReport


def close(date: str) -> CloseReport:
    """
    Retrieve closing Ptax rates on a certain date.

    Parameters
    ----------
    date
        Year, month and day of the date to be searched. Format - "YYYY-MM-DD"

    Returns
    -------
    object
        A CloseReport object with datetime, bid and ask attributes

    Raises
    ------
    DateFormatException
        If fails to parse the informed date

    Examples
    --------
    >>> close_report = close("2020-01-20")
    >>> close_report
    CloseReport(datetime=2020-01-20 13:09:02.871, bid=4.1823, ask=4.1829)
    >>> print(close_report)
    2020-01-20 13:09:02.871 - bid: 4.1823 - ask: 4.1829
    >>> close_report.bid
    4.1823
    >>> close_report.ask
    4.1829
    >>> close_report.as_dict
    {'datetime': '2020-01-20 13:09:02.871', 'bid': '4.1823', 'ask': '4.1829'}

    """
    resource = CloseResource(date)
    return Ptax(resource).response()
