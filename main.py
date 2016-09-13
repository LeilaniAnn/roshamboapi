#!/usr/bin/env python
"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging
from api import roshamboAPI

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb

from models.User import User
from models.Game import Game


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
                    Game.over == False, 
                    ndb.OR(Game.playerOne == user.key, 
                           Game.playerTwo == user.key
                          )
                        )
                    )
            for game in games:
                if game.playerOne == user.key:
                    if len(game.playerOne_command) < game.rounds:
                        send_email = True
                        break
                else:
                    if len(game.playerTwo_command) < game.rounds:
                        send_email = True
                        break
            if send_email:
                subject = 'We Miss You @ RoshamboAPI'
                body = 'Hello {}, you have an unfinished round at RoshamboAPI, come back?'.format(user.name)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
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
    ('/tasks/cache_user_stats', CacheUserStats),

], debug=True)
