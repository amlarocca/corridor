import flask
import json
import sys
from flask import Flask,render_template, request, jsonify
from Corridor import Board,Player
from CorridorBot import CorridorBot
app = Flask(__name__)
app.debug = True
@app.route("/")
def hello():
    return "Hello World!"

def build_response(board):
    response = {}
    response['players'] = [{'position':player.position,'walls':player.walls,'goal':player.goal} for player in board.players]
    response['walls_v'] = list(board.walls['v'])
    response['walls_h'] = list(board.walls['h'])
    print response['players']
    return flask.jsonify(response)

#I just want to be able to manipulate the parameters
@app.route('/get_board', methods=['GET'])
def get_board():
    b = Board(9,[Player((4,0),8,('h',8)),
                 Player((4,8),8,('h',0))])
    return build_response(b)

if __name__ == "__main__":
    app.run()


@app.route('/make_move', methods=['POST'])
def make_move():
    # Get the parsed contents of the form data
    board = request.json['board']
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    b = Board(9,[Player(p['position'],p['walls'],p['goal']) for p in board['players']])
    b.walls['v'] = set([tuple(wall) for wall in board['walls_v']])
    b.walls['h'] = set([tuple(wall) for wall in board['walls_h']])
    print b.players[player].position,x,y
    b.move_player(player,x,y,trace=True)

    return build_response(b)

@app.route('/place_wall', methods=['POST'])
def place_wall():
    # Get the parsed contents of the form data
    board = request.json['board']
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    orientation = request.json['orientation']
    b = Board(9,[Player(p['position'],p['walls'],p['goal']) for p in board['players']])
    b.walls['v'] = set([tuple(wall) for wall in board['walls_v']])
    b.walls['h'] = set([tuple(wall) for wall in board['walls_h']])
    b.add_wall(orientation,x,y,player)

    return build_response(b)

@app.route('/bot_move', methods=['POST'])
def bot_move():
    board = request.json['board']
    player = request.json['player']
    opponent = request.json['opponent']
    move_num = request.json['move_num']
    b = Board(9,[Player(p['position'],p['walls'],p['goal']) for p in board['players']])
    b.walls['v'] = set([tuple(wall) for wall in board['walls_v']])
    b.walls['h'] = set([tuple(wall) for wall in board['walls_h']])

    #try:
    if True:
	bot = CorridorBot()
	bot.make_move(b,player,opponent,move_num,trace=False)
    #except:
    #   print(sys.exc_info())

    return build_response(b)


if __name__ == "__main__":
    app.run()

