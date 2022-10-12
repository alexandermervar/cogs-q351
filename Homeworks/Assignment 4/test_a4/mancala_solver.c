#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int board_history[255][15] = {[0] = {4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0, 1}};
int* orig = board_history[0];
int* board = board_history[0];
int game_over = 0;

int max_depth = 12;

#define p1_pot board[6]
#define p2_pot board[13]
#define turn board[14]
#define calc_p1_sum board[0] + board[1] + board[2] + board[3] + board[4] + board[5]
#define calc_p2_sum board[7] + board[8] + board[9] + board[10] + board[11] + board[12]

#define board_push memcpy(board + 15, board, 15*sizeof(int)); board += 15
#define board_pop board -= 15; game_over = 0
#define depth (board - orig) / 15

void makeMove(int pit) {
    // remove stones from corresponding pit
    int stones = board[pit];
    board[pit] = 0;
    while (stones > 0) {
        // skip opponent's pot
        if ((pit == 5 && turn == 1) || (pit == 12 && turn == 0))
            pit += 2;
        else pit += 1;
        // loop around
        pit %= 14;
        // add stone to next pit
        board[pit] += 1;
        stones -= 1;
    }
    // switch turns, unless player's last stone landed in their pot
    if (pit != 6 && pit != 13) {
        // do crazy capturing thing
        int side = pit / 7;
        int across_pit = 12 - pit;
        if (side == turn && board[pit] == 1 && board[across_pit] != 0) {
            int player_pot = 7*turn+6;
            board[player_pot] += 1 + board[across_pit];
            board[pit] = 0;
            board[across_pit] = 0;
        }
        turn = 1 - turn;
    }
    int p1_sum = calc_p1_sum;
    int p2_sum = calc_p2_sum;
    if (p1_sum == 0 || p2_sum == 0) {
        p1_pot += p1_sum;
        p2_pot += p2_sum;
        game_over = 1;
    }
}

int alphaBeta(int alpha, int beta) {
    if (game_over) return (p1_pot - p2_pot);
    if (depth > max_depth) return 0;
    int best_score;
    int score;
    if (turn == 0) {
        best_score = -49;
        for (int pit = 0; pit < 6; pit ++) {
            if (board[pit]) {
                board_push;
                makeMove(pit);
                score = alphaBeta(alpha, beta);
                board_pop;
                if (score > alpha) alpha = score;
                if (alpha >= beta) return score;
                if (score > best_score) best_score = score;
            }
        }
    }
    else {
        best_score = 49;
        for (int pit = 7; pit < 13; pit ++) {
            if (board[pit]) {
                board_push;
                makeMove(pit);
                score = alphaBeta(alpha, beta);
                board_pop;
                if (score < beta) beta = score;
                if (alpha >= beta) return score;
                if (score < best_score) best_score = score;
            }
        }
    }
    return best_score;
}

int main(int argc, char *argv[]) {
    int pit;
    if (argc == 1)
        printf("Usage: mancala max_depth [board_trace='']\n");
    if (argc >= 2) sscanf(argv[1], "%d", &max_depth);
    if (argc >= 3) {
        char* move = argv[2];
        for (int i = 0; move[i] != '\0'; i++) {
            pit = turn*7 + (int) (move[i] - '0');
            if (board[pit] == 0) printf("Invalid board. Oh no.\n");
            makeMove(pit);
        }
    }
    printf("%d\n", alphaBeta(-50, 50));
}
