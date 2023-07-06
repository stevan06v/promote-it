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
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


time.sleep(60 * 30)
while True:
    with open("post.json", "r") as file:
        json_obj = json.load(file)

    popular_subreddits = reddit.subreddits.popular()
    subscribed_subreddits = [subreddit.display_name.lower() for subreddit in reddit.user.subreddits(limit=None)]

    subscribed_subreddits = [subreddit.display_name.lower() for subreddit in reddit.user.subreddits(limit=None)]

    # add all popular subreddit-names to list
    for iterator in popular_subreddits:
        subreddits.append(iterator.display_name.lower())

    post_title = json_obj["title"]
    post_content = json_obj["content"]
    post_subreddits = json_obj["subreddits"]

    # combine subreddits
    subreddits += post_subreddits
    subreddits += subscribed_subreddits

    print("posting...")

    for iterator in subreddits:
        try:
            subreddit = reddit.subreddit(iterator)
            subreddit.submit(post_title, selftext=post_content)
            print(bcolors.OKGREEN + "Successfully posted affiliate-link to: " + iterator + bcolors.ENDC)
        except:
            print(bcolors.FAIL + "Could not post to: " + iterator + bcolors.ENDC)
            subreddits.remove(iterator)

    subreddits.clear()
    time.sleep(60 * 10)
