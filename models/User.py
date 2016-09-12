import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

from rank import RankForm

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    gamesPlayed = ndb.IntegerProperty(default=0)
    draws = ndb.IntegerProperty(default=0)
    win_ratio = ndb.FloatProperty(default=0.0)
    
    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = UserForm()
        form.user_name = self.name
        form.win_ratio = str(self.win_ratio)
        form.wins = str(self.wins)
        form.losses = str(self.losses)
        form.gamesPlayed = str(self.gamesPlayed)
        form.draws = str(self.draws)
        return form

    def to_rank_form(self):
        form = RankForm()
        form.user_name = self.name
        form.win_ratio = str(self.win_ratio)
        return form

    def update_user_score(self):
        """ Update User Score """
        if self.losses + self.wins == 0:
            self.win_ratio = 0.0
        else:
            self.win_ratio = float(self.wins)/(self.gamesPlayed) * 100

class UserForm(messages.Message):
    """UserForm for information about the current user"""
    user_name = messages.StringField(1, required=True)
    win_ratio = messages.StringField(2, required=True)
    gamesPlayed = messages.StringField(3, required=True)
    wins = messages.StringField(4, required=True)
    losses = messages.StringField(5, required=True)
    draws = messages.StringField(6, required=True)        

class UserForms(messages.Message):
    """Multiple UserForm container"""
    items = messages.MessageField(UserForm, 1, repeated=True)