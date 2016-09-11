##PROJECT SPECIFICATION : Design A Game

##API Architecture
| Criteria | Meets Specifications | 
| ------------- |:-------------:|
| Is the project architected as a ```Web Service API``` using ```Google App Engine```? | Project is architected as a Web Service API using Google App Engine. |

## API Implementation

| Criteria | Meets Specifications | 
| ------------- |:-------------:|
| Is a new type of game implemented with additional features? | A new type of game is implemented with additional game logic or features (such as 2-player games). The new game is not a copy of Guess a Number, such as Guess a Date. If it is a guessing game like Hangman, additional features are included (partial reveal of the solution over time).
| Are illegal moves handled gracefully? | "Illegal" moves are handled gracefully by the ```API```. For example, if implementing ```Tic-Tac-Toe```, if a ```User``` tries to play a square that has already been filled - the server will respond with an error message explaining that the move is illegal. There should be no 'Internal Server Errors' so long as ```User``` input is otherwise properly formed. |

## Resource Containers
| Criteria | Meets Specifications | 
| ------------- |:-------------:|
| Do ```endpoints``` make use of appropriate ```Resource Containers?``` | All ````endpoints``` make use of sensible ```Resource Containers```.


## New Endpoints Created
| Criteria | Meets Specifications | 
| ------------- |:-------------:|
| Is ```get_user_games``` endpoint is implemented properly? | ```get_user_games``` is implemented as specified by Task 3 in the project description.
| Is ```cancel_game``` endpoint is implemented properly? | ```cancel_game``` is implemented as specified by Task 3 in the project description. |
| Is get_high_scores endpoint is implemented properly? | ```get_high_scores``` is implemented as specified by Task 3 in the project description.
| Is ```get_user_rankings``` endpoint is implemented properly? | ```get_user_rankings``` is implemented as specified by Task 3 in the project description. |
| Is ```get_game_history endpoint``` is implemented properly? | ```get_game_history``` is implemented as specified by Task 3 in the project description.|

## Appropriate use of HTTP Methods
| Criteria | Meets Specifications | 
| ------------- |:-------------:|
| Do ```additional endpoints``` make use of appropriate ```HTTP methods```? | Additional ```endpoints``` make use of appropriate ```HTTP methods```. Meaning ```GET``` only reads, and ```Post``` writes to ```Datastore``` |

Task Queues

CRITERIA
MEETS SPECIFICATIONS
Does the email reminder cronjob handler only notify Users needing a reminder?

The email reminder cronjob handler is modified so that only Users 'needing' a reminder (actual logic up to the student) is modified.

Code Readability

##CRITERIA
##MEETS SPECIFICATIONS
Are comments present and do they effectively explain longer code procedures?

Comments are present and effectively explain longer code procedures.

Documentation

CRITERIA
MEETS SPECIFICATIONS
Is the new game documented in a README.md file?

The new game is documented in a README.md file, with explanation of the rules and score-keeping.

Is the API documented in a README.md file?

The API is documented in a README.md file so that users can understand how to use the API without reading the source code.

Did the student reflect on their design decisions in a text file?

The student has meaningfully reflected on their design decisions and recorded their reflections in a text file (preferably named Design.txt).

Suggestions to Make Your Project Stand Out!
Design a front end for your game.
Implement OAuth so that a user would have to sign in to play the game(you can play around with how you want to decide the permissions a user would have in your game).
 English 
