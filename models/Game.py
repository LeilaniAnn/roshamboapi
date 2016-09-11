"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""
import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

COMMAND = ['rock','paper','scissors','lizard','spock','cancel']
RESULTS = ['win', 'lose', 'draw','cancelled', 'unknown']

    
class Game(ndb.Model):
    """Game object"""
    
    playerCommand = ndb.StringProperty(required=True)
    opponentCommand = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    

    @classmethod
    def new_game(cls, user, playerCommand):
        """Creates and returns a new game"""
        # The opponent's command is randomly selected.
        x = random.randint(0,4)
        opponentCommand = COMMAND[x]
        # To avoid errors, always lowercase commands
        playerCommand = playerCommand.lower()

        if playerCommand not in COMMAND:
            raise endpoints.BadRequestException('Please select command from the following: Rock, Paper, Scissors, Lizard, Spock, or cancel')
        result = None
        if playerCommand == 'cancel':
        	opponentCommand = 'cancel'
        	result = 'cancelled'
        elif playerCommand != opponentCommand:
            if playerCommand == 'rock':
            	if opponentCommand == 'scissors' or opponentCommand == 'lizard':
            		result = 'win'
            	elif opponentCommand == 'paper' or opponentCommand == 'spock':
            		result = 'lose'
            	else:
            		result = 'unknown'
            if playerCommand == 'paper':
            	if opponentCommand == 'rock' or opponentCommand == 'spock':
            		result = 'win'
            	elif opponentCommand == 'scissors' or opponentCommand == 'lizard':
            		result = 'lose'
            	else:
            		result = 'unknown'
            if playerCommand == 'scissors':
            	if opponentCommand == 'paper' or opponentCommand == 'lizard':
            		result = 'win'
            	elif opponentCommand == 'rock' or opponentCommand == 'spock':
            		result = 'lose'
            	else:
            		result = 'unknown'
            if playerCommand == 'lizard':
            	if opponentCommand == 'spock' or opponentCommand == 'paper':
            		result = 'win'
            	elif opponentCommand == 'rock' or opponentCommand == 'scissors':
            		result = 'lose'
            	else:
            		result = 'unknown'
            if playerCommand == 'spock':
            	if opponentCommand == 'scissors' or opponentCommand == 'rock':
            		result = 'win'
            	elif opponentCommand == 'paper' or opponentCommand == 'lizard':
            		result = 'lose'
            	else:
            		result = 'unknown'
        else:
        	result = 'draw'            		            		
        game = Game(user=user,
                    playerCommand = playerCommand,
                    opponentCommand = opponentCommand,
                    result = result
                    )
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.playerCommand = self.playerCommand
        form.opponentCommand = self.opponentCommand
        form.result = self.result
        form.message = message
        return form

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1)
    playerCommand = messages.StringField(2)
    opponentCommand = messages.StringField(3)
    result = messages.StringField(4)
    message = messages.StringField(5)
    user_name = messages.StringField(6)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    playerCommand = messages.StringField(2, required=True)
    
class GameForms(messages.Message):
    """Multiple GameForm container"""
    items = messages.MessageField(GameForm, 1, repeated=True)
