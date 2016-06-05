# corridor
# Customer Feedback


# TODO

Web Application (HTML/CSS):
- if game_mode = not started, option to: switch sides / get a link / play computer
  - already polling at this point so game can start at any time if link joined or in "public mode"
- if game_mode = completed, don't allow moves, polling, show winner overlay, new game button
- Scale board to screen size for phone
- Errors messages glow a color and then fade
- "Place Wall or Move Piece"
- polling bug when user interacts
- Highlight active player name and game piece
- detect if opponent online via polling
- Display moves list (low)
- Ability to change name
- Matchmaking
  - public vs. private
  - first in gets Player 1
  - next gets Player 2, game starts
  - If no parter yet, player can switch sides
  - If no parter yet, player can start with computer
  - Additional players in observer mode

Flask Application:
- Identity management via cookie
- Append data structure for move list in Redis 

Overall:
- Complete code refactor
- Python version upgrade from 2.6

# Tutorial
* EC2 Instance
* Domain Name
* DNS
* Apache httpd
* mod_wsgi
* Flask App
* Game Libarary
* AI Bot
* Web Application
* Persistence Layer


