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


def __search_stack__(search_stack, seen, depth_limit):
    """
    Searches a given dictionary of stacks and checks to see if Kevin Bacon
    exists. If Kevin Bacon is found, return True and the path to get to him,
    otherwise check if the tweet is a retweet from a verified user and add
    that user to the verified stack. If it is not a retweet nor a verified
    user, add any mentioned users to the stack. Repeat until Kevin Bacon is
    found or the stacks are empty.

    Args:
        search_stack: a dictionary containing a verified and unverified stack
                      containing the users to search through
        seen: a dictionary containing what twitter users have been seen and
              their predecessor
        depth_limit: a limit for how deep from the root to search

    Returns:
        True if Kevin Bacon has been found, and the path used to reach him

    """

    # stacks for tweets that exceed depth
    exceeds_depth_stack = {
        VERIFIED: deque(),
        UNVERIFIED: deque(),
    }

    while (search_stack[VERIFIED] or search_stack[UNVERIFIED]):
        # get the current user to search
        if search_stack[VERIFIED]:
            current_user, current_depth = search_stack[VERIFIED].pop()
            # check if depth is greater than the provided depth limit
            # for VERIFIED users
            if current_depth > depth_limit:
                current = (current_user, current_depth)
                exceeds_depth_stack[VERIFIED].append(current)
                continue
        else:
            current_user, current_depth = search_stack[UNVERIFIED].pop()
            # check if depth is greater than the provided depth limit
            # for UNVERIFIED users
            if current_depth > depth_limit:
                current = (current_user, current_depth)
                exceeds_depth_stack[UNVERIFIED].append(current)
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

                try:
                    # find verified retweeted user and add to stack
                    if tweet['retweeted_status']['user']['verified']:
                        retweeted_user =\
                                tweet['retweeted_status']['user']['screen_name']
                        if retweeted_user in seen:
                            continue

                        # generate path and add retweeted user to seen
                        path_to_mention =\
                                (current_user, tweet['id'], tweet[TWEET_TEXT])
                        seen[retweeted_user] = path_to_mention

                        search_stack[VERIFIED]\
                                .append((retweeted_user, current_depth + 1))
                except (TypeError, KeyError):
                    pass

                # search for mentions to add to stack
                for mention in tweet['entities']['user_mentions']:
                    mentioned_user = mention['screen_name']
                    if mentioned_user in seen:
                        continue

                    #generate path to mentioned user and add to seen
                    path_to_mention =\
                            (current_user, tweet['id'], tweet[TWEET_TEXT])
                    seen[mentioned_user] = path_to_mention

                    search_stack[UNVERIFIED]\
                            .append((mentioned_user, current_depth + 1))
        except TypeError:
            pass

    return False, [], exceeds_depth_stack, seen


def search_for_kevin_bacon(start):
    """
    Creates a dictionary of stacks starting with a given user and executes a
    search with a specified depth. If Kevin Bacon is found return the search
    results, else continue on with a new depth.

    Args:
        start: a twitter user to start searching for Kevin Bacon from

    Returns:
        The path to get to Kevin Bacon unless none is found

    """
    search_stack = {
        VERIFIED: deque(),
        UNVERIFIED: deque()
    }
    search_stack[UNVERIFIED].append((start, 0))
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

    # connection to Twitter API
    TWITTER.connect_to_twitter()

    # prints resutls of search
    for tweet in search_for_kevin_bacon(sys.argv[1]):
        user, tweet_id, tweet_text = tweet
        print "%s, %d, %s" % (user, tweet_id, tweet_text)


if __name__ == '__main__':
    main()
