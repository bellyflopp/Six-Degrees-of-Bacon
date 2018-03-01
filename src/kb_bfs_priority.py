"""
Six Degrees of Kevin Bacon
Author: Chris Lim
Date: 2/28/18

This intelligent agent determines how far a given individual is from following
Kevin Bacon on Twitter. The agent is limited to using the search() function
from the Twython API.
"""


import sys
from collections import deque
from threaded_twitter_wrapper import TwitterConnection


# open connection to Twitter API
TWITTER = TwitterConnection()

KEVIN_BACON = 'Kevin Bacon'
TWEET_TEXT = 'full_text'
VERIFIED = 'verified'
UNVERIFIED = 'unverified'

# "The average Bacon number is 2.955. Using one of the actors
# with the highest known finite Bacon number (7), William Rufus Shafter as
# the centre of the acting universe instead of Bacon, we can find two
# actors with a Rufus Shafter number of 15." - Wikipedia
SHAFTER_LIMIT = 15


def __contains_kevin_bacon__(tweet):
    """
    Check if a tweet contains Kevin Bacon, Kevin_Bacon, or KevinBacon (case
    insensitive).

    Args:
        tweet: tweet text

    Return:
        True if the tweet text contains a form of "Kevin Bacon"

    """
    tweet_text = tweet.lower()
    if "kevin bacon" in tweet_text:
        return True
    if "kevin_bacon" in tweet_text:
        return True
    if "kevinbacon" in tweet_text:
        return True
    return False


def __generate_path__(seen, user):
    """
    Generates the path to a user.

    Args:
        seen: dictionary of seen users and their predecessors
        user: user generate the path from

    Return:
        A list of the path from the user to the parent node

    """
    path_to_bacon = []
    while user:
        predecessor = seen[user]
        if predecessor:
            path_to_bacon.append(predecessor)
            user = predecessor[0]
        else:
            break
    return reversed(path_to_bacon)


def __search_queue__(search_queue, seen):
    """
    Searches a dictionary of queues and checks to see if Kevin Bacon exists.
    If Kevin Bacon is found, return True and the path to get to him, otherwise
    check if the tweet is a retweet of a verified user and add that user to the
    verified stack. If not, add any mentioned users to the queue. Repeat until
    Kevin Bacon is found or the queues are empty.

    Args:
        search_queue: a dictionary of queues containing the users to search
                      through
        seen: a dictionary containing what twitter users have been seen and
              their predecessor

    Returns:
        True if Kevin Bacon has been found, and the path used to reach him

    """

    while search_queue[VERIFIED] or search_queue[UNVERIFIED]:
        # get the current user to search
        if search_queue[VERIFIED]:
            current_user = search_queue[VERIFIED].popleft()
        else:
            current_user = search_queue[UNVERIFIED].popleft()

        # queries twitter
        query = "from:%s" % current_user
        tweets = TWITTER.search_twitter(query)

        # search through current users tweets
        try:
            for tweet in tweets['statuses']:
                if __contains_kevin_bacon__(tweet[TWEET_TEXT]):
                    # mark Kevin Bacon as seen and generate path to him
                    seen[KEVIN_BACON] =\
                            (current_user, tweet['id'], tweet[TWEET_TEXT])
                    path_to_kevin_bacon = __generate_path__(seen, KEVIN_BACON)
                    return True, path_to_kevin_bacon, search_queue, seen

                try:
                    # find verified retweeted user and add to queue
                    if tweet['retweeted_status']['user']['verified']:
                        retweeted_user =\
                            tweet['retweeted_status']['user']['screen_name']
                        if retweeted_user in seen:
                            continue

                        # generate path and add retweeted user to seen
                        path_to_mention =\
                            (current_user, tweet['id'], tweet[TWEET_TEXT])
                        seen[retweeted_user] = path_to_mention

                        search_queue[VERIFIED].append(retweeted_user)
                except (TypeError, KeyError):
                    pass

                # search for mentions to add to queue
                for mention in tweet['entities']['user_mentions']:
                    mentioned_user = mention['screen_name']
                    if mentioned_user in seen:
                        continue

                    # generate path to mentioned user and add to seen
                    path_to_mention =\
                        (current_user, tweet['id'], tweet[TWEET_TEXT])
                    seen[mentioned_user] = path_to_mention

                    search_queue[UNVERIFIED].append(mentioned_user)
        except TypeError:
            pass

    return False, [], search_queue, seen


def search_for_kevin_bacon(start):
    """
    Creates a dictionary of queues starting with a given user and executes a
    search. If Kevin Bacon is found return the search results.

    Args:
        start: a twitter user to start searching for Kevin Bacon from

    Returns:
        The path to get to Kevin Bacon unless none is found

    """
    search_queue = {
        VERIFIED: deque(),
        UNVERIFIED: deque()
    }
    search_queue[UNVERIFIED].append(start)
    seen = {start: None}

    found, search_results, search_queue, seen = \
        __search_queue__(search_queue, seen)
    if found:
        return search_results

    print 'No connection to Kevin Bacon'
    sys.exit(0)


def main():
    """ main function to execute to run agent """
    if len(sys.argv) != 2:
        sys.exit("Invalid Argument Exception\n" + \
                 "Usage: python2 kb.py <twitter_user>")

    # connection to Twitter API
    TWITTER.connect_to_twitter()

    # prints resutls of search
    for tweet in search_for_kevin_bacon(sys.argv[1]):
        user, tweet_id, tweet_text = tweet
        print "%s, %d, %s" % (user, tweet_id, tweet_text)


if __name__ == '__main__':
    main()
