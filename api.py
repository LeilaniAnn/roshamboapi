# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models.User import User
from models.Game import Game, NewGameForm, GameForm, GameForms, MakeMoveForm, COMMANDS
from models.Rank import StringMessage, RankForms
from utils import get_by_urlsafe


# Request containers
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

GET_GAME_REQUEST = endpoints.ResourceContainer(
                   urlsafe_game_key=messages.StringField(1),
                   )
GET_USER_GAMES = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            )
SELECT_COMMAND_REQUEST = endpoints.ResourceContainer(MakeMoveForm)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2)
                                          )
GET_USER_RANKINGS = endpoints.ResourceContainer(
    user_name=messages.StringField(1),)

CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
                      urlsafe_game_key=messages.StringField(1),
                      )
MEMCACHE_USER_STATS = 'USER_STATS'


@endpoints.api(name='roshamboAPI', version='v2')
class roshamboAPI(remote.Service):
    """Game API"""

# - - - - User Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name,
                    email=request.email
                   )
        user.put()
        # Send Welcome email.
        taskqueue.add(url='/tasks/send_welcome_email',
                      params={'user_key': user.key}
                      )
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=GET_USER_RANKINGS,
                      response_message=RankForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns all users and their win ratio"""
        return RankForms(items=[user.to_rank_form() for user in User.query().order(-User.win_ratio)])

    @endpoints.method(request_message=GET_USER_GAMES,
                      response_message=GameForms,
                      path='game/get_by_user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all games that the user is currently playing."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with the name {} does not exist!'.format(request.user_name))

        games = Game.query(
                ndb.AND(Game.over == False,
                        ndb.OR(Game.playerOne == user.key,
                               Game.playerTwo == user.key
                               )
                        )
                )
        return GameForms(items=[game.to_form('') for game in games])

    @endpoints.method(response_message=StringMessage,
                      path='user_stats',
                      name='get_user_stats',
                      http_method='GET')
    def get_user_stats(self, request):
        """Get the cached user stats"""
        return StringMessage(message=memcache.get(MEMCACHE_USER_STATS) or 'No Memcache Found, create game then try again')

    @staticmethod
    def _cache_user_stats():
        """Populates memcache after new game played - shows win ratio"""
        users = User.query()
        string = ''
        # Memcache string with player statistics
        for user in users:
            wins = user.wins
            losses = user.losses
            win_ratio = user.win_ratio
            user_stats = " {} {} {} {} {} {} {} Win Percentage: {}%--" \
                .format("Player:",
                        user.name.upper(),
                        "has",
                        wins,
                        "win" if wins < 1 else "wins",
                        losses,
                        "loss" if losses < 1 else "losses",
                        win_ratio
                        )

            string += user_stats

        memcache.set(MEMCACHE_USER_STATS, string)

# - - - - Game Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
      """Creates new game of Roshambo + Lizard + Spock. Rounds are optional - will default to 1"""
      playerOne = User.query(User.name == request.playerOne).get()
      if not playerOne:
          raise endpoints.NotFoundException(
            'A User with that name does not exist!')
      playerTwo = User.query(User.name == request.playerTwo).get()
      if not playerTwo:
          raise endpoints.NotFoundException(
            'A User with that name does not exist!')
      if not request.rounds:
        game = Game.new_game(playerOne.key, 
                             playerTwo.key
                            )
      else:
        game = Game.new_game(playerOne.key, 
                             playerTwo.key, 
                             request.rounds
                            )
      # Use a task queue to update win ratio/player stats.
      # This operation is not needed to complete the creation of a new game
      # so it is performed out of sequence.
      taskqueue.add(url='/tasks/cache_user_stats')
      return game.to_form("Game Successfully Created!")

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the history of the game if completed"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.over:
          txt = "Player {} played {}. Player {} played {}. End Result:  {}" \
                  .format(game.playerOne.get().name, 
                          game.playerOne_command, 
                          game.playerTwo.get().name, 
                          game.playerTwo_command,
                          game.result)
        elif game.cancelled:
          txt = "Game was cancelled"
        else:
          txt = "Game still in progress!"
        return StringMessage(message = txt)

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel the game if not complete"""
        game = get_by_urlsafe (
               request.urlsafe_game_key, 
               Game
               )

        if not game:
            raise endpoints.NotFoundException('Game could not be found!')

        if game.over:
            raise endpoints.BadRequestException('Cannot cancel a completed game!')
        game.cancelled = True            
        game.over = True
        game.result = 'cancelled'
        game.put()
        return game.to_form("Game Cancelled, Good luck with other games!")
    
    @endpoints.method(request_message=SELECT_COMMAND_REQUEST,
                      response_message = GameForm,
                      path = 'game/make_move',
                      name = 'make_move',
                      http_method = 'PUT')
    def make_move(self, request):
        """User makes a move"""
        game = get_by_urlsafe(
               request.urlsafe_key, 
               Game
               )

        if not game:
            raise endpoints.NotFoundException('Game could not be found!')

        if game.over:
            raise endpoints.BadRequestException('Can not play a game that\'s completed or cancelled')

        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        # Find the commands for user
        command_list = 0
        if game.playerOne == user.key:
            command_list = 1
        else:
            if game.playerTwo == user.key:
                command_list = 2
            else:
                raise endpoints.NotFoundException('User ' + request.user_name +' is not a playing in this match!')
        # To avoid errors, always lowercase commands
        command = request.command.lower()

        if command in COMMANDS:
            if command_list == 1:
                if len(game.playerOne_command) < game.rounds:
                  game.playerOne_command.append(command)
                  txt = "Command Successful"
                else:
                  txt = "Your turn is over"
            if command_list == 2:
                if len(game.playerTwo_command) < game.rounds:
                  game.playerTwo_command.append(command)
                  txt = "Command Successful"
                else:
                  txt = "Your turn is over"
            # make move in game
            game.makeMove()
            game.put()
        else:
          raise endpoints.BadRequestException('Please select a valid command!')

        return game.to_form(txt)

    

api = endpoints.api_server([roshamboAPI])
