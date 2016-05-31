from flask import Flask
from Corridor import Board,Player
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

#I just want to be able to manipulate the parameters
@app.route('/get_board', methods=['GET'])
def get_board():
    b = Board(9,[Player((4,8),8,('h',0)),
                 Player((4,0),8,('h',8))])
    return b
#username = request.args.get('username')
    #password = request.args.get('password')

if __name__ == "__main__":
    app.run()
