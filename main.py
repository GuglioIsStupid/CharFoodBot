import random, os, time, re
import tweepy
from dotenv import load_dotenv
from foods import foodList
from randomList import randomList

TimeBetweenTweets:int = 60 * 60 * 0.5 # 30 minutes. 60 seconds * 60 minutes * 0.5 hours

load_dotenv(".env")

Client = tweepy.Client(
    consumer_key= os.environ["consumer_key"],
    consumer_secret= os.environ["consumer_secret"],
    access_token= os.environ["access_token"],
    access_token_secret= os.environ["access_token_secret"],
    bearer_token= os.environ["bearer_token"]
)

auth = tweepy.OAuth1UserHandler(
    consumer_key= os.environ["consumer_key"],
    consumer_secret= os.environ["consumer_secret"],
    access_token= os.environ["access_token"],
    access_token_secret= os.environ["access_token_secret"]
)

api = tweepy.API(auth, wait_on_rate_limit=True)

createdTweet:str = ""

excludedExts:list = [
    ".svg"
]

"""
e.g. layout
- Characters/
    - {Franchise}
        - {Char Name}
"""
charactersPath:str = "Characters/"
foodPath:str = "Food/"

now:int = 0

def generateTweet() -> list:
    baseStr:str = random.choice(randomList)
    files:list = []
    ####
    ###  Generate Character(s)
    ####

    # For each <character> with regex
    for match in re.findall(r"<character>", baseStr):
        franchise:str = random.choice(os.listdir(charactersPath))

        char:str = random.choice(os.listdir(os.path.join(charactersPath, franchise)))

        while re.search(".svg$", char):
            char = random.choice(os.listdir(os.path.join(charactersPath, franchise)))

        files.append(os.path.join(charactersPath, franchise, char))
        baseStr = baseStr.replace(match, re.sub(".png", "", char), 1)

    ####
    ###  Generate Food(s)
    ####
    for match in re.findall(r"<food>", baseStr):
        food:str = random.choice(foodList)

        for match2 in re.findall(r"\{file [^}]+\.[a-zA-Z0-9]+\}", food):
            food = re.sub(match2, "", food)

            file:str = re.sub(r"\{file ([^}]+\.[a-zA-Z0-9]+)\}", r"\1", match2)

            while re.search(r"\.svg$", file):
                file = re.sub(r"\{file ([^}]+\.[a-zA-Z0-9]+)\}", r"\1", match2)

            files.append(os.path.join(foodPath, file))

        baseStr = re.sub(match, food, baseStr)

    return [baseStr, files]
    
if __name__ == "__main__":
    while True:
        if time.time() - (now or 0) >= TimeBetweenTweets:
            tweetData:list = generateTweet()
            now = time.time()

            medias:list = []
            for file in tweetData[1]:
                medias.append(api.media_upload(file).media_id)
            
            tweet:str = tweetData[0]
            print(tweetData)

            Client.create_tweet(text=tweet, media_ids=medias)
        else:
            time.sleep(1)