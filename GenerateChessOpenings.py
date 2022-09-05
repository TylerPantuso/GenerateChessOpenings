# GenerateChessOpenings.py
# MIT License

from os import path
import chess
import stockfish


# Abstract class to represent a single chess move
class ChessMove:
    def set_fen(self, fen: str):
        self.fen = fen
    
    def get_fen(self):
        return self.fen
    
    def set_san(self, san: str):
        self.san = san
    
    def get_san(self):
        return self.san
    
    def set_uci(self, uci: str):
        self.uci = uci
    
    def get_uci(self):
        return self.uci
    
    def get_turn():
        next_move_turn_text = fen.split()[1]
        is_white = next_move_turn_text == "b"
        return is_white


# Base object that holds a sequence of chess moves
class ChessGame:
    def __init__(self, fen = chess.STARTING_FEN):
        self.fen = fen
        self.starting_fen = fen
        self.move_sequence = []
    
    def set_fen(self, fen: str):
        self.fen = fen
    
    def get_fen(self):
        return self.fen
    
    def get_starting_fen(self):
        return self.starting_fen
    
    def append_move(self, move):
        self.move_sequence.append(move)
        self.fen = move.get_fen()
    
    def get_moves(self):
        return self.move_sequence
    
    def get_san_sequence(self):
        moves = [chess.Move.from_uci(x.get_uci()) for x in self.move_sequence]
        return blank_board.variation_san(moves)
    
    def copy(self):
        new_copy = ChessGame(self.starting_fen)
        new_copy.move_sequence = self.move_sequence.copy()

        if len(new_copy.move_sequence) > 0:
            last_move = new_copy.move_sequence[-1]
            new_copy.set_fen(last_move.get_fen())
        
        return new_copy


# Create one board to move pieces on and another one to generate SAN sequences
board = chess.Board()
blank_board = chess.Board()

# Create stockfish instance
sf_dir = path.dirname(stockfish.__file__)
sf_exe = "stockfish.exe"
sf_path = path.join(sf_dir, sf_exe)
sf = stockfish.Stockfish(sf_path)

# Set hash to 2048 (2 gigs RAM) & 16 threads (number of processors being used)
sf.update_engine_parameters({"Hash": 2048, "Threads": 16})

# Set depth (number of half-moves to analyze) to twice the default value
sf.set_depth(30)

# Create list to hold all generated game variations & load first blank game
game_collection = [ChessGame(board.fen())]

# Tell the user how to use this code
print("*" * 30 + " GenerateChessOpenings.py " + "*" * 30)
print("#")
print("# Last updated:  9/5/2022")
print("# License:       MIT")
print("# Dependencies:  Stockfish, python-chess")
print("#")
print("# Use chess_help() for more information.")
print("#")
print("\n")


# Makes a move with chess.Board and stockfish
def make_move_san(san_text):
    move = board.push_san(san_text)
    sf.make_moves_from_current_position([move.uci()])


# Makes a move with chess.Board and stockfish
def make_move_uci(uci_text):
    move = board.push_uci(uci_text)
    sf.make_moves_from_current_position([move.uci()])


# Makes a move with chess.Board and stockfish
def make_move(move):
    board.push_san(move.get_san())
    sf.make_moves_from_current_position([move.get_uci()])


# Prints a visual of the board with the stockfish method
def show_board(is_white: bool = True):
    board_text = sf.get_board_visual(is_white)
    print(board_text)


# Resets the chess board in stockfish and chess.Board
def reset_board():
    board.reset()
    sf.set_position()


# Sets board in stockfish and chess.Board
def set_board(game: ChessGame):
    reset_board()

    for move in game.get_moves():
        make_move_san(move.get_san())


# Returns true if white's turn, false if black's turn
def get_turn():
    turn_text = board.fen().split()[1]
    return turn_text == "w"


# Takes a FEN and UCI and returns a SAN
def get_san(fen_before: str, uci: str):
    temp_board = chess.Board(fen_before)
    temp_move = chess.Move.from_uci(uci)
    return temp_board.san(temp_move)


# Returns what the FEN will be if the given move is made
def get_next_fen(current_fen: str, uci: str):
    temp_board = chess.Board(current_fen)
    temp_board.push_uci(uci)
    return temp_board.fen()


