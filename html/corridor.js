//
// Bugs:
// 1. Game thinks I am blocking opponent from winning (search for longer paths?
// should be same search as computer does when evaluating.

var size = 9
var cell_width = 30
var wall_width = 10
var current_board = {}
var move_num = 1

window.addEvent("domready", initializeBoard);

var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("get", url, true);
    xhr.responseType = "json";
    xhr.onload = function() {
      var status = xhr.status;
      if (status == 200) {
        callback(null, xhr.response);
      } else {
        callback(status,xhr.response);
      }
    };
    xhr.send();
};

var postJSON = function(url,body,callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.onload = function () {
      var status = xhr.status;
      if (status == 200) {
        callback(null, xhr.response);
      } else {
        callback(status,JSON.parse(xhr.response).message);
      }
    };
    xhr.send(JSON.stringify(body));
};
function initializeBoard(board)
{
    getJSON("http://tools.zensky.com/corridor/get_board",
    function(err, data) {
          if (err != null) {
            alert("Something went wrong: " + err);
          } else {
            //alert("Your query count: " + data.players);
            renderBoard(data)
            current_board = data
        }
    });
}

function botMove()
{
    data = {}
    data.board = current_board
    data.player = 1
    data.opponent = 0
    data.move_num = move_num
    postJSON("http://tools.zensky.com/corridor/bot_move",data,
      function(err, data2) {
          if (err != null) {
               alert(data2);
          } else {
              board = JSON.parse(data2)
              renderBoard(board)
              current_board = board
              move_num += 1
        }
    });
}

function makeMove(board,x,y)
{
    data = {}
    data.board = board
    data.x = x
    data.y = y
    data.player = 0
    postJSON("http://tools.zensky.com/corridor/make_move",data,
      function(err, data2) {
          if (err != null) {
               alert(data2);
          } else {
              board = JSON.parse(data2)
              renderBoard(board)
              current_board = board
              move_num += 1
              botMove()
        }
    });
}

function placeWall(board,orientation, x,y)
{
    data = {}
    data.board = board
    data.x = x
    data.y = y
    data.player = 0
    data.orientation = orientation
    postJSON("http://tools.zensky.com/corridor/place_wall",data,
      function(err, data2) {
          if (err != null) {
               alert(data2);
          } else {
              board = JSON.parse(data2)
              renderBoard(board)
              current_board = board
              move_num += 1
              botMove()
        }
    });
}
function boardClicked(event) {
    var elem = document.getElementById('corridor')
    var elemLeft = elem.offsetLeft
    var elemTop = elem.offsetTop
    var x = event.pageX - elemLeft
    var y = event.pageY - elemTop
    
    var moveType = document.getElementById("moveType");
    console.log(moveType.value)
    
    // cells are 30 and walls are 10 and come together,
    // divide by the combined width then determine which wall
    click_x = Math.floor(x / (cell_width + wall_width))
    wall_x = false
    if (x % (cell_width + wall_width) > cell_width) {
        wall_x = true
    }
    click_y = Math.floor(y / (cell_width + wall_width))
    wall_y = false
    if (y % (cell_width + wall_width) > cell_width) {
        wall_y = true
    }
    if (!wall_x & !wall_y & moveType.value == "move") {
        //alert('move piece: (' + click_x + ',' + click_y + ')')
        makeMove(current_board,click_x,click_y)
    } else if (wall_x & wall_y) {
        //alert('place wall: (' + click_x + ',' + click_y + ')')
        if (moveType.value == "h_wall") {
            placeWall(current_board,"h",click_x,click_y)
        } else if (moveType.value == "v_wall"){        
            placeWall(current_board,"v",click_x,click_y)
        }
    }

}
function renderBoard(board)
{ 
    var canvas = document.getElementById("corridor");
    canvas.addEventListener('click', boardClicked, false);
    var context2D = canvas.getContext("2d");

    var cells = (size * 2) - 1
    var row_offset = 0
    for (var row = 0; row < cells; row ++)
    {
        // if row is even, this is a cell, else it is a wall
        var height = wall_width
        if (row % 2 == 0) {
              height = cell_width
        }
        var col_offset = 0
        for (var column = 0; column < cells; column ++)
        {
            var width = wall_width
            if (column % 2 == 0) {
                  width = cell_width
            }
      
              // We'll use black unless there is a wall
            context2D.fillStyle = "black";    
            for (var wall = 0; wall < board.walls_h.length; wall++) {
                  pos = board.walls_h[wall]
                if ((row - 1)/ 2 == pos[1] && column  >= 2*pos[0] && column <= 2*pos[0]+2)
                {
                    context2D.fillStyle = "white";
                }
            }
            for (var wall = 0; wall < board.walls_v.length; wall++) {
                pos = board.walls_v[wall]
                if ((column - 1) / 2 == pos[0] && row >=2*pos[1] && row <= 2*pos[1]+2) {
                    context2D.fillStyle = "white";
                }
            }
            context2D.fillRect(col_offset, row_offset, width-1,height-1);
      
      
            for (var player = 0; player < board.players.length; player++)
            {
                pos = board.players[player].position
                if (column / 2 == pos[0] && row / 2 == pos[1])
                {
                    context2D.beginPath();
                    context2D.arc(col_offset + (width/2), row_offset + (height/2), (width/2)-2, 0, 2 * Math.PI, false);
                    if (player == 0) { context2D.fillStyle = 'white'; };
                    if (player == 1) { context2D.fillStyle = 'grey'; };
                    context2D.fill();
                    context2D.lineWidth = 1;
                    context2D.strokeStyle = '#003300';
                    context2D.stroke();
                }
            }
      
            col_offset = col_offset + width;
        }
        
        row_offset = row_offset + height;
    }
    document.getElementById("p1_walls").textContent=board.players[0].walls;
    document.getElementById("p2_walls").textContent=board.players[1].walls;
    if (board.winner != "") {
        alert("Player " + (board.winner + 1) + " Wins!")
    }
}
