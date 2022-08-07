#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Imports
import re
from psaw import PushshiftAPI
import unicodedata, sys
from textblob import TextBlob
import replacements as rep

api = PushshiftAPI()

## Adjust to your liking
# Which subreddit to process
subreddits = ['Dreams']
# The directory to store post-processes texts
directory = "./output" # Create this
# The directory to store skipped texts
skipped_dir = "./skipped" # Create this
# The directory to store original texts (pre-validation)
validations_dir = "./validations" # Create this

submission_count = 1000 # Don't touch
# If text is removed for being irrelevant to our training, save a copy of the original text with the reasons
save_validation_copies = False
# If test is removed for being irrelevant, print the reasons it was removed in the console at runtime
print_validation_reasons = False
# Set to false to stop spelling autocorrect on text. This is a very slow process and will delay the processing very much! (10x or more)
spellcheck = False
# The minimum amount of words the post should have (post-processing) in order to keep it
min_word_count = 100
# How many copies of each post to store, depending on its reddit score
duplicates = {
    # This means we do not save downvoted posts. Increase the first key to 1 or more to only store texts with a score threshold over that amount.
    0: 0,
    # This means we save one copy if the post has 1-3 upvotes
    3: 1,
    # 4-5 upvotes etc...
    5: 2,
    10: 3,
    25: 4,
    50: 5,
    75: 6,
    100: 7,
}

skipped = 0


validations = [
    {
        "regex": re.compile(r"(Hello|Greetings|Aloha|Hey|Hi) ?(everyone|everybody|guys|girls|lads|peeps)?[!.]?", flags=re.I|re.M),
        "sub": '',
        "reason": "Greetings"
    },
    {
        "regex": re.compile(r"I need some (help|assistance) ?(everyone|everybody|guys|girls|lads|peeps)?[!. ]", flags=re.I|re.M),
        "sub": '',
        "reason": "Requests Assistance"
    },
    {
        "regex": re.compile(r"(Last Night|Yesterday|(About)? ?([a1-9]) (day|month)s? ago)|a long time ago", flags=re.I|re.M),
        "sub": '',
        "reason": "Timing Reference"
    },
    {
        "regex": re.compile(r"What do you.+?think.*?\?|Any(body|one).+?interpret.+?\?|what does.+?mean\?|Any ideas? what.+?[.?\r\n]", flags=re.I|re.M),
        "sub": '',
        "reason": "Interpretation"
    },
    {
        "regex": re.compile(r"Throwaway( account)?|First time posting( here)?|I've never posted.*?dreams?\.", flags=re.I|re.M),
        "sub": '',
        "reason": "Throwaway reference"
    },
    {
        "regex": re.compile(r"(^|[.,!?]).*?(w[ao]ke|aw[ao]ken) ?(up)?.*?([,.!?\r\n]|$)", flags=re.I|re.M),
        "sub": '',
        "reason": "Awaken reference"
    },
    {
        "regex": re.compile(r"(^|[.,!?]).*?(to )?(sleep|slept).*?([,.!?\r\n]|$)", flags=re.I|re.M),
        "sub": '',
        "reason": "Sleeping reference"
    },
    {
        "regex": re.compile(r"(Can|Does) any(one|body).+?\?|I'm interested i[fn].+?\?|my question is.+?[.?\r\n]", flags=re.I|re.M),
        "sub": '',
        "reason": "Question"
    },
    {
        "regex": re.compile(r"&amp;#x200B|and#x200B;", flags=re.I|re.M),
        "sub": '',
        "reason": "Garbage"
    },
    {
        "regex": re.compile(r"^.*(backstory|background:).+?.", flags=re.I|re.M),
        "sub": '',
        "reason": "Backstory",
        # "force_notify": True,
    },
    {
        "regex": re.compile(r"I want to hear other peoples perspective of this", flags=re.I|re.M),
        "sub": '',
        "reason": "Ponderings",
        # "force_notify": True,
    },
    {
        "regex": re.compile(r"Thank you for reading", flags=re.I),
        "sub": '',
        "reason": "Thanks",
    },
    {
        "regex": re.compile(r" ts ", flags=re.I),
        "sub": ' this ',
        "reason": "lazy typo",
        "avoid_store": True,
    },
    {
        "regex": re.compile(r"(^|[,.!?\r\n]).*?(dream|nightmare)s?.*?(?!dream)([,.!?\r\n]|$)", flags=re.I),
        "sub": '',
        "reason": "Dream References",
    },
    {
        # People REALLY like repeating the word 'dream' in many creative ways
        "regex": re.compile(r"(^|[,.!?\r\n]).*?(dream|nightmare)s?.*?(?!dream)([,.!?\r\n]|$)", flags=re.I),
        "sub": '',
        "reason": "Excessive Dream References",
    },
]


