#Full Stack Nanodegree Game Endpoints API - Roshambo featuring Lizard and Spock

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
 You could also add any front end to this application.
 
 
 
##Game Description:

Rock–paper–scissors is a zero-sum hand game usually played between two people, in which each player simultaneously forms one of three shapes with an outstretched hand. These shapes are "rock" (✊ a simple fist), "paper" (✋ a flat hand), and "scissors" (✌️ a fist with the index and middle fingers together forming a V). The game has only three possible outcomes other than a tie: a player who decides to play rock will beat another player who has chosen scissors ("rock crushes scissors") but will lose to one who has played paper ("paper covers rock"); a play of paper will lose to a play of scissors ("scissors cut paper"). If both players choose the same shape, the game is tied and is usually immediately replayed to break the tie. Other names for the game in the English-speaking world include roshambo and other orderings of the three items, sometimes with "rock" being called "stone".

One popular five-weapon expansion is "rock-paper-scissors-Spock-lizard", invented by Sam Kass and Karen Bryla,[82] which adds "Spock" and "lizard" to the standard three choices. "Spock" is signified with the Star Trek Vulcan salute, while "lizard" is shown by forming the hand into a sock-puppet-like mouth. Spock smashes scissors and vaporizes rock; he is poisoned by lizard and disproven by paper. Lizard poisons Spock and eats paper; it is crushed by rock and decapitated by scissors. This variant was mentioned in a 2005 article in The Times of London[83] and was later the subject of an episode of the American sitcom The Big Bang Theory in 2008 (as rock-paper-scissors-lizard-Spock).[84]

(https://en.wikipedia.org/wiki/Rock–paper–scissors)
 
While in game, a game can be created with 2 players and any number of rounds. The player (you) will choose a command of "rock", "paper", "scissors", "lizard", "spock" and the opponent player (also you) will also pick a command. The result is displayed immediately . Each game can be retrieved by its id using the path parameter `urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - /models/ user, game, rank: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: playerOne, playerTwo, rounds
    - Returns: GameForm with game result.
    - Description: Creates a new Game with 2 players (playerOne and playerTwo) with a number of rounds. 
 - **make_move**
    - Path: 'game/make_move'
    - Method: PUT
    - Parameters: urlsafe_game_key, command, user_name
    - Returns: GameForm with game result
    - Description: game with certain # rounds (accoring to player). user_name provided must correspond to an existing user - will raise a NotFoundException if not. Valid commands are "rock", "paper", "scissors", "lizard", "spock", or "cancel". Will raise BadRequestException otherwise. The API will randomly generate a command as an opponent. The result will be returned as a GameForm. The user record of 'wins', 'loses', 'games' and 'win_ratio' are updated.

 - **get_user_games**
    - Path: 'game/get_by_user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms of a specific user.
    - Description: Returns GameForms of a specific user.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: RankForms of all users ordered by win_ratio.
    - Description: Returns RankForms of all users ordered by win_ratio.
    
 - **get_user_stats**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: RankForms of all users ordered by win_ratio.
    - Description: Returns RankForms of all users ordered by win_ratio.
    
 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage of all completed games and results.
    - Description: Returns history of completed games - players and results
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm of cancelled game completion.
    - Description: Cancels a game- unless game is completed


    
##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

- **Rank**
    - Records completed game stats.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game (urlsafe_key, playerOne_name, playerTwo_name, message).
 - **NewGameForm**
    - Used to create a new game (user_name, player_form)
 - **GameForms**
    - Multiple GameForm container.    
 - **UserForm** 	
    - Representation of a User's information(user_name, win_ratio, games played, wins, losses)
 - **UserForms**
    - Multiple UserForm container.
 - **RankForm**
    - Representation of a User's ranking record (user_name, win_ratio)
  - **RankForms**
    - Multiple RankForm container.
 - **StringMessage**
    - General purpose String container.

## Creator

**Leilani Raranga**

* <https://twitter.com/leilanirar>
* <https://github.com/leilaniann>


## Copyright and license

Copyright © 2016, [Leilani Raranga](http://github.com/leilaniann). Released under the [MIT license](https://github.com/helpers/helper-copyright/blob/master/LICENSE).
