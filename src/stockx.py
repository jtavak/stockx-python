import requests
from datetime import date
from urllib.parse import quote_plus, urljoin


def _get_fields(item, fields):

    return {field: item[field] for field in fields}


class StockXAPI:

    def __init__(self, user_agent=None):

        self.API_BASE = 'https://stockx.com/api/'

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0' if not user_agent else user_agent
        self.headers = {
            'user-agent': user_agent,
            'sec-fetch-dest': 'none',
            'accept': '*/*',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'accept-language': 'en-US'
        }

    def _get(self, resource, **kwargs):

        url = urljoin(self.API_BASE, resource)
        response = requests.get(url, **kwargs)
        return response

    # searches for products related to 'query'
    def search_products(self, query, page=0, fields=('title', 'id', 'brand', 'retailPrice', 'urlKey', 'market')):

        url = 'browse'
        params = {
            '_search': quote_plus(query),
            'page': page
        }

        response = self._get(url, headers=self.headers, params=params).json()

        return [_get_fields(product, fields) for product in response['Products']]

    # gets product info based on product ID or urlKey
    def get_product(self, pid, fields=('title', 'id', 'brand', 'retailPrice', 'urlKey', 'market')):

        url = 'products/{}'.format(pid)
        params = {
            'includes': 'market'
        }

        response = self._get(url, headers=self.headers, params=params).json()

        return _get_fields(response['Product'], fields)

    # returns pricing data from 'start_date' to 'end_date' over 'interval' samples as a dict
    def get_past_prices(self, pid, start_date='all', end_date=date.today(), intervals=20):
        url = 'products/{}/chart'.format(pid)
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'intervals': intervals
        }

        response = self._get(url, headers=self.headers, params=params).json()

        pricing_data = {
            'time_ranges': response['xAxis']['categories'],
            'prices': response['series'][0]['data']
        }
        return pricing_data

    def _get_activity(self, pid, state, extra_params=None):

        if extra_params is None:
            extra_params = {}

        url = 'products/{}/activity'.format(pid)
        params = {
            'state': state
        } | extra_params

        response = self._get(url, headers=self.headers, params=params).json()

        return response

    # gets past sales for product with urlKey or ID = 'pid'
    def get_sales(self, pid, sort='createdAt', order='DESC'):

        extra_params = {
            'sort': sort,
            'order': order
        }

        return self._get_activity(pid, 480, extra_params)

    # gets current asks for product
    def get_asks(self, pid):

        return self._get_activity(pid, 400)

    # gets current bids for product
    def get_bids(self, pid):

        return self._get_activity(pid, 300)