def save_skipped(post, reason):
    global skipped
    skipped += 1
    print(f"{skipped} Skipped {post.id}: {reason}.")
    try:
        filepath = f"{skipped_dir}/{subreddit}-{post.id}.txt"
        with open(f"{filepath}", 'w') as file:
            file.write(f"{selftext}")
    except UnicodeEncodeError:
        print(f"failed to parse post with id {post.id}")

def save_for_validation(post, reason, force_notify=False):
    if print_validation_reasons or force_notify:
        print(f"Validate {post.id}: {reason}.")
    try:

        filepath = f"{validations_dir}/{subreddit}-{post.id}.txt"
        with open(f"{filepath}", 'w') as file:
            file.write(f"\n[{reason}]\n")
            file.write(f"{selftext}")
    except UnicodeEncodeError:
        print(f"failed to parse post with id {post.id}")

def validate_text(post, selftext):
    valid_found = []
    for v in validations:
        if v["regex"].search(selftext):
            valid_found.append(v["reason"])
            if not v.get("avoid_store") and save_validation_copies:
                save_for_validation(post, valid_found,v.get("force_notify"))
        selftext = v["regex"].sub(v["sub"],selftext)
    return(selftext)


try:
#     t = """Well I'm make this very easy to understand ; my soul was really weeping because I struggle in real life as well.
# A strange man in a suit and hat that was black sat next to me at this job, not scary but quite calming and sincere.. he kept comforting me and telling me he knew and understood all my pain, and that my soul should be set free..
# For some reason I accepted s grant, and next tng you know I'm in s office and he pulls out and wad of money and checks for me, I felt so strange afterwards.
# my boyfriend asked me if I was okay, I couldn't answer m, I just said I'm fine and walked around my house like I didn't recognize it ...
# I went to my moms, and our family dog aggressively barked and growled at me! It made me feel so sad, but yet again I couldn't let out my emotions
# My mom knew sometng was wrong.. she looked in to my eyes and knew what I did, but yet she comforted me without saying a word, we sat down, and held eachother..
# The last tng I can remember is my mother telling me no matter what she will make this my best life ever.. and she will do whatever to make sure I enjoy it..
# I woke up crying and it felt so real I was terrified, it's so bizarre because I didn't get to use any of the money, my heart chose to go to my family first and I have no idea why..
# Is someone or sometng trying to show me the consequences of some sort ?"""
#     print(t)
#     selftext = re.sub(r"(^|[.,!?]).*?(w[ao]ke|aw[ao]ken) ?(up)?.*?[.,!?\r\n]", '', t, flags=re.I|re.M)
#     print(selftext)
#     sys.exit()
    skipped_counts = {}
    for subreddit in subreddits:
        one_entry = list(api.search_submissions(subreddit=subreddit,filter=['id','title', 'selftext', 'link_flair_text'],limit=1))
        continue_point = one_entry[0].created_utc + 1
        while submission_count >= 990:
            print(f"Continuing iteration before time: {continue_point}")
            submissions = list(api.search_submissions(subreddit=subreddit,before=continue_point,filter=['score', 'is_self', 'id','title', 'selftext', 'link_flair_text'],limit=1000))
            submission_count = len(submissions)
            for post in submissions:
                continue_point = post.created_utc
                if post.is_self == False:
                    # print(f"Post {post.id} is not a self-post")
                    continue
                if not hasattr(post, 'selftext'):
                    print(f"Post {post.id} does not have a selftext")
                    continue
                selftext = post.selftext
                if re.search(r"[\s](poll|questionnaire|Question:)[\s]", selftext, flags=re.I|re.M):
                    save_skipped(post, "Appears to be a poll")
                    skipped_counts['poll'] = skipped_counts.get('poll',0) + 1
                    continue
                if re.search(r"[\s](payment|I'm a medium)[\s]", selftext, flags=re.I|re.M):
                    save_skipped(post, "Appears to be a merchant")
                    skipped_counts['merchant'] = skipped_counts.get('merchant',0) + 1
                    continue
                if re.search(r"[\s](rape|molestation|sexual assault)[\s]", selftext, flags=re.I|re.M):
                    save_skipped(post, "Appears to be about sexual abuse")
                    skipped_counts['sexual abuse'] = skipped_counts.get('sexual abuse',0) + 1
                    continue
                if re.search(r"NSFW", selftext, flags=re.I|re.M):
                    save_skipped(post, "Removed NSFW")
                    skipped_counts['NSFW'] = skipped_counts.get('NSFW',0) + 1
                    continue
                selftext = validate_text(post,selftext)
                selftext = rep.ai_training_format(selftext)
                if len(selftext.split()) < min_word_count:
                    continue
                if spellcheck:
                    selftext = TextBlob(selftext).correct()
                try:
                    copies = 0
                    for v in duplicates:
                        if post.score <= v:
                            copies = duplicates[v]
                            break
                    if copies == 0:
                        save_skipped(post, "lower than minimum score")
                        skipped_counts['low score'] = skipped_counts.get('low score',0) + 1
                    subiter = 1
                    # print(f"saving {copies} copies of {post.id} for {post.score} score")
                    for iter in range(copies):
                        filepath = f"{directory}/{subreddit}-{post.id}-{subiter}.txt"
                        subiter += 1
                        with open(f"{filepath}", 'w') as file:
                            file.write(f"{selftext}")
                except UnicodeEncodeError:
                    print(f"failed to parse post with id {post.id}")
    filepath = f"{skipped_dir}/_skipped_counts.txt"
    with open(f"{filepath}", 'w') as file:
        file.write(f"{skipped_counts}")
    print(f"Skipped Counts: {skipped_counts}")
    # while submission_count > 0: #Check if we're still doing useful things
    #     #Obtain new posts
    #     submissions = list(api.search_submissions(before=deadline,subreddit='piracy',filter=['url','author','title','subreddit'],limit=10))
    #     #Count how many posts we've got
    #     submission_count = len(submissions)

    #     #Iterate over posts
    #     for sub in submissions:
    #         #Obtain data from post
    #         deadline = int(sub.created_utc)
    #         sub_id = sub.id

    #         #Better formatting to post the sub title before the comments
    #         sub_title = sub.title
    #         if len(sub_title) > 40:
    #             sub_title = sub_title[:40]+"..."
    #         print(f"[{sub_id}] Removing submission from {datetime.datetime.fromtimestamp(deadline)} [{deadline}]: {sub_title}")

    #         #Iterate over comments if required
    #         if remove_comments:
    #             #Obtain comments
    #             sub.comments.replace_more(limit=None)
    #             comments = sub.comments.list()
    #             #Remove comments
    #             print(f'-[{sub_id}] Found {len(comments)} comments to delete')
    #             for comment in comments:
    #                 comment_body = comment.body.replace("\n", "")
    #                 if len(comment_body) > 50:
    #                     comment_body = "{}...".format(comment_body[:50])
    #                 print("--[{}] Removing comment: {}".format(sub_id, comment_body))
    #                 delRetry = True
    #                 delIter = 1
    #                 while delRetry:
    #                     try:
    #                         if not testing_mode: comment.mod.remove()
    #                         delRetry = False
    #                     except:
    #                         print(f'[Error] Service unavailable while trying to delete comment. Retry No #{delIter}')
    #                         delIter += 1
    #                         time.sleep(5)
    #                         continue

    #         #Remove post
    #         if not testing_mode: sub.mod.remove()

except KeyboardInterrupt:
    print("Stopping due to impatient human.")
