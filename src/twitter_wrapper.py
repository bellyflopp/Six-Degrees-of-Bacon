"""
Author: Chris Lim
Date: 2/27/18

This module acts as a wrapper for the Twython module. It allows the user to
exceed the standard rate limit of the search call to the Twitter API by
rotating accounts when a specified account exceeds it's limit. If all accounts
timeout, it sleeps an application for 10 minutes before resuming.
"""

import datetime

from time import sleep
from twython import Twython, TwythonRateLimitError, TwythonError

# enter your keys, and tokens obtained from your twitter app
ACCOUNTS = []


class TwitterConnection(object):
    """
    Acts as a wrapper class to the Twython object and Twitter API. Maintains
    a counter representing which account is being used to make the API calls.

    Attribute(s):
        trace (bool): Represents whether trace print statements should be made
        count (int): The current account being used
        connection (obj): Twython object that exists as the current connection
        connected (bool): Represents whether a connection is present
    """

    def __init__(self, trace=False):
        self.count = 0
        self.connection = None
        self.connected = False


    @property
    def get_connection(self):
        """(obj) Returns the current connection made to Twitter."""
        if self.connected:
            return self.connection
        raise TwythonError("not connected to Twitter")


    @property
    def get_account(self):
        """(int) Returns the current account being used"""
        return self.count


    def connect_to_twitter(self):
        """
        Rotates which account is used to connect to the Twitter API. Then
        establishes a connection to Twitter using twython.
        """
        if self.count >= len(ACCOUNTS):
            self.count = 0
        key, secret, token, token_secret = ACCOUNTS[self.count]
        self.connection = Twython(key, secret, token, token_secret)
        self.connected = True
        self.count += 1


    def search_twitter(self, query):
        """
        Makes a search call to Twitter based on a give query. If the rate limit
        is exceeded by the call, a new connection is established and the search
        call is re-made. If all accounts fail the app sleeps for 10 minutes,
        then the process is restarted.

        Args:
            query: the query made to Twitter

        Returns:
            The results of the search call made to Twitter

        """
        for _ in range(len(ACCOUNTS)):
            try:
                return self.connection.search(q=query, count=100, tweet_mode='extended')
            except TwythonRateLimitError:
                self.connect_to_twitter()
                self.connected = False
                continue
            except TwythonError:
                return []
            self.connected = True
            break
        if not self.connected:            
            sleep(10*60)
            self.connect_to_twitter()
            self.search_twitter(query)
