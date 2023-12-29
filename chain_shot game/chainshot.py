""" This game is a collect game where of each turn you should collect two or more numbers based on spatial relationship.
That is, once you pick a cell, all neighboring cells (including the cell you picked) that contain the same number will disappear from the board.
If a cell disappears in a column, that column moves down to fill the row with blank cells. this game continues until there is no cell that has no neighbor with the same value,
 it means that the game is over.

python3 chainshot.py input.txt
"""
import sys
#globals
ram_list=[]
score=0
removed_cells=0
def main():
    board_file=sys.argv[1]
    #output_file=sys.argv[2]
    board=txt_to_list(board_file)
    menu(board)
def txt_to_list(board_file):
    # This function transforms the input file into a list.
    board_raw=open(board_file,"r")
    board=[]
    for line in board_raw:
        board.append(list(map(int,line.split(" "))))
    return board
def show_board(board):
    # The function is below this text, portraying the board  in an aesthetically pleasing manner
    print("-"*((len(board[0])*2)-1),end="|")
    print("SCORE:",score)
    for row_num,row_content in enumerate(board):

        for col_num,index in enumerate(row_content):
            if board[row_num][col_num]!="y":
                print(str(board[row_num][col_num]),end=" ")
            else:
                print(" ",end=" ")
        print("\n")
    print("-" * ((len(board[0]) * 2) - 1))
def menu(board):
    # Menu function takes input from the user and checks for some exceptions
    show_board(board)
    numbers_raw=input("Please enter row and column row(1,2,3..n) col(1,2,3..n): ")
    numbers=numbers_raw.split(" ")
    row = int(numbers[0])-1
    col = int(numbers[1])-1
    # Checking whether the selected number is within bounds. (try except block)
    #3 possible scenarios:
    #1) The selected number may correspond to the string 'x',
    #2) The selected index may be negative,
    #3) An error may occur due to the selected number being out of bounds (in which case the except block will be executed)
    try:
        if(type(board[row][col])==str or row<0 or col<0):
            print("\nPlease enter a correct size")
            return menu(board)
    except:
        print("\nPlease enter a correct size")
        return menu(board)

    #Checking whether the number at the selected index is alone or not if its alone that means dont do anything and call the menu again
    counter = 0

    if col + 1 < len(board[0]) and type(board[row][col + 1]) == int and board[row][col + 1] == board[row][col]:
        counter += 1

    if col - 1 >= 0 and type(board[row][col - 1]) == int and board[row][col - 1] == board[row][col]:
        counter += 1

    if row + 1 < len(board) and type(board[row + 1][col]) == int and board[row + 1][col] == board[row][col]:
        counter += 1

    if row - 1 >= 0 and type(board[row - 1][col]) == int and board[row - 1][col] == board[row][col]:
        counter += 1

    if counter < 1:
        print("No movement happened, try again")
        return menu(board)
    #We will use this number variable while calculating score
    number = board[row][col]

    return collect_cells(board, row, col, number)
def collect_cells(board, row, col, number):
    # The main idea of this function is to change the index of the collected cell to 'x' and send the collected cells matrix to ram
    # Also updates the 'removed_cells' global variable (necessary for score calculation)
    global removed_cells

    # The operation of changing the selected number
    board[row][col] = "x"

    # remove neighboring cells
    try:
        if col + 1 < len(board[0]) and board[row][col + 1] == number:
            board[row][col + 1] = "x"
            removed_cells += 1
            ram_list.append((str(row) + " " + str(col + 1)))

        if col - 1 >= 0 and board[row][col - 1] == number:
            board[row][col - 1] = "x"
            removed_cells += 1
            ram_list.append((str(row) + " " + str(col - 1)))

        if row + 1 < len(board) and board[row + 1][col] == number:
            board[row + 1][col] = "x"
            removed_cells += 1
            ram_list.append((str(row + 1) + " " + str(col)))

        if row - 1 >= 0 and board[row - 1][col] == number:
            board[row - 1][col] = "x"
            removed_cells += 1
            ram_list.append((str(row - 1) + " " + str(col)))

    except:
        pass

    return ram(board,number)
