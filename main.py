import urllib2
from BeautifulSoup import BeautifulSoup
import json
import twitter
import os
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PROFILE_URL = "http://comentarios1.folha.com.br/perfil/175843?skin=folhaonline"

CONSUMER_KEY = "XXXXXXXXXXXXXXXXXX"
CONSUMER_SECRET = "XXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN_SECRET = "XXXXXXXXXXXXXXXXXX"

class PlacarDoAlicate:
    def __init__(self):
        self.soup = None
        self.comments = []
        self.last_comment_id = None
        self.score = self.load_score()

        self.twitter = twitter.Api(consumer_key = CONSUMER_KEY,
                                   consumer_secret = CONSUMER_SECRET,
                                   access_token_key = ACCESS_TOKEN,
                                   access_token_secret = ACCESS_TOKEN_SECRET)

        self.get_last_comments()

    def get_soup(self):
        try:
            html = urllib2.urlopen(PROFILE_URL).read()
            self.soup = BeautifulSoup(html.decode('cp1252'))
        except:
            print("Error, site down")

    def get_last_comments(self):
        self.get_soup()
        try:
            comments_html = self.soup.findAll("li", { "class" : "comment comment_li"})
            for comment in comments_html:
                text = comment.article.find("div", {"class": "comment-body"}).p.text
                self.comments.append((int(comment.article['data-id'][8:]), text))
        except:
            pass

        self.last_comment_id = comments_html[0].article['data-id'][8:]

    def get_scoreboard(self):
        profile_id = self.soup.find("address", { "class" : "profile-name" }).a.text
        score = profile_id[len("alicate("):-1]
        return score

    def store_last_comment(self):
        try:
            with open(BASE_DIR + "/last_comment.txt", "w") as f:
                f.write(self.last_comment_id)
        except:
            print("Failed to store last comment")

    def load_last_comment(self):
        try:
            with open(BASE_DIR + "/last_comment.txt", "r") as f:
                return f.read()
        except:
            print("Failed to load last comment")

    def load_score(self):
        try:
            with open(BASE_DIR + "/score.txt", "r") as f:
                return f.read()
        except:
            print("Failed to load score")

    def store_score(self):
        try:
            with open(BASE_DIR + "/score.txt", "w") as f:
                f.write(self.score)
        except:
            print("Failed to store score")

    def tweet_comments(self):
        last = int(self.load_last_comment())
        for (cid, text) in self.comments[::-1]:
            if cid > last:
                self.send_tweet(cid, text)

        self.store_last_comment()

    def send_tweet(self, cid, text):
        if len(text) > 91:
            text = text[:91] + "..."

        tweet = "%s http://www.folha.com/cs%d" % (text, cid)
        self.twitter.PostMedia(tweet, BASE_DIR + "/score_banner.png")

    def generate_banner(self):
        old_score = self.get_scoreboard()
        if old_score == self.score:
            return
        self.score = old_score

        font = ImageFont.truetype(BASE_DIR + "/kidsboardgamefont.ttf", 96)
        img = Image.new("RGBA", (700, 160), (204, 204, 204))
        draw = ImageDraw.Draw(img)
        draw.text((140, 25), self.score, (28, 28, 28), font = font)
        draw = ImageDraw.Draw(img)
        img.save(BASE_DIR + "/score_banner.png")

        #self.twitter.UpdateBanner(BASE_DIR + "/score_banner.png")
        self.store_score()

    def update_banner(self):
        self.generate_banner()
        self.twitter.UpdateBanner(BASE_DIR + "/score_banner.png")

if __name__ == '__main__':
    pa = PlacarDoAlicate()
    pa.update_banner()
    pa.tweet_comments()
