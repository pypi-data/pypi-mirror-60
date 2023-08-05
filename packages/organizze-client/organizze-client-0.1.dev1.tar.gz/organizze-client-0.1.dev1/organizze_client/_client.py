from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth


class OrganizzeClient:
    # Endpoints. They cannot start with slashes (/)
    # Users
    USERS = 'users/'
    USER = USERS + '{user_id}'
    # Accounts
    ACCOUNTS = 'accounts/'
    ACCOUNT = ACCOUNTS + '{account_id}'
    # Budgets
    BUDGETS = 'budgets/'
    BUDGET = BUDGETS + '{budget_id}'
    # Categories
    CATEGORIES = 'categories/'
    CATEGORY = CATEGORIES + '{category_id}'
    # Credit Cards
    CREDIT_CARDS = 'credit_cards/'
    CREDIT_CARD = CREDIT_CARDS + '{credit_card_id}/'
    CREDIT_CARD_INVOICES = CREDIT_CARD + 'invoices'
    CREDIT_CARD_INVOICE = CREDIT_CARD_INVOICES + '{invoice_id}/'
    CREDIT_CARD_INVOICE_PAYMENTS = CREDIT_CARD_INVOICE + 'payments'
    # Transactions
    TRANSACTIONS = 'transactions/'
    TRANSACTION = TRANSACTIONS + '{transaction_id}'

    # Configs
    BASE_URL = 'https://api.organizze.com.br/rest/v2/'
    CONTENT_TYPE = {'Content-Type': 'application/json; charset=utf-8'}

    def __init__(self, email, token):
        if not email:
            raise ValueError('Missing email.')
        if not token:
            raise ValueError('Missing auth token.')
        self.email = email
        self.token = token
        # self.def_ua = f'Organizze Python Client {__version__} ({self.email})'
        self.def_ua = f'Lucas ({self.email})'
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username=self.email, password=self.token)
        self.session.headers.update(self.CONTENT_TYPE)
        self.session.headers.update({'User-Agent': self.def_ua})

    def __str__(self):
        return f'{self.__class__.__name__}[{self.def_ua}]'

    def __repr__(self):
        return f'{self.__class__.__name__}(email={self.email}, token=***)'

    @classmethod
    def url_for(cls, endpoint, *args, **kwargs):
        return urljoin(cls.BASE_URL, endpoint.format(*args, **kwargs))

    def get_users(self):
        endpoint = self.url_for(self.USERS)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_user(self, user_id):
        endpoint = self.url_for(self.USER, user_id=user_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_accounts(self):
        endpoint = self.url_for(self.ACCOUNTS)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_account(self, account_id):
        endpoint = self.url_for(self.ACCOUNT, account_id=account_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_budgets(self):
        endpoint = self.url_for(self.BUDGETS)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_categories(self):
        endpoint = self.url_for(self.CATEGORIES)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_category(self, category_id):
        endpoint = self.url_for(self.CATEGORY, category_id=category_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_credit_cards(self):
        endpoint = self.url_for(self.CREDIT_CARDS)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_credit_card(self, credit_card_id):
        endpoint = self.url_for(self.CREDIT_CARD, credit_card_id=credit_card_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_credit_card_invoices(self, credit_card_id):
        endpoint = self.url_for(self.CREDIT_CARD_INVOICES, credit_card_id=credit_card_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_credit_card_invoice(self, credit_card_id, invoice_id):
        endpoint = self.url_for(self.CREDIT_CARD_INVOICE,
                                credit_card_id=credit_card_id,
                                invoice_id=invoice_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_transactions(self):
        endpoint = self.url_for(self.TRANSACTIONS)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])

    def get_transaction(self, transaction_id):
        endpoint = self.url_for(self.TRANSACTION, transaction_id=transaction_id)
        r = self.session.get(endpoint)
        if r.ok:
            return r.json()
        # Error
        raise Exception(r.json()['error'])
