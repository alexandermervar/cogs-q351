#!/usr/bin/python3

import time
import numbers
from .instructor import RefBoard, RandomPlayer, KylePlayer

def compete(StudentPlayer, StudentBoard, trace, TestPlayer=KylePlayer, TestBoard=RefBoard, max_time=0.1, verbose=False):
	student_players = []

	for depth in range(1, 17):
		student_players.append(StudentPlayer(depth))

	test_player = TestPlayer()

	traces = [[],[]]
	turns = [[],[]]
	times = [[],[]]

	wins = 0

	penalty_time = max_time*4

	for player_first in [True, False]:
		ref_board = TestBoard(trace=trace)

		traces[player_first].append(ref_board.trace)
		turns[player_first].append('start')
		times[player_first].append(0)
		if verbose: test_board.print()

		# use the test board as a reference
		while not ref_board.game_over:
			if (ref_board.turn == 0) ^ player_first:
				turns[player_first].append(test_player.__class__.__name__)
				start = time.perf_counter()
				move = test_player.findMove(ref_board.trace)
				end = time.perf_counter()
			else:
				for student_player in student_players:
					start = time.perf_counter()
					move = student_player.findMove(ref_board.trace)
					if not isinstance(move, numbers.Number) or not 0 <= move <= 5:
						raise RuntimeError(f'On board with trace {ref_board.trace}, {StudentPlayer.__name__}({student_player.max_depth}) returns invalid move {move!r}.')
					end = time.perf_counter()
					if end - start > max_time:
						if end - start > penalty_time:
							max_time /= 2
						#print(end-start)
						break
				turns[player_first].append(student_player.__class__.__name__+f'({student_player.max_depth}) (you)')
			ref_board.makeMove(move)

			times[player_first].append(end-start)
			traces[player_first].append(ref_board.trace)
			if verbose: ref_board.print()

		if ref_board.winner == -1:
			wins += .5
		elif player_first ^ (ref_board.winner == 1):
			wins += 1

	return traces, turns, times, wins
