"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""
from protorpc import messages
from google.appengine.ext import ndb

COMMANDS = ['rock', 'paper', 'scissors', 'lizard', 'spock']
RESULTS = ['win', 'lose', 'draw']


class Game(ndb.Model):
    """Game object"""
    playerOne = ndb.KeyProperty(required=True, kind='User')
    playerTwo = ndb.KeyProperty(required=True, kind='User')
    playerOne_command = ndb.StringProperty(repeated=True)
    playerTwo_command = ndb.StringProperty(repeated=True)
    result = ndb.StringProperty(required=True, default = "unknown")
    cancelled = ndb.BooleanProperty(required=True, default=False)
    over = ndb.BooleanProperty(required=True, default=False)
    rounds = ndb.IntegerProperty(required=True, default=1)

    @classmethod
    def new_game(cls, playerTwo, playerOne, rounds=1):
        """Creates and returns a new game"""
        game = Game(playerOne=playerOne,
                    playerTwo=playerTwo,
                    rounds=rounds
                    )
        game.put()
        return game

    def makeMove(self):
        """ After game is created, now it's time to play game """

        playerOne_command = self.playerOne_command
        playerTwo_command = self.playerTwo_command
        # Check to see if players have completed round
        if len(playerOne_command) == len(playerTwo_command):
            if len(playerOne_command) == self.rounds:
                p1 = self.playerOne.get()
                p2 = self.playerTwo.get()
                playerOne_wins = 0
                playerTwo_wins = 0
                # for each game, declare a winner
                for command in range(0, self.rounds):
                    p1_command = playerOne_command[command]
                    p2_command = playerTwo_command[command]
                    # if player tries to play a wrong command
                    if p1_command != p2_command:
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
                            if p2_command == 'paper' or p2_command == 'lizard':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                            elif p2_command == 'rock' or p2_command == 'spock':
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
                           if p2_command == 'scissors' or p2_command == 'rock':
                                playerOne_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                           elif p2_command == 'paper' or p2_command == 'lizard':
                                playerTwo_wins += 1
                                p1.gamesPlayed += 1
                                p2.gamesPlayed += 1
                self.over = True
                if playerOne_wins > playerTwo_wins:
                    self.result = p1.name + ' wins the round: ' + str(playerOne_wins) + '-' + str(playerTwo_wins)
                    p1.wins += 1
                    p1.update_user_score()
                    p1.put()
                    p2.losses += 1
                    p2.update_user_score()
                    p2.put()
                elif playerOne_wins < playerTwo_wins:
                    self.result = p2.name + ' wins the round: ' +  str(playerTwo_wins) + '-' +  str(playerOne_wins)
                    p2.wins += 1
                    p2.update_user_score()
                    p2.put()
                    p1.losses += 1
                    p1.update_user_score()
                    p1.put()
                else:
                   self.result = 'draw'
            else:
                self.over = False
        else:
            self.over = False                                       

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        playerOne_name = self.playerOne.get().name
        playerTwo_name = self.playerTwo.get().name
        form.playerOne_name= playerOne_name
        form.playerTwo_name = playerTwo_name
        if self.cancelled:
            form_msg = "{} - Game Status: CANCELLED".format(message)
        else:
            if not self.over:
                form_msg = "{} - Game Status: Game still in progress".format(message)
            else:
                form_msg = "{} - Game Status: Game over -  {}".format(message, self.result)
        
        form.message = form_msg
        return form

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    playerOne_name = messages.StringField(2, required=True)
    playerTwo_name = messages.StringField(3, required=True)
    message = messages.StringField(4, required=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    playerOne = messages.StringField(1, required=True)
    playerTwo = messages.StringField(2, required=True)
    rounds = messages.IntegerField(3)
    
class GameForms(messages.Message):
    """Multiple GameForm container"""
    items = messages.MessageField(GameForm, 1, repeated=True)
            
class MakeMoveForm(messages.Message):
    """Used to make a play in an existing game."""
    urlsafe_key = messages.StringField(1, required = True)
    user_name = messages.StringField(2, required = True)
    command = messages.StringField(3, required = True)
