# corridor

# TODO

Game Libary:
- Return: current player (only increment on valid move)
- Return: status: not_started, active, complete
- Return: shortest paths (UI feature to highlight)
- Return: move list
- New Method: get_valid_moves(player)
  - Any valid move in search with depth == num_players
- Bug: Computer can't hop player
- Bug: Valid wall method can't hop player

Flask Application:
- Identity management via cookie
- Persistence via Redis
- Assign unique key for new games

Web Application (HTML/CSS):
- Responsive UI: phone compatible
  - Scale board to screen size for phone
- Number of walls in wall type selector
- Ability to change name
- Highlight active player name and game piece
- Ghost for valid moves
- Display moves list
- Matchmaking
  - Share via url with key
  - public vs. private
  - first in gets Player 1
  - next gets Player 2, game starts
  - If no parter yet, player can switch sides
  - If no parter yet, player can start with computer
  - Additional players in observer mode
- Mechanism for polling or notifications to client

Overall:
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


