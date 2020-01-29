"""Retrieve Tweets, embeddings, and persist in the database."""
import basilica
from os import getenv
import tweepy
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(getenv('TWITTER_CONSUMER_KEY'),
                                   getenv('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(getenv('TWITTER_ACCESS_TOKEN'),
                              getenv('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(getenv('BASILICA_KEY'))


def add_user_to_db(username):
    """Adds a Twitter user and their latest Tweets to the database."""
    twitter_user = TWITTER.get_user(username)
    tweets = get_tweets(twitter_user)
    db_user = User(id=twitter_user.id, name=twitter_user.screen_name,
                   newest_tweet_id=tweets[0].id)
    db_tweets = add_tweets_to_db(tweets)
    for tweet in db_tweets:
        db_user.tweets.append(tweet)
    DB.session.add(db_user)
    DB.session.commit()


def get_tweets(twitter_user, count=200, exclude_replies=True,
               include_rts=False, tweet_mode='extended'):
    """Gets a user's latest Tweets."""
    return twitter_user.timeline(count=count,
                                 exclude_replies=exclude_replies,
                                 include_rts=include_rts,
                                 tweet_mode=tweet_mode)


def get_embeddings(tweets):
    """Gets embeddings from Basilica for a list of Tweets."""
    return [BASILICA.embed_sentence(tweet.full_text, model='twitter')
            for tweet in tweets]


def add_tweets_to_db(tweets):
    """Add a list of Tweets and their embeddings to the database."""
    embeddings = get_embeddings(tweets)
    db_tweets = []
    for tweet, embedding in zip(tweets, embeddings):
        db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500],
                         embedding=embedding)
        DB.session.add(db_tweet)
        db_tweets.append(db_tweet)
    return db_tweets
