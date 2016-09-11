# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models.User import User, UserForm, UserForms
from models.Game import Game, NewGameForm, GameForm, GameForms
from models.Rank import StringMessage, RankForm, RankForms
from utils import get_by_urlsafe

import heapq

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
GET_USER_GAMES = endpoints.ResourceContainer(
        user_name=messages.StringField(1),)
GET_ALL_USERS = endpoints.ResourceContainer()
GET_USER_RANKINGS = endpoints.ResourceContainer()
GET_ALL_GAMES = endpoints.ResourceContainer()
GET_HIGH_SCORES= endpoints.ResourceContainer()
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


high_scores = []

@endpoints.api(name='roshambo', version='v1')
class roshamboAPI(remote.Service):
    """Game API"""
    
    def _returnResult(self, game):
        if game.result == 'draw':
            return game.to_form('You played Roshambo with Lizard and Spock! You played {}, your opponent played {}. You reach a draw!'.format(game.playerCommand, game.opponentCommand))
        elif game.result == 'win':
            return game.to_form('You played Roshambo with Lizard and Spock! You played {}, your opponent played {}. You win!'.format(game.playerCommand, game.opponentCommand))
        elif game.result == 'cancelled':
            return game.to_form('Game successfully cancelled, you neither lose nor win')
        else:
            return game.to_form('You played Roshambo with Lizard and Spock! You played {}, your opponent played {}. Sorry, You Lose!'.format(game.playerCommand, game.opponentCommand))
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
        user = User(name=request.user_name, email=request.email)
        user.put()
        # Send Welcome email.
        taskqueue.add(url='/tasks/send_welcome_email',
                      params={'user_key': user.key})
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game of Roshambo + Lizard + Spock. Command = cancel to cancel game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.playerCommand)
        except ValueError:
            raise endpoints.BadRequestException('Please make a valid choice: Rock, Paper, Scissors, Lizard, Spock')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(params={'user_name': user.name,
                              'result': game.result},
            url='/tasks/update_user_score')
        return self._returnResult(game)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return self._returnResult(game)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_ALL_USERS,
                      response_message=UserForms,
                      path='allusers',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Return all user information"""
        return UserForms(items=[user.to_form() for user in User.query()])
        
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserForm,
                      path='record/{user_name}',
                      name='get_user_record',
                      http_method='GET')
    def get_user_record(self, request):
        """Return the record of one user."""
        user = User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('User' + '"' + request.user_name+ '"' + 'Not found!')
        return user.to_form()
        
    @endpoints.method(request_message=GET_ALL_GAMES,
                      response_message=GameForms,
                      path='allgames',
                      name='get_all_games',
                      http_method='GET')
    
    def get_all_games(self, request):
        """Return game history for all users/games"""
        return GameForms(items=[game.to_form('') for game in Game.query()])
    
    @endpoints.method(request_message=GET_USER_GAMES,
                      response_message=GameForms,
                      path='games/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all the game history of one user."""
        user = User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with {} does not exist!'.format(request.user_name))
        games = Game.query(Game.user==user.key)
        return GameForms(items=[game.to_form('') for game in games])
    
    @endpoints.method(request_message=GET_USER_RANKINGS,
                      response_message=RankForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns all users and their win ratio"""
        return RankForms(items=[user.to_rank_form() for user in User.query().order(-User.win_ratio)])
    
    @endpoints.method(request_message=GET_USER_RANKINGS,
                      response_message=RankForms,
                      path='highScores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """ Return top 5 high scores """
        return RankForms(items=[user.to_rank_form() for user in User.query().order(-User.win_ratio).fetch(limit=5)])
    
        
api = endpoints.api_server([roshamboAPI])