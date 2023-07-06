import praw
import os
import json
from dotenv import load_dotenv
import time

json_obj = {}
subreddits = []

# init dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
API_KEY = os.getenv("API_KEY")
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=API_KEY,
    user_agent=USER_AGENT,
    username=USER_NAME,
    password=PASSWORD
)

popular_subreddits = reddit.subreddits.popular()

with open("post.json", "r") as file:
    json_obj = json.load(file)

# add all popular subreddit-names to list
for iterator in popular_subreddits:
    subreddits.append(iterator.display_name.lower())


post_title = json_obj["title"]
post_content = json_obj["content"]
post_subreddits = json_obj["subreddits"]

# combine subreddits
subreddits += post_subreddits

print("posting...")


while True:
    for iterator in subreddits:
        try:
            subreddit = reddit.subreddit(iterator)
            subreddit.submit(post_title, selftext=post_content)
            print("Successfully posted affiliate-link to: " + iterator)
        except:
            print("Could not post to: " + iterator)
            subreddits.remove(iterator)
    time.sleep(60 * 30)
