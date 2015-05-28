import urllib2
from BeautifulSoup import BeautifulSoup
import json
import twitter

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

    def store_last_comment(self):
        try:
            with open("last_comment.txt", "w") as f:
                f.write(self.last_comment_id)
        except:
            print("Failed to store last comment")

    def load_last_comment(self):
        try:
            with open("last_comment.txt", "r") as f:
                return f.read()
        except:
            print("Failed to load last comment")

    def tweet_comments(self):
        last = int(self.load_last_comment())
        for (cid, text) in self.comments[::-1]:
            if cid > last:
                self.send_tweet(cid, text)

        self.store_last_comment()

    def send_tweet(self, cid, text):
        if len(text) > 114:
            text = text[:114] + "..."

        tweet = "%s http://www.folha.com/cs%d" % (text, cid)
        self.twitter.PostUpdate(tweet)

if __name__ == '__main__':
    pa = PlacarDoAlicate()
    pa.tweet_comments()
