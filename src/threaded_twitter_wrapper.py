"""
Author: Chris Lim
Date: 2/27/18

This module acts as a wrapper for the Twython module. It allows the user to
exceed the standard rate limit of the search call to the Twitter API by
rotating accounts when a specified account exceeds it's limit. If all accounts
timeout, it sleeps an application for 10 minutes before resuming.
"""

from time import sleep
from multiprocessing import Process, Manager
from twython import Twython, TwythonRateLimitError, TwythonError


# enter your keys, and tokens obtained from your twitter app
MINUTE = 60
RATE_LIMITE_TIMER = 15

# enter your keys, and tokens obtained from your twitter app
ACCOUNTS = []

def __account_refresher__(active_accounts, current_account):
    """
    Function that sleeps the specific process that represents a specific
    accounts rate limit reset time.

    Args:
        active_accounts: a list of active accounts to append to once sleep is
                         complete
        current_account: the account to sleep

    """
    sleep(RATE_LIMITE_TIMER * MINUTE)
    active_accounts.append(current_account)


class TwitterConnection(object):
    """
    Acts as a wrapper class to the Twython object and Twitter API. Maintains
    a counter representing which account is being used to make the API calls.

    Attribute(s):
        connection (Twython): Twython object that exists as the current
                              connection
        manager (Manger): Manger object that stores and manages active and
                          inactive accounts
    """
    def __init__(self):
        self.connection = None

        # handles processes linked to each account
        self.manager = Manager()
        self.current_account = None
        self.active_accounts = self.manager.list()

        for account in ACCOUNTS:
            account_object = Account(*account)
            self.active_accounts.append(account_object)


    def connect_to_twitter(self):
        """
        Rotates which account is used to connect to the Twitter API. Then
        establishes a connection to Twitter using twython.
        """
        if self.active_accounts:
            self.current_account = self.active_accounts.pop()
            key, secret, _, _ =\
                    self.current_account.get_credentials()
            oauth2_token =\
                    Twython(key, secret, oauth_version=2).obtain_access_token()
            self.connection = Twython(key, access_token=oauth2_token)
        else:
            while len(self.active_accounts) < 1:
                sleep(1)
            self.connect_to_twitter()


    def search_twitter(self, query):
        """
        Makes a search call to Twitter based on a give query. If the rate limit
        is exceeded by the call, the current account is slept for 15 minutes
        and a new connection is made.

        Args:
            query: the query made to Twitter

        Returns:
            The results of the search call made to Twitter

        """
        try:
            # Twitter search query
            return self.connection.\
                    search(q=query, count=100, tweet_mode='extended')
        except TwythonRateLimitError:
            # begin process of sleeping account
            account_sleep_process = \
                Process(target=__account_refresher__,
                        args=(self.active_accounts, self.current_account))
            account_sleep_process.daemon = True
            account_sleep_process.start()

            # make new connection and retry
            self.connect_to_twitter()
            return self.search_twitter(query)
        except TwythonError:
            return []


class Account(object):
    """
    Data class that stores a Twitter app credentials.

    Attribute(s):
        key: Twitter API key
        secret: Twitter API secret
        token: Twitter API token
        token_secret: Twitter API token secret
    """
    def __init__(self, key, secret, token, token_secret):
        self.key = key
        self.secret = secret
        self.token = token
        self.token_secret = token_secret


    def get_name(self):
        """
        Returns the account Twitter API key

        Returns:
            Twitter API key
        """
        return self.key


    def get_credentials(self):
        """
        Returns the data in the account

        Returns:
            Twitter API key, secret, toke, token_secret in account
        """
        return self.key, self.secret, self.token, self.token_secret
