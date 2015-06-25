import urllib2
from BeautifulSoup import BeautifulSoup
import json
import twitter
import os
from PIL import Image, ImageFont, ImageDraw
import textwrap

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PROFILE_URL = "http://comentarios1.folha.com.br/perfil/175843?skin=folhaonline"

CONSUMER_KEY = "XXXXXXXXXXXXXXXXXX"
CONSUMER_SECRET = "XXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN_SECRET = "XXXXXXXXXXXXXXXXXX"

IMG_WIDTH, IMG_HEIGHT = (800, 400)
BLUE_BG = (38, 169, 255)
FOLHA_FONT = "gloucester.ttf"
FONT_SIZE = 64

font = ImageFont.truetype(FOLHA_FONT, FONT_SIZE)

# text + link + media (140 - 23 - 23 - len("..."))
TWEET_MAX_SIZE = 91

class PlacarDoAlicate:
    def __init__(self):
        self.soup = None
        self.comments = []
        self.last_comment_id = None
        self.score = None

        self.twitter = twitter.Api(consumer_key = CONSUMER_KEY,
                                   consumer_secret = CONSUMER_SECRET,
                                   access_token_key = ACCESS_TOKEN,
                                   access_token_secret = ACCESS_TOKEN_SECRET)

        self.get_last_comments()
        self.load_history()

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
                title = comment.article.find("div", {"class": "comment-meta"}).h6.span.text
                self.comments.append((int(comment.article['data-id'][8:]), text, title))
        except:
            pass

        self.last_comment_id = comments_html[0].article['data-id'][8:]

    def get_scoreboard(self):
        profile_id = self.soup.find("address", { "class" : "profile-name" }).a.text
        score = profile_id[len("alicate("):-1]
        return score

    def load_history(self):
        try:
            with open(BASE_DIR + "/history.txt", "r") as f:
                self.last_comment_id, self.score = f.read().split(",")
        except:
            print("Failed to load history")

    def store_history(self):
        try:
            with open(BASE_DIR + "/history.txt", "w") as f:
                f.write("%s,%s" % (self.last_comment_id, self.score))
        except:
            print("Failed to store history")

    def tweet_comments(self):
        for (cid, text, title) in self.comments[::-1]:
            if cid > int(self.last_comment_id):
                self.send_tweet(cid, text, title)

    def send_tweet(self, cid, text, title):
        if len(text) > TWEET_MAX_SIZE:
            text = text[:TWEET_MAX_SIZE] + "..."

        tweet = "%s http://www.folha.com/cs%d" % (text, cid)
        self.generate_post_media(title)
        self.twitter.PostMedia(tweet, BASE_DIR + "/news_title.png")
        #print tweet

    def generate_post_media(self, title):
        img = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT), BLUE_BG)
        draw = ImageDraw.Draw(img)

        offset = 5
        for line in textwrap.wrap(title, width = 40):
            w, h = draw.textsize(line, font = font)
            draw.text((((IMG_WIDTH-w)/2), ((IMG_HEIGHT-h)/2) + offset-h), line, (255, 255, 255), font = font)
            offset += font.getsize(line)[1]

        draw = ImageDraw.Draw(img)
        img.save(BASE_DIR + "/news_title.png")

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

    def update_banner(self):
        self.generate_banner()
        self.twitter.UpdateBanner(BASE_DIR + "/score_banner.png")

if __name__ == '__main__':
    pa = PlacarDoAlicate()
    pa.update_banner()
    pa.tweet_comments()
    pa.store_history()
