from tgtg import TgtgClient


class TooGoodToGoWrapper:
    client = None
    credentials = None

    def __init__(self, email=None, tokens=None):
        if email is not None:
            self.authenticate_email(email)
        if tokens is not None:
            self.authenticate_tokens(tokens['access_token'], tokens['refresh_token'], tokens['user_id'])

    def authenticate_email(self, email):
        self.client = TgtgClient(email=email)
        credentials = self.client.get_credentials()
        self.credentials = credentials

    def authenticate_tokens(self, access_token, refresh_token, user_id):
        self.client = TgtgClient(access_token=access_token, refresh_token=refresh_token, user_id=user_id)

    def get_favourites(self):
        items = self.client.get_items()
        return items

    def filter_items_available(self, items):
        return items
