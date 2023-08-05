from baseapi import Client


class CrimeClient(Client):
    DEFAULT_URL = 'https://crime.structrs.com'
    DEFAULT_APIS = (
        'pycrime.apis.statistics',
    )
