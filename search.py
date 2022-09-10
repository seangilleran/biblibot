import json
import os
import uuid
from datetime import datetime
from urllib import parse as urlparse

import tweepy

query = "#BlackLivesMatter -is:retweet"
filename = "blacklivesmatter.json"

# Connect to Twitter and perform query.
bearer_token = os.getenv("BIBBOT_BEARER_TOKEN")
client = tweepy.Client(bearer_token)
response = client.search_recent_tweets(
    query,
    max_results=100,
    expansions="author_id,attachments.media_keys",
    tweet_fields="created_at,public_metrics,attachments",
    user_fields="username,name",
    media_fields="url,alt_text",
)

tweets = []
for tweet in response.data:

    # Find author info.
    author = next(u.data for u in response.includes["users"] if u.id == tweet.author_id)

    # Get attachment(s), if any.
    attachments = []
    try:
        for media_key in tweet.attachments["media_keys"]:
            attachments.append(
                next(
                    a.data
                    for a in response.includes["media"]
                    if a.media_key == media_key
                )
            )
    except TypeError:
        attachments = None
        pass

    # Compile.
    tweets.append(
        {
            "id": tweet.id,
            "author_id": tweet.author_id,
            "user": author,
            "created_at": tweet.created_at.isoformat(),
            "text": tweet.text,
            "attachments": attachments,
            "public_metrics": tweet.public_metrics,
            "url": f'https://twitter.com/{author["username"]}/status/{tweet.id}',
        }
    )

# Compile all tweets with query metadata.
data = {
    "id": f"{uuid.uuid4()}",
    "query": query,
    "url": f"https://twitter.com/search?q={urlparse.quote(query)}",
    "timestamp": datetime.now().isoformat(),
    "results": tweets,
}

# Save to file.
with open(filename, "w") as f:
    json.dump(data, f, indent=2)
