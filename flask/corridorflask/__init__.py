import flask
import json
import sys
import redis
import pickle
import time
import os,binascii
from flask import Flask,render_template, request, jsonify, abort
from Corridor import Board,Player
from CorridorBot import CorridorBot
app = Flask(__name__)
app.debug = True

r = None

@app.route("/")
def hello():
    return "Hello World!"

def build_response(game_id,board,write=True):
    if not board.timestamp:
        print('board has no timestamp')
        write_board_to_redis(game_id,board)
    elif write:        
        write_board_to_redis(game_id,board)
    response = {}
    response['game_id'] = game_id
    response['players'] = [{'position':player.position,'walls':player.walls,'goal':player.goal} for player in board.players]
    response['walls_v'] = list(board.walls['v'])
    response['walls_h'] = list(board.walls['h'])
    response['current_player'] = board.current_player
    response['winner'] = ''
    response['timestamp'] = board.timestamp
    response['valid_moves'] = board.get_valid_moves(board.current_player)
    for player in range(len(board.players)):
        if board.check_player_goal_status(player):
            response['winner'] = player
            board.status = "completed"
    response['status'] = board.status
    return flask.jsonify(response)

@app.route('/get_board', methods=['GET'])
def get_board():
    game_id = request.args.get('game_id')
    try:        
        if game_id and game_id != '':
            b = get_board_from_redis(game_id)
        else:
            game_id = get_game_id()
            b = build_board()
    except:
        abort(400,str(sys.exc_info())) 
    return build_response(game_id,b,write=False)

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

def get_redis():
    global r
    if r is None:
        r = redis.StrictRedis(host='127.0.0.1', port=6379)
        print 'Connected to redis:',r.client_list()
    return r
    
def get_game_id():
    return binascii.b2a_hex(os.urandom(15))
    
def write_board_to_redis(game_id,board):
    timestamp = time.time()
    board.timestamp = timestamp
    return get_redis().set(game_id,pickle.dumps(board))
    
def get_board_from_redis(game_id):
    print 'Getting game from redis with key',game_id
    pickled_board = str(get_redis().get(game_id))
    #print pickled_board
    board = pickle.loads(pickled_board)
    return board

@app.route('/make_move', methods=['POST'])
def make_move():
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    game_id = request.json['game_id']
    try:        
        if game_id:
            b = get_board_from_redis(game_id)
        else:
            game_id = get_game_id()
            b = build_board(request.json['board'])
        b.move_player(player,x,y,trace=True)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()[1]))
    return build_response(game_id,b)

@app.route('/place_wall', methods=['POST'])
def place_wall():
    x = request.json['x']
    y = request.json['y']
    player = request.json['player']
    orientation = request.json['orientation']
    game_id = request.json['game_id']
    try:        
        if game_id:
            b = get_board_from_redis(game_id)
        else:
            game_id = get_game_id()
            b = build_board(request.json['board'])
        b.add_wall(orientation,x,y,player)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()[1]))

    return build_response(game_id,b)

@app.route('/bot_move', methods=['POST'])
def bot_move():
    player = request.json['player']
    opponent = request.json['opponent']
    move_num = request.json['move_num']
    game_id = request.json['game_id']
    try:        
        if game_id:
            b = get_board_from_redis(game_id)
        else:
            game_id = get_game_id()
            b = build_board(request.json['board'])
        bot = CorridorBot()
        bot.make_move(b,player,opponent,move_num,trace=True)
        b.status = "active"
    except:
        abort(400,str(sys.exc_info()))
    return build_response(game_id,b)

@app.errorhandler(400)
def custom400(error):
    response = jsonify({'message': error.description})
    return response,400

if __name__ == "__main__":
    app.run()