def ram(board,number):
    # This function takes a number from the ram_list, removes it, and then sends  number to the "collect_cells" function.
    global removed_cells
    # This is a break statement if ram_list is empty its time to shuffle
    if ram_list==[]:
        if removed_cells >0:
            global score
            score = score + (removed_cells + 1) * number
            removed_cells=0
            return shifting(board)
    # Taking a matrix from the ram_list and sending its row and column values to the "collect_cells" function
    index=ram_list[0].split(" ")
    row=int(index[0])
    col=int(index[1])
    ram_list.pop(0)
    #Then, we will send this matrix to the "collect_cells" function to check it neighbors.
    return collect_cells(board, row, col, number)
    # To summarize, all deleted cells are added to the ram_list, and then the deleted cells are sent to the 'collect_cells' function to check neighbors this proccess continues until ram_list is empty
def matrix_reverser(board):
    # This function convert rows to columns,  we will use it later in the shifting function
    new_board=[]
    row_len=len(board)
    col_len=len(board[0])
    for a1 in range(col_len):
        temporary_row=[]
        for a2 in range(row_len):
            temporary_row.append(board[a2][a1])
        new_board.append(temporary_row)
    return new_board
def shifting(board):
    # The shifting function is used to shift column values
    # Firstly, we should modify rows and columns
    board=matrix_reverser(board)

    # Shuffle
    for row_number,row_content in enumerate(board):
        for index_num,index in enumerate(row_content):
            # In this context,"x"s are removed, and "y"s are added to the end of the column, thus performing the shifting operation
            if board[row_number][index_num]=="x":
                board[row_number].pop(index_num)
                board[row_number].insert(0,"y")
                board=matrix_reverser(board)
                return shifting(board)
    # We should fix rows and columns before exit the function
    board = matrix_reverser(board)
    # So, in these functions, all "x"s are transformed into "y" and shifted it's time to remove any empty rows and columns
    return row_col_remover(board)
def row_col_remover(board):

    def row_remover(board):
        # Row control, if it's empty remove it
        for row_num,row_content in enumerate(board):
            if all(index=="y" for index in row_content):
                board.pop(row_num)
                return row_remover(board)
        return(board)
    # Calling the function
    board=row_remover(board)

    # I added this "if" statement bcause "col" function below this text encounters an error with an empty list input
    if board==[]:
        gameover_check(board)


    def col_remover(board):
        # Col control, if it's empty remove it
        board=matrix_reverser(board)
        for row_num,row_content in enumerate(board):
            if all(index=="y" for index in row_content):
                board.pop(row_num)
                board = matrix_reverser(board)
                return col_remover(board)
        board = matrix_reverser(board)
        return(board)

    # Calling the function
    board=col_remover(board)

    return gameover_check(board)
def gameover_check(board):
    # If there are no other cells with the same neighbors, that means the game is over. function is brute forcing below this text
    for row,row_content in enumerate(board):
        for col,index in enumerate(row_content):
            if col + 1 < len(board[0]) and type(board[row][col + 1]) == int and board[row][col + 1] == board[row][col]:
                return menu(board)

            if col - 1 >= 0 and type(board[row][col - 1]) == int and board[row][col - 1] == board[row][col]:
                return menu(board)

            if row + 1 < len(board) and type(board[row + 1][col]) == int and board[row + 1][col] == board[row][col]:
                return menu(board)

            if row - 1 >= 0 and type(board[row - 1][col]) == int and board[row - 1][col] == board[row][col]:
                return menu(board)
    print( "there is no cell that has no neighbor with the same value, it means that the game is over.")

    try:
        # Shows the board before exiting if possible (If the board is empty, errors occur)
        show_board(board)
    except:
        pass
    return input("")
if __name__=="__main__":
    main()