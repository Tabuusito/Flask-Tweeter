import flask_login
import sirope

from werkzeug.security import check_password_hash

class User(flask_login.UserMixin):
    def __init__(self, username, password, picture = None, tweets = []) -> None:
        self.username = username
        self.password = password
        self.picture = picture
        self.tweets = tweets #list of ids of tweets published by this user
    
    def get_id(self):
        return self.username
    
    def chk_password(self, pswd):
        return check_password_hash(self.password, pswd)
    
    def post_tweet(self, tweet):
        self.tweets.append(tweet.get_id())

    def delete_tweet(self, tweet):
        self.tweets.remove(tweet.get_id())
    
    @staticmethod
    def find(s: sirope.Sirope, username: str):
        return s.find_first(User, lambda u: u.username == username)

        
    def __str__(self):
        return self.username + ": Amount tweets: " + str(len(self.tweets))