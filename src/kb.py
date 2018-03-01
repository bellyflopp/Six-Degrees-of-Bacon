"""
Six Degrees of Kevin Bacon
Author: Chris Lim
Date: 2/28/18

This intelligent agent determines how far a given individual is from following
Kevin Bacon on Twitter. The agent is limited to using the search() function
from the Twython API.
"""


import sys
import time
from collections import deque
from threaded_twitter_wrapper import TwitterConnection


# open connection to Twitter API
TWITTER = TwitterConnection()

KEVIN_BACON = 'Kevin Bacon'
TWEET_TEXT = 'full_text'

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


def __search_stack__(search_stack, seen, depth_limit):
    """
    Searches a given stack and checks to see if Kevin Bacon exists. If Kevin
    Bacon is found, return True and the path to get to him, otherwise add any
    mentioned users to the stack. Repeat until Kevin Bacon is found or the
    stack is empty.

    Args:
        search_stack: a stack containing the users to search through
        seen: a dictionary containing what twitter users have been seen and
              their predecessor
        depth_limit: a limit for how deep from the root to search

    Returns:
        True if Kevin Bacon has been found, and the path used to reach him

    """

    # stack for tweets that exceed depth
    exceeds_depth_stack = deque()

    while search_stack:
        # get current user to search
        current_user, current_depth = search_stack.pop()

        # check if depth is greater than the provided depth limit
        if current_depth > depth_limit:
            current = (current_user, current_depth)
            exceeds_depth_stack.append(current)
            continue

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
                    return True, path_to_kevin_bacon, search_stack, seen

                # search for mentions to add to stack
                for mention in tweet['entities']['user_mentions']:
                    mentioned_user = mention['screen_name']
                    if mentioned_user in seen:
                        continue

                    # generate path to mentioned user and add to seen
                    path_to_mention =\
                            (current_user, tweet['id'], tweet[TWEET_TEXT])
                    seen[mentioned_user] = path_to_mention

                    search_stack.append((mentioned_user, current_depth + 1))
        except TypeError:
            pass

    return False, [], exceeds_depth_stack, seen


def search_for_kevin_bacon(start):
    """
    Creates a stack starting with a given user and executes a search with a
    specified depth. If Kevin Bacon is found return the search results, else
    continue on with a new depth.

    Args:
        start: a twitter user to start searching for Kevin Bacon from

    Returns:
        The path to get to Kevin Bacon unless none is found

    """
    search_stack = deque()
    search_stack.append((start, 0))
    seen = {start: None}
    depth_limit = 3

    while depth_limit <= SHAFTER_LIMIT:
        found, search_results, search_stack, seen = \
            __search_stack__(search_stack, seen, depth_limit)
        if found:
            return search_results

        # if Kevin Bacon is not found increase depth
        depth_limit += 2

    print 'No connection to Kevin Bacon'
    sys.exit(0)


def main():
    """ main function to execute to run agent """
    if len(sys.argv) != 2:
        sys.exit("Invalid Argument Exception\n" + \
                 "Usage: python2 kb.py <twitter_user>")

    start = time.time()

    # connection to Twitter API
    TWITTER.connect_to_twitter()

    # prints resutls of search
    for tweet in search_for_kevin_bacon(sys.argv[1]):
        user, tweet_id, tweet_text = tweet
        print "%s, %d, %s" % (user, tweet_id, tweet_text)

    print "--- %s seconds ---" % (time.time() - start)

if __name__ == '__main__':
    main()
