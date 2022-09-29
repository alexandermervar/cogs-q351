function traceToBoardHTML(trace) {
    var board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0];
    var turn = 0;
    function makeMove(move) {
        var pit = turn*7 + move;
        var stones = board[pit];
        board[pit] = 0;
        while (stones > 0) {
            // skip opponent's pot, otherwise move 1 forward.
            if ((pit == 5 && turn == 1) || (pit == 12 && turn == 0))
                pit += 2;
            else
                pit += 1;
            // loop around
            pit %= 14;
            // add stone to next pit
            board[pit] += 1;
            stones -= 1;
        }
        // switch turns unless the player's last stone landed in their pot
        if (pit != 6 && pit != 13) {
            // do the crazy capturing thing
            var side = Math.floor(pit / 7);
            var player_pot = 7*turn + 6;
            var across_pit = 12 - pit;
            if (side == turn && board[pit] == 1 && board[across_pit]) {
                board[player_pot] += 1 + board[across_pit];
                board[pit] = 0;
                board[across_pit] = 0;
            }

            turn = 1 - turn;
        }
        // check whether game is over; award bonus if so
        var p1_total = board.slice(0,6).reduce((a,b) => a + b);
        var p2_total = board.slice(7,13).reduce((a,b) => a + b);
        if (p1_total == 0 || p2_total == 0) {
            board[6] += p1_total;
            board[13] += p2_total;
            board[0] = board[1] = board[2] = board[3] = board[4] = board[5] = 0;
            board[7] = board[8] = board[9] = board[10] = board[11] = board[12] = 0;
        }
    }
    for (var i = 0; i < trace.length; i ++) makeMove(Number(trace[i]));
    return '<table class="mancala"><tr><td rowspan="2">'+board[13]+'</td><td>'+board[12]+'</td><td>'+board[11]+'</td><td>'+board[10]
        +'</td><td>'+board[9]+'</td><td>'+board[8]+'</td><td>'+board[7]+'</td><td rowspan="2">'+board[6]+'</td></tr>'
        +'<tr><td>'+board[0]+'</td><td>'+board[1]+'</td><td>'+board[2]+'</td><td>'+board[3]+'</td><td>'+board[4]+'</td><td>'+board[5]+'</td></tr></table>';
}
