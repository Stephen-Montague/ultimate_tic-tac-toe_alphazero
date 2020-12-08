
import copy
import math
import numpy as np
from keras.models import load_model

# Hyper-parameters
model_path = "GoodUltimate2019-03-03 21_06_38+MCTS600+cpuct4.h5"
mcts_search = 1600
MCTS = True
cpuct = 1.5


def set_empty_board():
    board = []
    for i in range(9):
        board.append([[" ", " ", " "],
                      [" ", " ", " "],
                      [" ", " ", " "]])
    return board


def print_board(totalBoard):
    firstRow = ""
    secondRow = ""
    thirdRow = ""

    # Take each board, save each row in a variable, then print
    for boardIndex in range(len(totalBoard)):
        firstRow = firstRow + "|" + " ".join(totalBoard[boardIndex][0]) + "|"
        secondRow = secondRow + "|" + " ".join(totalBoard[boardIndex][1]) + "|"
        thirdRow = thirdRow + "|" + " ".join(totalBoard[boardIndex][2]) + "|"

        # print boards and reset variables
        if boardIndex > 1 and (boardIndex + 1) % 3 == 0:
            print(firstRow)
            print(secondRow)
            print(thirdRow)
            print("---------------------")
            firstRow = ""
            secondRow = ""
            thirdRow = ""


def possiblePos(board, subBoard):
    if subBoard == 9:
        return range(81)

    # otherwise, finds all available spaces in the subBoard
    possible = []
    if board[subBoard][1][1] != 'x' and board[subBoard][1][1] != 'o':
        for row in range(3):
            for column in range(3):
                if board[subBoard][row][column] == " ":
                    possible.append((subBoard * 9) + (row * 3) + column)
        if len(possible) > 0:
            return possible

    # if the subBoard has already been won, it finds all available spaces on the entire board
    for mini in range(9):
        if board[mini][1][1] == "x" or board[mini][1][1] == "o":
            continue
        for row in range(3):
            for column in range(3):
                if board[mini][row][column] == " ":
                    possible.append((mini * 9) + (row * 3) + column)
    return possible


def move(board, action, player):
    if player == 1:
        turn = 'X'
    else:  # player == -1
        turn = "O"

    bestPosition = [(int(action / 9))]
    remainder = action % 9
    bestPosition.append(int(remainder / 3))
    bestPosition.append(remainder % 3)

    # place piece at position on board
    board[bestPosition[0]][bestPosition[1]][bestPosition[2]] = turn

    emptyMiniBoard = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

    wonBoard = False
    win = False
    mini = board[bestPosition[0]]
    subBoard = bestPosition[0]
    x = bestPosition[1]
    y = bestPosition[2]

    # check for win on vertical
    if mini[0][y] == mini[1][y] == mini[2][y]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on horizontal
    if mini[x][0] == mini[x][1] == mini[x][2]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on negative diagonal
    if x == y and mini[0][0] == mini[1][1] == mini[2][2]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on positive diagonal
    if x + y == 2 and mini[0][2] == mini[1][1] == mini[2][0]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # set new subBoard
    newSubBoard = (bestPosition[1] * 3) + bestPosition[2]

    # if the subBoard was won, checking whether the entire board is won as well
    if wonBoard is True:
        win = checkWinner(board, subBoard, turn)

    return board, newSubBoard, win


def checkWinner(board, winningSubBoard, turn):
    # getting coordinates of winning subBoard
    winningSubBoardCoordinate = []
    for i in range(3):
        if (winningSubBoard - i) % 3 == 0:
            row = int((winningSubBoard - i) / 3)
            winningSubBoardCoordinate = [row, i]
            break

    # making winning subBoard using just centre pieces
    winningBoard = [
        [board[0][1][1], board[1][1][1], board[2][1][1]],
        [board[3][1][1], board[4][1][1], board[5][1][1]],
        [board[6][1][1], board[7][1][1], board[8][1][1]]
    ]

    # horizontal wins
    if turn.lower() == winningBoard[winningSubBoardCoordinate[0]][0] \
            == winningBoard[winningSubBoardCoordinate[0]][1] \
            == winningBoard[winningSubBoardCoordinate[0]][2]:
        return True
    # vertical wins
    elif turn.lower() == winningBoard[0][winningSubBoardCoordinate[1]] == winningBoard[1][
            winningSubBoardCoordinate[1]] == winningBoard[2][winningSubBoardCoordinate[1]]:
        return True
    # top left to bottom right diagonal
    elif turn.lower() == winningBoard[0][0] == winningBoard[1][1] == winningBoard[2][2]:
        return True
    # bottom left to top right diagonal
    elif turn.lower() == winningBoard[2][0] == winningBoard[1][1] == winningBoard[0][2]:
        return True
    else:
        return False


