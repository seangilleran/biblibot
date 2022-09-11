import json
import os
import uuid
from datetime import datetime
from urllib import parse as urlparse

import tweepy


query = "#BlackLivesMatter -is:retweet"
max_results = 15
bearer_token = "AAAAAAAAAAAAAAAAAAAAANqJfwEAAAAAMy8ZIiHw0wkOAc%2FbZuYBKeuWGls%3DnPPUp0vDf4T54nxc1Ln2vuZYGS6CSKmDrvBTXdqlTCh3ozukBk"

query_id = f"{uuid.uuid4()}"
query_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

client = tweepy.Client(bearer_token)
response = client.search_recent_tweets(
    query,
    max_results=max_results,
    expansions="author_id,attachments.media_keys",
    tweet_fields="created_at,public_metrics,attachments",
    user_fields="username,name",
    media_fields="url,alt_text",
)

tweets = []
for tweet_data in response.data:

    # Get Tweet.
    tweet = {
        "id": tweet_data.id,
        "created_at": tweet_data.created_at.isoformat(),
        "user": next(
            u.data for u in response.includes["users"] if u.id == tweet_data.author_id
        ),
        "text": tweet_data.text,
    }

    # Get attachment(s), if any.
    attachments = []
    try:
        for media_key in tweet_data.attachments["media_keys"]:
            attachments.append(
                next(
                    a.data
                    for a in response.includes["media"]
                    if a.media_key == media_key
                )
            )
        tweet["attachments"] = attachments
    except TypeError:
        pass

    # Get metrics & URL.
    tweet.update(
        {
            "public_metrics": tweet_data.public_metrics,
            "url": f'https://twitter.com/{tweet["user"]["username"]}/status/{tweet["id"]}',
        }
    )

    tweets.append(tweet)

# Compile all tweets with query metadata.
data = {
    "id": f"{query_id}",
    "timestamp": query_timestamp,
    "query": query,
    "url": f"https://twitter.com/search?q={urlparse.quote(query)}",
    "tweets": tweets,
}

# Save to file.
filename = f"{query_timestamp}_{query_id}.json"
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print("Done!")
