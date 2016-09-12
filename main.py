#!/usr/bin/env python
"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging
from api import roshamboAPI

import webapp2
from google.appengine.api import mail, app_identity

from models import User


class SendEmailReminderHandler(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        send_email = False
        for user in users:
            games = Game.query(
                    ndb.AND(
                    Game.game_over == False, 
                    ndb.OR(Game.playerOne == user.key, 
                           Game.playerTwo == user.key
                          )
                        )
                    )
            for game in games:
                if game.playerOne == user.key:
                    if len(game.player_one_weapons) < game.total_rounds:
                        send_email = True
                        break
                else:
                    if len(game.player_two_weapons) < game.total_rounds:
                        send_email = True
                        break
            if send_email:
                subject = 'We Miss You @ RoshamboAPI'
                body = 'Hello {}, you have an unfinished round at RoshamboAPI, come back?'.format(user.name)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

# Sends a user an email when they create a User
class SendUserEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email upon User Creation"""
        user = get_by_urlsafe(self.request.get('playerOne'), User)
        subject = 'Welcome!'
        body = "Welcome to Roshambo!"
        logging.debug(body)
        mail.send_mail('noreply@{}.appspotmail.com'.
                       format(app_identity.get_application_id()),
                       user.email,
                       subject,
                       body)


class CacheUserStats(webapp2.RequestHandler):
    def post(self):
        """Update user stats in memcache."""
        roshamboAPI._cache_user_stats()
        self.response.set_status(204)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendEmailReminderHandler),
    ('/tasks/send_welcome_email', SendUserEmail),
    ('/tasks/cache_user_stats', CacheUserStats),

], debug=True)