def human_turn(board, subBoard, turn):
    possible = possiblePos(board, subBoard)

    print_board(board)
    print("It is " + turn + "'s turn")

    # check if the subBoard has already been won, and takes new subBoard as input
    if subBoard == 9 or board[subBoard][1][1] == "x" or board[subBoard][1][1] == "o" or len(possible) > 9:
        while True:
            try:
                newSubBoard = int(input("Which sub-board would you like to play on? ")) - 1
            except ValueError:
                print("That was not a valid integer, please try again")
                continue
            if newSubBoard not in range(9):
                print("Please enter a number between 1 and 9")
                continue
            if board[newSubBoard][1][1] == "x" or board[newSubBoard][1][1] == "o":
                print("That board has been taken, please enter a valid board")
                continue
            else:
                subBoard = newSubBoard
                break

    # takes placement of piece as input
    print("You can only play on board number", subBoard + 1)
    input_to_coordinates = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    y, x = None, None
    while True:
        try:
            user_input = int(input("Please enter a space number: ")) - 1
            y, x = input_to_coordinates[user_input]
        except ValueError:
            print("The input was not a valid number, please try again")
            continue
        except IndexError:
            print("Number must be between 1 and 9, please try again")
        if board[subBoard][y][x] != " ":
            print("That space has already been taken, please try again")
            continue
        else:
            return subBoard * 9 + y * 3 + x


# ---------------------------------
# Functions for neural network
# --------------------------------


# initializing search tree
Q = {}  # state-action values
Nsa = {}  # number of times certain state-action pair has been visited
Ns = {}  # number of times state has been visited
W = {}  # number of total points collected after taking state action pair
P = {}  # initial predicted probabilities of taking certain actions in state


