from pyptax.client import Ptax
from pyptax.models import Bulletin, HistoricalBulletin
from pyptax.resources import CloseResource, HistoricalResource, IntermediaryResource


def close(date: str) -> Bulletin:
    """
    Retrieve closing Ptax rates on a certain date.

    Parameters
    ----------
    date
        Year, month and day of the date to be searched. Format - "YYYY-MM-DD"

    Returns
    -------
    Bulletin
        A Bulletin object with datetime, bid and ask attributes

    Raises
    ------
    DateFormatError
        If fails to parse the informed date

    Examples
    --------
    >>> bulletin = close("2020-01-20")
    >>> bulletin
    Bulletin(
        datetime="2020-01-20 13:09:02.871",
        bid=4.1823,
        sk=4.1829,
        bulletin_type="close"
    )
    >>> bulletin.bid
    4.1823
    >>> bulletin.ask
    4.1829
    >>> bulletin.as_dict
    {
        "datetime": "2020-01-20 13:09:02.871",
        "bid": 4.1823,
        "ask": 4.1829,
        "bulletin_type": "close"
    }
    """
    resource = CloseResource(date)
    return Ptax(resource).response()


def historical(start_date: str, end_date: str) -> HistoricalBulletin:
    """
    Retrieve historical closing Ptax rates for the requested time period.

    Parameters
    ----------
    start_date
        Beginning of the time period to be searched. Format - 'YYYY-MM-DD'
    end_date
        End of the time period to be searched. Format - 'YYYY-MM-DD'

    Returns
    -------
    HistoricalBulletin
        A HistoricalBulletin object with start_date, end_date and bulletins with a list
        of Bulletins.

    Raises
    ------
    DateFormatError
        If fails to parse the informed date
    ClientError
        If Ptax Service response returns an error
    UnavailableDataError
        If receives an empty list from Ptax Service

    Examples
    --------
    >>> historical_bulletin = historical("2020-01-02", "2020-01-03")
    >>> historical_bulletin
    HistoricalBulletin(
        start_date="2020-01-02",
        end_date="2020-01-04",
        bulletins=[
            Bulletin(
                datetime="2020-01-02 13:11:10.762",
                bid=4.0207,
                ask=4.0213,
                bulletin_type="close"
            ),
            Bulletin(
                datetime="2020-01-03 13:06:22.606",
                bid=4.0516,
                ask=4.0522,
                bulletin_type="close"
            ),
        ],
    )
    >>> historical_bulletin.as_dict
    {
        "start_date": "2020-01-02",
        "end_date": "2020-01-04",
        "bulletins": [
            {
                "datetime": "2020-01-02 13:11:10.762",
                "bid": 4.0207,
                "ask": 4.0213,
                "bulletin_type": "close"
            },
            {
                "datetime": "2020-01-03 13:06:22.606",
                "bid": 4.0516,
                "ask": 4.0522,
                "bulletin_type": "close"
            },
        ],
    }
    """
    resource = HistoricalResource(start_date, end_date)
    return Ptax(resource).response()


def intermediary(date: str):
    """
    Retrieve intermediary bulletins of Ptax rates for the requested date.

    Parameters
    ----------
    date
        Date to be searched. Format - 'YYYY-MM-DD'

    Returns
    -------
    IntermediaryBulletin
        A IntermediaryBulletin object with date and bulletins with a list of Bulletins.

    Raises
    ------
    DateFormatError
        If fails to parse the informed date
    ClientError
        If Ptax Service response returns an error
    UnavailableDataError
        If receives an empty list from Ptax Service

    Examples
    --------
    >>> intermediary("2020-01-02")
    IntermediaryBulletin(
        date='2020-01-02',
        bulletins=[
            Bulletin(
                datetime='2020-01-02 10:08:18.114',
                bid=4.0101,
                ask=4.0107,
                bulletin_type='open'
            ),
            Bulletin(
                datetime='2020-01-02 11:03:40.704',
                bid=4.0118,
                ask=4.0124,
                bulletin_type='intermediary'
            ),
            Bulletin(
                datetime='2020-01-02 12:10:55.168',
                bid=4.0302,
                ask=4.0308,
                bulletin_type='intermediary'
            ),
            Bulletin(
                datetime='2020-01-02 13:11:10.756',
                bid=4.0305,
                ask=4.0311,
                bulletin_type='intermediary'
            ),
            Bulletin(
                datetime='2020-01-02 13:11:10.762',
                bid=4.0207,
                ask=4.0213,
                bulletin_type='close'
            )
        ]
    )
    """
    resource = IntermediaryResource(date)
    return Ptax(resource).response()
