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


def add_or_update_user(name):
    """
    Add or update a user and their Tweets.
    Throw an error if user doesn't exist or is private.
    """
    try:
        twitter_user = TWITTER.get_user(name)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=name))
        DB.session.add(db_user)
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        for tweet in tweets:
            emb = BASILICA.embed_sentence(tweet.full_text, model='twitter')
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500],
                             embedding=emb)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Encountered error while processing @{name}: {e}')
        raise e
    else:
        DB.session.commit()
