//
// Bugs:
// 1. Game thinks I am blocking opponent from winning (search for longer paths?
// should be same search as computer does when evaluating.

var size = 9
var cell_width = 33
var wall_width = 11
var current_board = {}
var move_num = 1
var wall_type = "H"
var player_number = 0
var botDelay = 500
var play_computer = false
var api_url = "http://corridor.zensky.com/corridor/"

window.onload = initializeBoard;

function playComputer(checkbox)
{
    play_computer = checkbox.checked
    var new_uri = updateQueryStringParameter(window.location.href,'play_computer',play_computer);
    window.location.href = new_uri;
    //botMove()
}

function updateStatus(message) {
    document.getElementById("statusMessage").textContent=message;
        
}

function updateQueryStringParameter(uri, key, value) {
  var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
  var separator = uri.indexOf('?') !== -1 ? "&" : "?";
  var new_uri;
  if (uri.match(re)) {
    new_uri = uri.replace(re, '$1' + key + "=" + value + '$2');
  }
  else {
    new_uri = uri + separator + key + "=" + value;
  }
  return new_uri
}

function getParameterByName(name) {
    var url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return '';
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function initializeBoard()
{
    var wallselector = document.getElementById('wallselector');

    wallselector.style.cursor = 'pointer';
    wallselector.onclick = function() {
        if (wall_type == "H") {
          wall_type = "V";
        } else if (wall_type == "V") {
          wall_type = "H"
        }
        renderWallSelector();
    };
    
    var startOver = document.getElementById('startOver');
    startOver.style.cursor = 'pointer';
    startOver.onclick = function() {setupBoard(true);};
    
    var switchSides = document.getElementById('switchSides');
    switchSides.style.cursor = 'pointer';
    switchSides.onclick = function() {
        player_number = (player_number + 1) % 2
        var new_uri = updateQueryStringParameter(window.location.href,'player_number',player_number);
        window.location.href = new_uri;
    };
    
    setupBoard(false);
}


function setupBoard(reset)
{
    // get game_id from url, if available
    // get player_number from url, if available
    url = api_url + "get_board"
    game_id = getParameterByName('game_id')
    if (!reset & game_id != '') {
        url = updateQueryStringParameter(url,"game_id",game_id)
    }
    player_number_url = getParameterByName('player_number')
    if (player_number_url != '') {
        player_number = parseInt(player_number_url)
    }
    play_computer_url = getParameterByName('play_computer')
    if (play_computer_url != '') {
        play_computer = (play_computer_url == "true")
        document.getElementById("play_computer").checked = play_computer;
    }
    getJSON(url,
    function(err, data) {
          if (err != null) {
            updateStatus("Something went wrong: " + err);
          } else {
            //alert("Your query count: " + data.players);
            if (!game_id || reset || !player_number_url) {
                console.log('updating query string')
                current_uri = window.location.href
                current_uri = updateQueryStringParameter(current_uri,'game_id',data.game_id);
                current_uri = updateQueryStringParameter(current_uri,'player_number',player_number);
                current_uri = updateQueryStringParameter(current_uri,'play_computer',play_computer);
                window.location.href = current_uri
            } else {
                current_board = data
                renderBoard()
                if (current_board.current_player != player_number)
                    botMove()
            }
        }
    });
}

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

function poll(fn, callback, errback, timeout, interval) {
    var endTime = Number(new Date()) + (timeout || 300000);
    interval = interval || 5000;

    (function p() {
            // If the condition is met, we're done! 
            if(fn()) {
                callback();
            }
            // If the condition isn't met but the timeout hasn't elapsed, go again
            else if (Number(new Date()) < endTime) {
                setTimeout(p, interval);
            }
            // Didn't match and too much time, reject!
            else {
                //errback(new Error('timed out for ' + fn + ': ' + arguments));
                errback();
            }
    })();
}

// Usage:  ensure element is visible
already_polling = false;
board_changed = false;
function wait_for_opponent_move() {
    console.log('called wait_for_opponent_move, already polling:' + already_polling)
    if (!already_polling & current_game.status != "completed") {
        already_polling = true;
        board_changed = false;
        poll(
            function() {
                if (!board_changed) {
                    url = api_url + "get_board"
                    game_id = getParameterByName('game_id')
                    url = updateQueryStringParameter(url,"game_id",game_id)
                    getJSON(url,
                        function(err, data) {
                        if (err != null) {
                            updateStatus("Something went wrong: " + err);
                        } else if (data.timestamp != current_board.timestamp) {
                            console.log('the board changed!' + data.timestamp + ' different from ' + current_board.timestamp)
                            current_board = data;
                            board_changed = true;
                            renderBoard();
                        }}
                    );
                }
                return board_changed;
            },
            function() {
                console.log('in callback for wait_for_opponent_move, unsetting polling flag')
                already_polling = false;
            },
            function() {
                console.log('error callback')
                already_polling = false;
                // Error, failure callback
            }
        );
    }
}


function botMove()
{
    if (current_board.current_player != player_number) {
        if (play_computer) {
            updateStatus("Player " + (current_board.current_player + 1) + " Thinking...")
            data = {}
            //data.board = current_board
            data.game_id = current_board.game_id
            data.player = (player_number + 1) % 2
            data.opponent = player_number
            data.move_num = move_num
            postJSON(api_url + "bot_move",data, function(err, data2) {
                if (err != null) {
                    updateStatus(data2);
                } else {
                    setTimeout(function() { 
                        board = JSON.parse(data2)
                        current_board = board
                        renderBoard()
                        move_num += 1
                    }, botDelay); 
                }
            });
        } else {    
            wait_for_opponent_move()        
        }
    }
}

function makeMove(board,x,y)
{
    data = {}
    //data.board = board
    data.game_id = current_board.game_id
    data.x = x
    data.y = y
    data.player = player_number
    postJSON(api_url + "make_move",data,
      function(err, data2) {
          if (err != null) {
               updateStatus(data2);
          } else {
              board = JSON.parse(data2)
              current_board = board
              renderBoard()
              move_num += 1
              botMove()
        }
    });
}

function placeWall(orientation, x,y)
{
    data = {}
    //data.board = board
    data.game_id = current_board.game_id;
    data.x = x;
    data.y = y;
    data.player = player_number
    data.orientation = orientation
    postJSON(api_url + "place_wall",data,
      function(err, data2) {
          if (err != null) {
               updateStatus(data2);
          } else {
              board = JSON.parse(data2)
              current_board = board
              renderBoard()
              move_num += 1
              botMove()
        }
    });
}
function boardClicked(event) {
    if (current_board.current_player != player_number) {
        updateStatus('Not your turn fool!');
    } else {
        
        var elem = document.getElementById('corridor')
        var elemLeft = elem.offsetLeft
        var elemTop = elem.offsetTop
        var x = event.pageX - elemLeft
        var y = event.pageY - elemTop
    
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
        if (!wall_x & !wall_y) {
            //alert('move piece: (' + click_x + ',' + click_y + ')')
            makeMove(current_board,click_x,click_y)
        } else if (wall_x & wall_y) {
            //alert('place wall: (' + click_x + ',' + click_y + ')')
            if (wall_type == "H") {
                placeWall("h",click_x,click_y)
            } else if (wall_type == "V"){        
                placeWall("v",click_x,click_y)
            }
        }
    }
}

function renderBoard()
{ 
    console.log('Rendering board with timestamp: ', current_board.timestamp)
    var canvas = document.getElementById("corridor");
    var totalWidth = size * cell_width + (size -1) * wall_width
    canvas.setAttribute('width', totalWidth);
    canvas.setAttribute('height', totalWidth);
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
            for (var wall = 0; wall < current_board.walls_h.length; wall++) {
                pos = current_board.walls_h[wall]
                if ((row - 1)/ 2 == pos[1] && column  >= 2*pos[0] && column <= 2*pos[0]+2)
                {
                    context2D.fillStyle = "white";
                }
            }
            for (var wall = 0; wall < current_board.walls_v.length; wall++) {
                pos = current_board.walls_v[wall]
                if ((column - 1) / 2 == pos[0] && row >=2*pos[1] && row <= 2*pos[1]+2) {
                    context2D.fillStyle = "white";
                }
            }
            context2D.fillRect(col_offset, row_offset, width-1,height-1);
            
            if (current_board.current_player == player_number) {
                for (var valid_move_num = 0; valid_move_num < current_board.valid_moves.length; valid_move_num++) {
                    valid_move = current_board.valid_moves[valid_move_num];
                    if (column / 2 == valid_move[0] && row / 2 == valid_move[1])
                    {
                        context2D.beginPath();
                        context2D.arc(col_offset + (width/2), row_offset + (height/2), (width/2)-4, 0, 2 * Math.PI, false);
                        //if (player == 0) { context2D.fillStyle = 'white'; };
                        //if (player == 1) { context2D.fillStyle = 'grey'; };
                        //context2D.fill();
                        context2D.lineWidth = 2;
                        context2D.strokeStyle = 'white';
                        context2D.stroke();
                    }
            
                }
            }
            
            for (var player = 0; player < current_board.players.length; player++)
            {
                pos = current_board.players[player].position
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
                    
                    if (current_board.current_player == player) {
                        context2D.beginPath();
                        context2D.arc(col_offset + (width/2), row_offset + (height/2), (width/2)-4, 0, 2 * Math.PI, false);
                        context2D.lineWidth = 3;
                        context2D.strokeStyle = 'yellow';
                        context2D.stroke();                    
                    }
                    
                }
            }
      
            col_offset = col_offset + width;
        }
        
        row_offset = row_offset + height;
    }
    document.getElementById("p1_walls").textContent=current_board.players[0].walls;
    document.getElementById("p2_walls").textContent=current_board.players[1].walls;
    document.getElementById("playerNumber").textContent=(player_number + 1);
    if (current_board.current_player == player_number) {
        updateStatus("Your turn: Place wall or move game piece")
    } else {
        updateStatus("Player " + (current_board.current_player + 1) + "'s Turn");
    }
    renderWallSelector();
    if (current_board.winner === player_number) {
        updateStatus("You win!")
    }else if (current_board.winner) {
        updateStatus("Player " + (current_board.winner + 1) + " Wins!")
    }
}

function renderWallSelector() {
    var walltype = document.getElementById("walltype");
    walltype.setAttribute('width', 2*cell_width);
    walltype.setAttribute('height', 2*cell_width);
    var wallContext = walltype.getContext("2d");
    wallContext.fillStyle = "black";
    center = cell_width - (wall_width / 2)
    if (wall_type == "H") {
      wallContext.fillRect(0, center, 2* cell_width,wall_width);
    } else if (wall_type == "V") {      
      wallContext.fillRect(center, 0, wall_width, 2*cell_width);
    }
    wallContext.font = "30px Arial";
    if (current_board.players) {
        wallContext.fillText(current_board.players[player_number].walls,2*cell_width-18,2*cell_width-2);
    }
  
};
