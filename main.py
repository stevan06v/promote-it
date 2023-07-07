import random

import praw
import os
import json
from dotenv import load_dotenv
import time

json_obj = {}
subreddits = set()
listSizes = []

failedPostings = set()

counter = 0

startTime = 0
endTime = 0
measuredTime = 0

# temp times
startTempTime = 0
endTempTime = 0

post_title = ""
post_content = ""
post_flair = ""
post_flair_id = ""
post_keywords = []
post_image = ""

# set the amount of keywords you want to get subreddit-lists from
# [0-283]
keywordAmount = 200

# in minutes
sleep = 20

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


# count posts
countSuccess = 0
countFailed = 0

while True:
    startTime = time.time()
    startTempTime = time.time()
    if counter <= 1:
        with open("post.json", "r") as file:
            json_obj = json.load(file)

        # any kind of subreddit
        default_subreddits = set(iterator.display_name for iterator in reddit.subreddits.default())
        popular_subreddits = set(iterator.display_name for iterator in reddit.subreddits.popular())
        subscribed_subreddits = set(iterator.display_name for iterator in reddit.user.subreddits(limit=None))

        post_title = json_obj["title"]
        post_content = json_obj["content"]
        post_keywords = json_obj["keywords"]
        post_flair = json_obj["flair"]

        print("Collecting data...")

        # add lists of keyword outputs
        for iterator in post_keywords:
            # convert object to list of strings
            subredditsPerKeyword = list(iterator.display_name for iterator in reddit.subreddits.search(iterator))
            subreddits.update(subredditsPerKeyword)

        # combine subreddits
        subreddits.update(subscribed_subreddits)
        subreddits.update(default_subreddits)
        subreddits.update(popular_subreddits)

    endTempTime = time.time()

    passedTempTime = endTempTime - startTempTime

    # temp stats
    print("=================================")
    print("Posts to proceed: " + str(len(subreddits)))
    print("Passed time collecting subreddits: " + str(passedTempTime))
    print("=================================")

    print("Posting...")
    time.sleep(5)

    for iterator in subreddits:
        try:
            subreddit = reddit.subreddit(iterator)

            # get all attributes with dir --> pretty cool
            requirements = subreddit.post_requirements()

            # check if images are allowed or nor
            isTextPostAllowed = True if requirements["body_restriction_policy"] == "none" else False

            if not isTextPostAllowed:
                failedPostings.add(iterator)
                continue

            # get random flair id (I have actually no fucking clue what a flair is or does but never mind :) )
            post_flair_obj = random.choice(list(subreddit.flair.link_templates))

            # parse the flair out the post
            post_flair = post_flair_obj["text"]
            post_flair_id = post_flair_obj["id"]

            # error occurs if flai id is wrong
            if post_flair_id != "":
                subreddit.submit(title=post_title, selftext=post_content, flair_text=post_flair, nsfw=False,
                                 flair_id=post_flair_id)
            else:
                subreddit.submit(title=post_title, selftext=post_content, flair_text=post_flair, nsfw=False)

            print(bcolors.OKGREEN + "Successfully posted affiliate-link to: " + str(iterator) + bcolors.ENDC)
            countSuccess = countSuccess + 1
        except Exception as e:
            print(bcolors.FAIL + "Could not post to: " + str(iterator) + bcolors.ENDC)
            print("Error: ", str(e))
            countFailed = countFailed + 1

            failedPostings.add(iterator)

    # calculations
    successRate = len(subreddits) / countSuccess if countSuccess != 0 else 0
    failureRate = 100 - successRate
    passedTime = (endTime - startTime) / 60

    subreddits.difference(failedPostings)

    endTime = time.time()

    print("=================================")
    print("Iteration count: " + str(counter + 1))
    print("Attempted post tries: " + str(len(subreddits)) + ".")
    print(bcolors.OKGREEN + "Successful posts: " + str(countSuccess) + "." + bcolors.ENDC)
    print(bcolors.FAIL + "Failed posts: " + str(countFailed) + "." + bcolors.ENDC)
    print(bcolors.OKGREEN + "Successful posts-rate: " + str(successRate) + "%." + bcolors.ENDC)
    print(bcolors.FAIL + "Failed posts-rate: " + str(failedPostings) + "%." + bcolors.ENDC)
    print("Passed time: " + str(passedTime) + "min.")
    print("=================================")

    counter += 1
    time.sleep(sleep * 60)