def fill_winning_boards(board):
    # takes in a board in its normal state, and converts all subBoards that have been won to the winning player's piece

    new_board = []
    for subBoard in board:
        if subBoard[1][1] == 'x':
            new_board.append([["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]])
        elif subBoard[1][1] == 'o':
            new_board.append([["O", "O", "O"], ["O", "O", "O"], ["O", "O", "O"]])
        else:
            new_board.append(subBoard)
    return new_board


def letter_to_int(letter, player):
    # based on the letter in a box in the board, replaces 'X' with 1 and 'O' with -1
    if letter == 'v':
        return 0.1
    elif letter == " ":
        return 0
    elif letter == "X":
        return 1 * player
    elif letter == "O":
        return -1 * player


def set_board_to_array(board_original, mini_board, player):
    # makes copy of board, so that the original board does not get changed
    board = copy.deepcopy(board_original)

    # takes a board in its normal state, and returns a 9x9 numpy array, changing 'X' = 1 and 'O' = -1
    # also places a 0.1 in all valid board positions

    board = fill_winning_boards(board)
    tie = True

    # if it is the first turn, then all of the cells are valid moves
    if mini_board == 9:
        return np.full((9, 9), 0.1)

    # replacing all valid positions with 'v'
    # checking whether all empty values on the board are valid
    if board[mini_board][1][1] != 'x' or board[mini_board][1][1] != 'o':
        for line in range(3):
            for item in range(3):
                if board[mini_board][line][item] == " ":
                    board[mini_board][line][item] = 'v'
                    tie = False
    # if not, then replacing empty cells in mini board with 'v'
    else:
        for subBoard in range(9):
            for line in range(3):
                for item in range(3):
                    if board[subBoard][line][item] == " ":
                        board[subBoard][line][item] = 'v'

    # if the miniBoard ends up being a tie
    if tie:
        for subBoard in range(9):
            for line in range(3):
                for item in range(3):
                    if board[subBoard][line][item] == " ":
                        board[subBoard][line][item] = 'v'

    board_to_array = []
    firstLine = []
    secondLine = []
    thirdLine = []

    for subBoardNum in range(len(board)):

        for item in board[subBoardNum][0]:
            firstLine.append(letter_to_int(item, player))

        for item in board[subBoardNum][1]:
            secondLine.append(letter_to_int(item, player))

        for item in board[subBoardNum][2]:
            thirdLine.append(letter_to_int(item, player))

        if (subBoardNum + 1) % 3 == 0:
            board_to_array.append(firstLine)
            board_to_array.append(secondLine)
            board_to_array.append(thirdLine)
            firstLine = []
            secondLine = []
            thirdLine = []

    return np.array(board_to_array)


def mcts(s, current_player, mini_board):
    if mini_board == 9:
        possibleA = range(81)
    else:
        possibleA = possiblePos(s, mini_board)

    sArray = set_board_to_array(s, mini_board, current_player)
    sTuple = tuple(map(tuple, sArray))

    if len(possibleA) > 0:
        if sTuple not in P.keys():

            policy, v = nn.predict(sArray.reshape((1, 9, 9)))
            v = v[0][0]
            validS = np.zeros(81)
            np.put(validS, possibleA, 1)
            policy = policy.reshape(81) * validS
            policy = policy / np.sum(policy)
            P[sTuple] = policy

            Ns[sTuple] = 1

            for a in possibleA:
                Q[(sTuple, a)] = 0
                Nsa[(sTuple, a)] = 0
                W[(sTuple, a)] = 0
            return -v

        best_uct = -100
        best_a = None
        for a in possibleA:

            uct_a = Q[(sTuple, a)] + cpuct * P[sTuple][a] * (math.sqrt(Ns[sTuple]) / (1 + Nsa[(sTuple, a)]))

            if uct_a > best_uct:
                best_uct = uct_a
                best_a = a

        next_state, mini_board, wonBoard = move(s, best_a, current_player)

        if wonBoard:
            v = 1
        else:
            current_player *= -1
            v = mcts(next_state, current_player, mini_board)
    else:
        return 0

    W[(sTuple, best_a)] += v
    Ns[sTuple] += 1
    Nsa[(sTuple, best_a)] += 1
    Q[(sTuple, best_a)] = W[(sTuple, best_a)] / Nsa[(sTuple, best_a)]
    return -v


def set_action_probability_distribution(init_board, current_player, mini_board):
    for _ in range(mcts_search):
        s = copy.deepcopy(init_board)
        mcts(s, current_player, mini_board)

    print("Done MCTS")

    actions_dict = {}

    sArray = set_board_to_array(init_board, mini_board, current_player)
    sTuple = tuple(map(tuple, sArray))

    for a in possiblePos(init_board, mini_board):
        actions_dict[a] = Nsa[(sTuple, a)] / Ns[sTuple]

    print("Actions dict:", actions_dict)

    action_probability_distribution = np.zeros(81)
    for a in actions_dict:
        np.put(action_probability_distribution, a, actions_dict[a], mode='raise')

    return action_probability_distribution


nn = load_model(model_path)


def playGame():
    board = set_empty_board()
    mini_board = 9
    global nn

    while True:
        action = human_turn(board, mini_board, 'X')
        next_board, mini_board, wonBoard = move(board, action, 1)

        if wonBoard:

            print("You won the game!")
            print_board(board)
            print("Wow you're really good. "
                  "You just beat a computer that trained for hours and thought about thousands of moves.")
            break
        else:
            board = next_board

        if MCTS:
            policy = set_action_probability_distribution(board, -1, mini_board)
            policy = policy / np.sum(policy)
        else:
            policy, value = nn.predict(set_board_to_array(board, mini_board, -1).reshape((1, 9, 9)))
            possibleA = possiblePos(board, mini_board)
            validS = np.zeros(81)
            np.put(validS, possibleA, 1)
            policy = policy.reshape(81) * validS
            policy = policy / np.sum(policy)

        action = np.argmax(policy)
        print("Action", action)
        print("Policy")
        print(policy)

        next_board, mini_board, wonBoard = move(board, action, -1)

        if wonBoard:
            print("Awww you lost. Better luck next time")
            break
        else:
            board = next_board


playGame()
