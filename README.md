# corridor
# Customer Feedback


# TODO

Game Libary:
- Return: shortest paths (UI feature to highlight)
- Return: move list
- New Method: get_valid_moves(player)
  - Any valid move in search with depth == num_players

Flask Application:
- Identity management via cookie
- Persistence via Redis
  - Append for move list
- Assign unique key for new games

Web Application (HTML/CSS):
- Responsive UI: phone compatible
  - Scale board to screen size for phone
- Errors into a status message
- Better indiation of winner and game stoppage.
- Polling
  - Start polling any time it isn't players turn
  - stop polling when game ends
  - Keep polling when it is my move? (to maintain active state?)
  - dont' poll when I'm playing the computer
- Ability to change name
- Highlight active player name and game piece
- Ghost for valid moves
- put player number in url immediately
- put if computer player in url
- detect if opponent online via polling
- put configuration on git
- Display moves list (low)
- Matchmaking
  - public vs. private
  - first in gets Player 1
  - next gets Player 2, game starts
  - If no parter yet, player can switch sides
  - If no parter yet, player can start with computer
  - Additional players in observer mode

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


