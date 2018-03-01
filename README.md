# Six Degrees of Bacon

This program called kb.py that takes as input the name of a twitter user as a command line argument and outputs a sequence of tweets, where the given user is the first tweeter, each succesive tweet is made by someone mentioned (i.e., via the @ symbol next to the user's name in the text of the tweet, e.g., @USER_MENTIONED) in the previous tweet, and the last tweet contains the phrase "Kevin Bacon" or "Kevin_Bacon," or "@KevinBacon" (case-insensitive). Specifically, the output should be formatted as (where USER1 is the given user):
USER1, TWEETID1, TWEET_TEXT1
USER2, TWEETID2, TWEET_TEXT2
USER3, TWEETID3, TWEET_TEXT3
...
USERK, TWEETIDK, TWEET_TEXTK
And TWEET_TEXTK contains the phrase "Kevin Bacon" or "Kevin_Bacon" or "@KevinBacon." Also, the same user can appear multiple times in the list, but the same tweet should not.
For example,

```
> python kb.py joe_user
joe_user, 22344912234, Slo day at work @ginny23412, @b0b5
ginny2312, 23449223412, Feeling tired. CU at gym @gfqqq
gfqqq, 93228333423, Hooray! a new Kevin bacon CD!!!
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

1. Unzip the compressed file and extract files
2. Open a command line tool and navigate to the location of the stored files
3. Run the following commands in the command line

Run using Iterative Deepening Search:
    `$ python2 kb.py <twitter_user>`

Run using Breadth-First Search:
    `$ python2 kb_bfs.py <twitter_user>`

Run using Itereative Deepening Search w/ Priority:
    `$ python2 kb_priority.py <twitter_user>`

Run using Breadth-First Search w/ Priority:
    `$ python2 kb_bfs_priority.py <twitter_user>`

"""Note: Feel free to use the provided credentials within the threaded_twitter_wrapper.py file"""

### Prerequisites

What things you need to install the software and how to install them

```
python2 - download and install python [here](https://www.python.org/downloads/)
Twython - `pip2 install Twython`
```

### Additional Notes
The agent will return `No connection to Kevin Bacon` if run on a user that does not exist.
Additionally, if a user is private the agent cannot query that user and will return `No Connection to Kevin Bacon`

### Coding Style

Coding style follows default pylint style and conforms to pep8 standards.

## Author

* **Chris Lim**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
