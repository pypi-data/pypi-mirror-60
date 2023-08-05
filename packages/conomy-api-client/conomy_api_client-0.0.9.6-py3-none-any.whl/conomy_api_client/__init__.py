from collections import namedtuple
import requests
import json
from json import JSONDecodeError
import pickle


class DataClient(object):
    MAIN_API_URL = 'http://data.conomy.ru/api/'
    PUB_DATE_FORMAT = '%d.%m.%Y %H:%M'
    choices = namedtuple('Types', 'FACT NEWS ACCS C_NEWS C_FACT')
    publication_types = choices('fact', 'news', 'accs', 'c_news', 'c_fact')

    ENDPOINTS = {
        'issuers': 'stock/issuer/',
        'publications': {'/':        'publication/',
                         'counts':   'publication/counts/',
                         'new':      'publication/new/',
                         'latest':   'publication/latest/',
                         'archived': 'publication/archived/',
                         'fact':     'publication/fact/',
                         'accs':     'publication/accs/',
                         'news':     'publication/news/',
                         'c_news':   'publication/conomy-news/',  # 'c' in key means 'Conomy'
                         'c_fact':   'publication/conomy-facts/', # ...
                         },
        'dividends': {'by-ticker':   'stock/dividends-by-ticker/',},
        'bonds':     {'/':           'stock/bond/',
                      'add_rates':   'stock/bond/add-ratings/'}
    }

    mocked_issuer = {'uuid': '43f44d20-4e03-4a50-938d-fe2b5aef0242',
                     'conomy_issuer_id': 3043,
                     'edisclosure_id': 3043,
                     'name': 'ПАО "Сбербанк"',
                     'url': '/api/stock/issuer/43f44d20-4e03-4a50-938d-fe2b5aef0242/'}

    def __init__(self, token: str, api_host: str = None):
        self.api_url = api_host or self.MAIN_API_URL
        self.headers = {'Authorization': 'Token ' + token,
                        'Content-Type': 'application/json; charset=utf-8',
                        }

    def send_resp(self, method: str, endpoint_url: str, **kwargs):
        method = method.lower()
        if hasattr(requests, method):
            resp = getattr(requests, method)(url=self.api_url + endpoint_url,
                                             headers=self.headers,
                                             **kwargs
                                             )
            try:
                return resp.json()
            except JSONDecodeError:
                return json.dumps({"code": resp.status_code,
                                   "mess": resp if isinstance(resp, str) else None})
    """
    Issuers
    """

    def get_issuers(self, mock=False):
        if mock:
            return [self.mocked_issuer]
        return self.send_resp(method='GET', endpoint_url=self.ENDPOINTS['issuers'])

    def get_issuer(self, uuid, mock=False):
        if mock:
            return self.mocked_issuer
        return self.send_resp(method='GET', endpoint_url=self.ENDPOINTS['issuers'] + uuid + '/')

    """
    Publications
    """

    def count_new_pubs(self):
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['publications']['counts'])

    def get_publications(self, type_=None, mock=False, page=1):
        """
        Get publications if parameter 'type_' is set then return Publications only selected type
        else it return all publications
        """
        if mock:
            return self.load_pubs_from_pickle(type_)
        endpoint_with_type = self.ENDPOINTS['publications'].get(type_)
        endpoint_url = endpoint_with_type if endpoint_with_type else self.ENDPOINTS['publications']['/']
        endpoint_url += f"?page={page}"
        resp = self.send_resp(method='GET', endpoint_url=endpoint_url)
        return resp

    def get_new_publications(self, page=1):
        return self.send_resp(method='GET', endpoint_url=self.ENDPOINTS['publications']['new'] + f"?page={page}")

    def get_archived_publications(self, page=1):
        return self.send_resp(method='GET', endpoint_url=self.ENDPOINTS['publications']['archived']+ f"?page={page}")

    def get_publication(self, pk):
        """
        Get one publication
        """
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['publications']['/'] + str(pk),
                              )

    def get_latest_publication(self, issuer_uuid):
        """
        Get last publication about issuer by `edisclosure_id`
        """
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['publications']['latest'] + str(issuer_uuid),
                              )

    def get_latest_news(self, source):
        """
        Get last publication about issuer by `edisclosure_id`
        """
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['publications']['news'] + source + "/latest",
                              )

    def archived_publication(self, pk):
        data = {"archived": True}
        return self.send_resp(method='PATCH',
                              endpoint_url=self.ENDPOINTS['publications']['/'] + str(pk),
                              data=json.dumps(data))

    def extract_publication(self, pk):
        data = {"archived": False}
        return self.send_resp(method='PATCH',
                              endpoint_url=self.ENDPOINTS['publications']['/'] + str(pk),
                              data=json.dumps(data))

    def publication_to_conomy(self, pk):
        data = {"conomy_api_client": True}
        return self.send_resp(method='PATCH',
                              endpoint_url=self.ENDPOINTS['publications']['/'] + str(pk),
                              data=json.dumps(data))

    def publication_from_conomy(self, pk):
        data = {"conomy_api_client": False}
        return self.send_resp(method='PATCH',
                              endpoint_url=self.ENDPOINTS['publications']['/'] + str(pk),
                              data=json.dumps(data))

    def save_pubs_to_pickle(self, pubs, type_=None):
        """
        Function to save Pubs dataset for mocking Data requests
        """
        type_ = type_ or self.publication_types.C_FACT
        filename = type_ + '_mocking_pubs.pickle'
        with open(filename, 'wb') as handle:
            pickle.dump(pubs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_pubs_from_pickle(self, type_=None):
        type_ = type_ or self.publication_types.C_FACT
        filename = type_ + '_mocking_pubs.pickle'
        with open(filename, 'rb') as handle:
            return pickle.load(handle)

    def create_publication(self, **kwargs) -> dict:
        # def create_publication(self, pub_date: str, issuer: int, title: str, text: str, author: str, url: str) -> dict:
        """
        To use this method user must have the admin (staff) permissions
        :param pub_date: Publication date in format '%d.%m.%Y %H:%M'
        :param issuer:  ID of issuer on 'e-disclosure.ru' or 0
        :param title: Title of publication
        :param text:    Text of publication
        :param author: Author of publication
        :param url: Url with original text of publication
        :return:    json response
        """
        # data = {k:v for k, v in locals() if k != 'self'}
        return self.send_resp(method='POST',
                              endpoint_url=self.ENDPOINTS['publications']['/'],
                              data=json.dumps(kwargs))

    """
    Dividends
    """

    def divds_by_tic(self, tick=None):
        if tick:
            return self.send_resp(method='GET',
                                  endpoint_url=self.ENDPOINTS['dividends']['by-ticker'] + tick,
                                  )
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['dividends']['by-ticker'])

    """
    Bonds
    """

    def update_bond_data(self, data: dict=None):
        data = data or {"ratings": [],
                        "inn": 0}
        return self.send_resp(method='PATCH',
                              endpoint_url=self.ENDPOINTS['bonds']['add_rates'],
                              data=json.dumps(data))

    def get_bond(self, symbol):
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['bonds']['/'] + str(symbol) + '/',
                              )

    def get_bonds(self, offset=0, limit=100):
        return self.send_resp(method='GET',
                              endpoint_url=self.ENDPOINTS['bonds']['/'] + f'?limit={limit}&offset={offset}',
                              )



dc = DataClient('979617efb82e966b8e30942e347a8d9ec2ddb889',
                api_host='http://127.0.0.1:8000/api/')

data = {'inn': '7740000076',
        'ratings': [{'bond_id': 'RU000A0JR4J2',
                     'bond_rate': 'ruAA',
                     'rate_date': '27.12.2017'},
                    {'bond_id': 'RU000A0JR4J2',
                     'bond_rate': 'ruAA',
                     'rate_date': '27.12.2017'},
                    {'bond_id': 'RU000A0JR4J2',
                     'bond_rate': 'ruAA',
                     'rate_date': '27.12.2017'},]
        }
