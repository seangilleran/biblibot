import os
import random

from pyzotero import zotero
from titlecase import titlecase
import tweepy

consumer_key = os.getenv("BIBBOT_CONSUMER_KEY")
consumer_secret = os.getenv("BIBBOT_CONSUMER_SECRET")
access_token = os.getenv("BIBBOT_ACCESS_TOKEN")
access_token_secret = os.getenv("BIBBOT_ACCESS_TOKEN_SECRET")
api = tweepy.API(
    tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
)

api_key = os.getenv("BIBBOT_API_KEY")
library_id = os.getenv("BIBBOT_LIBRARY_ID")
zot = zotero.Zotero(library_id, "group", api_key)

items = zot.items()
text = ""
while True:
    item = random.choice(items)

    type = item["data"]["itemType"]
    if type.startswith("book"):
        text = "📕"
    elif type.startswith("magazine"):
        text = "📔"
    elif type == "webpage":
        text = "🌐"
    else:
        text = "📄"

    try:
        creators = item["data"]["creators"]
        text += f" {creators[0]['firstName']} {creators[0]['lastName']}"
        if len(creators) == 2:
            text += f" and {creators[1]['firstName']} {creators[1]['lastName']}"
        elif len(creators) > 2:
            text += f" et al."
        text += ","
    except IndexError:
        pass

    title = titlecase(item["data"]["title"])
    text += f" “{title}”"

    date = item["data"].get("date", "")
    if date != "":
        text += f" ({date})"

    url = item["data"].get("url", "")
    if url == "":
        url = item["links"]["alternate"]["href"]
    text += f" {url}"

    #tags = [
    #    t["tag"]
    #    for t in item["data"]["tags"]
    #    if not t["tag"].startswith("*") and not "-" in t["tag"]
    #]
    #for tag in random.choices(tags, k=min([len(tags), 2])):
    #    text += f" #{tag.replace('_', '')}"

    if len(text) <= 280:
        break
    print("Skipping, tweet would be too long.")

api.update_status(text)
print("Done!")
