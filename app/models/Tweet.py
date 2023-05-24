import uuid
import sirope

class Tweet:
    def __init__(self, owner, text = "text", picture = None, likes = [], answers = []):
        self.id = uuid.uuid1().hex
        self.owner = owner #username of tweet's author
        self.text = text
        self.picture = picture
        self.likes = likes #list of usernames that currently like the tweet
        self.answers = answers #list of ids of tweets replying to this tweet

    def get_id(self):
        return self.id

    #returns True if username param already liked the tweet
    def has_liked(self, username):
        return username in self.likes
    
    #likes or unlikes the tweet
    def like(self, username):
        if self.has_liked(username):
            self.likes.remove(username)
        else:
            self.likes.append(username)

    def get_number_likes(self):
        return len(self.likes)
    
    def its_owner(self, username):
        return self.owner == username

    def add_answer(self, tweet):
        self.answers.append(tweet.get_id())

    """
    Returns a list with the tweets replying to this one.
    If there's a reference not found in the database,
    it's removed from the list
    """
    def get_answers(self, s: sirope.Sirope):
        toret = []
        for id in self.answers:
            tweet = Tweet.find(s, id)
            if tweet != None:
                toret.append(tweet)
            else:
                self.answers.remove(id)
        return toret
    
    @staticmethod
    def find(s: sirope.Sirope, id: str):
        return s.find_first(Tweet, lambda t: t.get_id() == id)
    
    def __str__(self):
        if self.text != None:
            return self.id + ": " + self.text
        else:
            return self.id + ": No text"