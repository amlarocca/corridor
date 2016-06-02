import flask
import json
import sys
import redis
import pickle
from flask import Flask,render_template, request, jsonify, abort
from Corridor import Board,Player
from CorridorBot import CorridorBot
app = Flask(__name__)
app.debug = True

@app.route("/")
def hello():
    return "Hello World!"

def build_response(game_id,board):
    write_board_to_redis(game_id,board)
    response = {}
    response['game_id'] = game_id
    response['players'] = [{'position':player.position,'walls':player.walls,'goal':player.goal} for player in board.players]
    response['walls_v'] = list(board.walls['v'])
    response['walls_h'] = list(board.walls['h'])
    response['current_player'] = board.current_player
    response['winner'] = ''
    for player in range(len(board.players)):
        if board.check_player_goal_status(player):
            response['winner'] = player
            board.status = "completed"
    response['status'] = board.status
    return flask.jsonify(response)

@app.route('/get_board', methods=['GET'])
def get_board():
    return build_response(build_board())

def build_board(board=None):
    if not board:
        b = Board(9,[Player((4,8),8,('h',0)),
                     Player((4,0),8,('h',8))])
    else:
        b = Board(9,[Player(p['position'],p['walls'],p['goal']) for p in board['players']])
        b.walls['v'] = set([tuple(wall) for wall in board['walls_v']])
        b.walls['h'] = set([tuple(wall) for wall in board['walls_h']])
        b.current_player = board['current_player']
        b.status = board['status']
    return b

def write_board_to_redis(board,game_id):
    return pickle.dumps(r.set(game_id,board))
    
def get_board_from_redis(game_id):
    return pickle.loads(r.get(game_id))

@app.route('/make_move', methods=['POST'])
def make_move():
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    try:
        board_key = request.json['game_id']
        if board_key:
            b = get_board_from_redis(board_key)
        else:
            b = build_board(request.json['board'])
        b.move_player(player,x,y,trace=True)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()[1]))
    return build_response(b)

@app.route('/place_wall', methods=['POST'])
def place_wall():
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    orientation = request.json['orientation']
    try:
        board_key = request.json['game_id']
        if board_key:
            b = get_board_from_redis(board_key)
        else:
            b = build_board(request.json['board'])
        b = build_board(request.json['board'])
        b.add_wall(orientation,x,y,player)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()[1]))

    return build_response(b)

@app.route('/bot_move', methods=['POST'])
def bot_move():
    player = request.json['player']
    opponent = request.json['opponent']
    move_num = request.json['move_num']
    try:
        board_key = request.json['game_id']
        if board_key:
            b = get_board_from_redis(board_key)
        else:
            b = build_board(request.json['board'])
        bot = CorridorBot()
        bot.make_move(b,player,opponent,move_num,trace=False)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()[1]))
    return build_response(b)

@app.errorhandler(400)
def custom400(error):
    response = jsonify({'message': error.description})
    return response,400

if __name__ == "__main__":
    r = redis.StrictRedis(host='127.0.0.1', port=6379)
    app.run()

