"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""
import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from User import User

COMMAND = ['rock', 'paper', 'scissors', 'lizard', 'spock']
RESULTS = ['win', 'lose', 'draw']


class Game(ndb.Model):
    """Game object"""
    playerOne = ndb.KeyProperty(required=True, kind='User')
    playerTwo = ndb.KeyProperty(required=True, kind='User')
    playerOne_command = ndb.StringProperty(required=True)
    playerTwo_command = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    cancelled = ndb.BooleanProperty(required=True, default=False)
    gameOver = ndb.BooleanProperty(required=True, default=False)
    totalRounds = ndb.IntegerProperty(required=True)

    @classmethod
    def new_game(cls, playerTwo, playerOne, totalRounds=1):
        """Creates and returns a new game"""
        game = Game(playerOne=playerOne,
                    playerTwo=playerTwo,
                    totalRounds=totalRounds
                    )
        game.put()
        return game

    def selectCommand(self):
        """ After game is created, now it's time to play game """
        # The opponent's command is randomly selected.
        # x = random.randint(0,4)
        # playerTwo = COMMAND[x]

        # To avoid errors, always lowercase commands
        playerOne_command = self.playerOne_command.lower()
        playerTwo_command = self.playerTwo_command.lower()
        # Check to see if players have completed round
        if len(playerOne_command) == len(playerTwo_command):
            if len(playerOne_command) == self.totalRounds:
                p1 = self.playerOne.get()
                p2 = self.playerTwo.get()
                playerOne_wins = 0
                playerTwo_wins = 0
                for command in range(0, self.totalRounds):
                    p1_command = playerOne_command[command]
                    p2_command = playerTwo_command[command]
                    if p1_command or p2_command not in COMMAND:
                        raise endpoints.BadRequestException(
                            'Please select command from the following: Rock, Paper, Scissors, Lizard, Spock, or cancel')
                    elif p1_command != p2_command:
                        if p1_command == 'rock':
                           if p2_command == 'scissors' or p2_command == 'lizard':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                           elif p2_command == 'paper' or p2_command == 'spock':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                        if p1_command == 'paper':
                            if p2_command == 'rock' or p2_command == 'spock':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                            elif p2_command == 'scissors' or p2_command == 'lizard':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                        if p1_command == 'scissors':
                            if playerTwo == 'paper' or playerTwo == 'lizard':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                            elif playerTwo == 'rock' or playerTwo == 'spock':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                        if p1_command == 'lizard':
                           if p2_command == 'spock' or p2_command == 'paper':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                           elif p2_command == 'rock' or p2_command == 'scissors':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                        if p1_command == 'spock':
                           if playerTwo == 'scissors' or playerTwo == 'rock':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                           elif playerTwo == 'paper' or playerTwo == 'lizard':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                self.game_over = True
                if playerOne_wins > playerTwo_wins:
                    self.result = p1.name + 'wins the round: ' + playerOne_wins + '-' + playerTwo_wins
                    p1.wins += 1
                    p2.losses += 1
                    p1.update_user_score()
                    p1.gamesPlayed += 1
                    p1.put()
                    p2.update_user_score()
                    p1.gamesPlayed += 1
                    p2.put()
                elif playerOne_wins < playerTwo_wins:
                    self.result = p2.name + 'wins the round: ' + playerTwo_wins + '-' + playerOne_wins
                    p2.wins = p2.wins + 1
                    p1.losses = p1.losses + 1
                    p1.update_user_score()
                    p1.put()
                    p2.update_user_score()
                    p2.put()
                else:
                   self.result = 'draw'
            else:
                self.gameOver = False
        else:
            self.gameOver = False                                       

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.playerOne = self.playerOne
        form.playerTwo = self.playerTwo
        form.result = self.result
        if self.cancelled:
            message = "{} - Game Status: CANCELLED".format(message)
        else:
            if not self.game_over:
                message = "{} - Game Status: Game still in progress".format(message)
            else:
                message = "{} - Game Status: Game over -  {}".format(message, self.game_result)
        
        form.message = message
        return form

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1)
    playerOne = messages.StringField(2)
    playerTwo = messages.StringField(3)
    result = messages.StringField(4)
    message = messages.StringField(5)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    playerOne = messages.StringField(2, required=True)
    totalRounds = messages.StringField(3)
    
class GameForms(messages.Message):
    """Multiple GameForm container"""
    items = messages.MessageField(GameForm, 1, repeated=True)
            
class SelectCommandForm(messages.Message):
    """Used to make a play in an existing game."""
    urlsafe_key = messages.StringField(1, required = True)
    user_name = messages.StringField(2, required = True)
    command = messages.StringField(3, required = True)
