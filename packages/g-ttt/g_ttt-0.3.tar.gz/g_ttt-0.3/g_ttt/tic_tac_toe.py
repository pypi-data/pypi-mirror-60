#Prints the board
def board(moves):
	print(f' {moves[7]} | {moves[8]} | {moves[9]} \n-----------\n {moves[4]} | {moves[5]} | {moves[6]} \n-----------\n {moves[1]} | {moves[2]} | {moves[3]} ')

#Checks winning condition
def win_check(moves,letter):
	if moves[7] == letter and moves[8] == letter and moves[9] == letter:
		return True
	if moves[4] == letter and moves[5] == letter and moves[6] == letter:
		return True
	if moves[1] == letter and moves[2] == letter and moves[3] == letter:
		return True

	if moves[7] == letter and moves[4] == letter and moves[1] == letter:
		return True
	if moves[8] == letter and moves[5] == letter and moves[2] == letter:
		return True
	if moves[9] == letter and moves[6] == letter and moves[3] == letter:
		return True

	if moves[7] == letter and moves[5] == letter and moves[3] == letter:
		return True
	if moves[9] == letter and moves[5] == letter and moves[1] == letter:
		return True
	else:
		return False


def ask_to_play_again():
	while True:
		answer = input('\n\nDo you want to play again (Y/N)? ')
		if answer == 'N' or answer == 'n':
			print('\nThank you for playing!')
			return False
		elif answer == 'Y' or answer == 'y':
			print('\n')
			return True
		else:
			print('Please, input a valid answer')

def instructions():
	print('\nInstructions of how to play the game:\n\n')
	print('When choosing a place to make a move, use the correspondent number keys as stated here: \n')
	print(f' 7 | 8 | 9 \n-----------\n 4 | 5 | 6 \n-----------\n 1 | 2 | 3 ')
	print('\n')

#Prints the score
def game_score(score):
	print(f'X score: {score[0]}')
	print(f'O score: {score[1]}')
	print('\n')	

def game_start():
	start_game()

#Starting the game
def start_game():

	score = [0, 0]
	while True:

		#Introduction
		print('\n\n\nHey, welcome to Tic Tac Toe!')
		instructions()
		game_score(score)
		#Choosing the letter of the first player
		XO = ['X','O']
		first_letter = input('Does the first player want to be the O or the X? ')
		while True:
			if first_letter == 'X' or first_letter == 'x':
				break
			elif first_letter == 'O' or first_letter == 'o':
				XO = XO[::-1]
				break
			else:
				first_letter = input('Please, choose between "X" or "O": ')

		#Setting starting conditions
		moves = [' ']*10
		win = False
		print('\n'*3)
		board(moves)
		

		#Starts the game
		for i in range(1,10):
			print(f'\nTURN: {XO[i%2 - 1]}')
			
			#Checking for legal move
			while True:
				u = input('Where do you to make your move? ')

				if u not in '123456789':
					print('\nPlease make a legal move')
				elif moves[int(u)] == 'X' or moves[int(u)] == 'O':
					print('\nPlease make a legal move')
				else:
					u = int(u)
					break

			print('\n'*3)
			moves[u] = XO[i%2 - 1]
			board(moves)

			#Checking winning conditions
			if win_check(moves,XO[i%2 - 1]):
				print(f'\nTHE GAME IS OVER!\n{XO[i%2 - 1]} IS THE WINNER! CONGRATULATIONS!')
				
				if XO[i%2 - 1] == 'X':
					score[0] += 1
				else:
					score[1] += 1
				
				game_score(score)
				break

			if win_check(moves,XO[i%2]):
				print(f'\nTHE GAME IS OVER!\n{XO[i%2]} IS THE WINNER! CONGRATULATIONS!')
				
				if XO[i%2] == 'X':
					score[0] += 1
				else:
					score[1] += 1
				
				game_score(score)
				break

			if i == 9:
				print("\nTHE GAME IS OVER! IT'S A DRAW!")
				game_score(score)
				break
		
			

		if ask_to_play_again() == False:
			print('\nFINAL SCORES')
			game_score(score)
			break

start_game()