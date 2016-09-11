import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

class RankForm(messages.Message):
    """Representation of a User's ranking record"""
    user_name = messages.StringField(1, required=True)
    win_ratio = messages.StringField(2, required=True)
    
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
    
class RankForms(messages.Message):
    """Multiple RankForm container"""
    items = messages.MessageField(RankForm, 1, repeated=True)