# Creates and returns a Move based on the current chess.Board
def create_move_from_san(san_text):
    uci_text = board.parse_san(san_text).uci()
    fen_text = get_next_fen(board.fen(), uci_text)

    move = ChessMove()
    move.set_san(san_text)
    move.set_uci(uci_text)
    move.set_fen(fen_text)

    return move


# Gests the best n moves based on the current board
def get_best_moves(number_of_moves: int):
    sf_moves = sf.get_top_moves(number_of_moves)
    moves = []
    
    for move in sf_moves:
        chess_move = ChessMove()
        chess_move.set_uci(move["Move"])
        chess_move.set_fen(get_next_fen(board.fen(), move["Move"]))
        chess_move.set_san(get_san(board.fen(), move["Move"]))
        
        moves.append(chess_move)
    
    return moves


# Expands the games by the factor provided using the best n moves
def expand_game_collection(factor: int):
    print(f"Log: Expanding game collection by {factor}.") # LOG
    global game_collection
    new_game_collection = []
    
    log_index = 1
    
    for game in game_collection:
        print(f"Log: Starting loop {log_index} of {len(game_collection)}")
        set_board(game)
        best_moves = get_best_moves(factor)
        
        for best_move in best_moves:
            new_game = game.copy()
            new_game.append_move(best_move)
            
            new_game_collection.append(new_game)
        
        log_index += 1
    
    game_collection = new_game_collection.copy()
    print(f"Log: {len(game_collection)} games in game collection.") # LOG


# Loads a game collection from text, delimited by spaces and newlines
def load_game_collection(game_text: str):
    global game_collection
    game_collection = []
    
    game_lines = game_text.splitlines()
    log_index = 1
    
    for line in game_lines:
        print(f"Log: Loading {log_index} of {len(game_lines)} games.") # LOG
        moves_by_san = [x for x in line.split(" ") if "." not in x]
        
        reset_board()
        new_game = ChessGame()
        
        for move_san in moves_by_san:
            move = create_move_from_san(move_san)
            make_move_san(move_san)
            new_game.append_move(move)
        
        game_collection.append(new_game)
        log_index += 1


# Gets a string of the current game collection, delimited by spaces and newlines
def get_game_collection_text():
    game_collection_text = ""
    
    for game in game_collection:
        game_collection_text += f"{game.get_san_sequence()}\n"
    
    return game_collection_text


# Prints help information on available functions
def chess_help():
    print("""
    This script uses Stockfish and python-chess to generate chess openings.
    
    Run the following commands before using this script:

        pip install stockfish
        pip install chess
    
    The game_collection list is where the generated games are stored. Upon first
    running this script, the game_collection list has a single empty game.
    
    In order to add games, use expand_game_collection(int). The argument is the
    factor by with the game_collection grows. For example, the following line
    will add the 3 best moves to each game in the game_collection:
    
        expand_game_collection(3)
    
    You can now look at the games with the following line:
    
        get_game_collection_text()
    
    The game_collection grows very quickly, so it is only practical to expand
    the game_collection by small amounts just a few times. If you expand the
    game_collection by a factor of 3 just 5 times, there will already be up to
    243 games. This may not sound like a lot, but Stockfish is analyzing many
    moves ahead for each move of each game generated. Time will be the
    constraint.
    
    You can save your progress by saving the string from
    get_game_collection_text(). You can then load it at a later time with
    load_game_collection(str).
    
    Here is an example of generating continuations from the Ruy Lopez opening
    when playing as white.
    
        # Set Ruy Lopez opening
        make_move_san("e4")
        make_move_san("e5")
        make_move_san("Nf3")
        make_move_san("Nc6")
        make_move_san("Bb5")
        
        # Display the board with the stockfish method
        show_board()
        
        # Get black's best five moves
        expand_game_collection(5)
        
        # Get white's best response to each move
        expand_game_collection(1)
        
        # Get black's best three moves from each position
        expand_game_collection(3)
        
        # Get white's best response to each move
        expand_game_colleciton(1)
        
        # Save generated openings
        openings = get_game_collection_text()
        file_path = "C:\\\\Users\\\\Name\\\\Openings.txt"

        with open(file_path, "w") as file
            file.write(openings)
        
    """)
