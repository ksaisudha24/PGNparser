import re

def setup():
	squares = [y + x for x in "12345678" for y in "abcdefgh"]
	start = "RNBQKBNR"+ "P" * 8 + " " * 32+ "p" * 8 + "rnbqkbnr"
	board_view = dict(zip(squares, start))
	piece_view = {_:[] for _ in "BKNPQRbknpqr"}
	for sq in board_view:
		piece = board_view[sq]
		if piece != " ":
			piece_view[piece].append(sq)
	return board_view, piece_view

def pgn_to_moves(game_file):
	raw_pgn = " ".join([line.strip() for line in open(game_file)])
	comments_marked = raw_pgn.replace("{", "<").replace("}", ">")
	STRC = re.compile("<[^>]*>")
	comments_removed = STRC.sub(" ", comments_marked)
	STR_marked = comments_marked.replace("[", "<").replace("]", ">")
	str_removed = STRC.sub(" ", STR_marked)
  MOVE_NUM = re.compile("[1-9][0-9]* *\. ")
  just_moves = [_.strip() for _ in MOVE_NUM.split(str_removed)]
  last_move = just_moves[-1]
  RESULT = re.compile("(1-0|0-1|1/2-1/2)")
  last_move = RESULT.sub("", last_move)
  moves = just_moves[:-1]+[last_move]
  return [_ for _ in moves if len(_) > 0 ]

def pre_process_a_move(move):
	wmove, bmove = move.split()
	if wmove[0] in "abcdefgh":
		wmove = "P" + wmove
	if bmove[0] in "abcdefgh":
		bmove = "p" + bmove
	else:
		bmove = bmove.lower()
	return wmove, bmove

def pre_process_moves(moves):
	return [pre_process_a_move(move) for move in moves[:-1]]

def is_valid_move(piece, start_position, end_position, colour):
    
    def is_valid_king_move(file1, file2, rank1, rank2, colour):
        return abs(file1 - file2) <= 1 and abs(rank1 - rank2) <= 1

    def is_valid_bishop_move(file1,file2,rank1,rank2,colour):
        return abs(file1 - file2) == abs(rank1 - rank2)

    def is_valid_rook_move(file1, file2, rank1, rank2, colour):
        if file1 == file2:
            for rank in range(rank1 + 1, rank2):
                if board_view[chr(file1) + str(rank)] != ' ':
                    return False
        if rank1 == rank2:
            for file_ in range(file1+1,file2):
                if board_view[chr(file_)+str(rank1)] != ' ':
                    return False
        return file1 == file2 or rank1 == rank2
    def is_valid_queen_move(file1, file2, rank1, rank2, colour):
        return is_valid_rook_move(file1, file2, rank1, rank2, colour) or is_valid_bishop_move(file1, file2, rank1, rank2, colour)

    def is_valid_knight_move(file1, file2, rank1, rank2, colour):
        return (abs(file2 - file1), abs(rank2 - rank1)) in [(1, 2), (2, 1)]

    def is_valid_pawn_move(file1, file2, rank1, rank2, colour):
         if colour == 'W':
             return file2 == file1 and (rank2 - rank1 == 1 or rank2 - rank1 == 2)
        return file2 == file1 and (rank1 - rank2 == 1 or rank1 - rank2 == 2)

    def is_valid_position(file1, file2, rank1, rank2):
        return not (file1 == file2 and rank1 == rank2)

    file1, file2, rank1, rank2 = start_position[0], end_position[0], int(start_position[1]), int(end_position[1])
    if is_valid_position(file1, file2, rank1, rank2):
        return {'K':is_valid_king_move, 'Q':is_valid_queen_move, 'B':is_valid_bishop_move, 'N':is_valid_knight_move, 'P':is_valid_pawn_move} [piece](ord(file1), ord(file2),rank1,rank2,colour)
    else:
    	return False

def castling(board_view, piece_view, king, rook, king_intial_position, king_final_position, rook_intial_position, rook_final_position):
    
    board_view[king_intial_position] = ' '
    board_view[king_final_position] = king
    piece_view[king] = [king_final_position]

    board_view[rook_intial_position] = ' '
    board_view[rook_final_position] = rook
    piece_view[rook][piece_view[rook].index(rook_intial_position)] = rook_final_position

def king_castling(board_view, piece_view, colour):
	if colour == 'W':
		return castling(board_view, piece_view, 'K', 'R', 'e1', 'g1', 'f1', 'h1')
    else:
    	return castling(board_view, piece_view, 'k', 'r', 'e8', 'g8', 'f8', 'h8')

def queen_castling(board_view, piece_view, colour):
	if colour == 'W':
		return castling(board_view, piece_view, 'K', 'R', 'e1', 'c1', 'a1', 'd1')
    else:
    	return castling(board_view, piece_view, 'k', 'r', 'e8', 'c8', 'a8', 'd8')
    
 def en_passant(board_view, piece_view, piece, final_position, colour):

	captured_pawn_position = chr(ord(final_position[0]) + 1) + final_position[1]
	board_view[final_position] = board_view[captured_pawn_position]
	board_view[captured_pawn_position] = ' '
	piece_view[board_view[final_position]] = final_position

def make_pawn_move(board_view, piece_view, piece, extra, final_position, colour):
    
    if 'x' in extra:
        if piece.lower() == 'p' and board_view[final_position] == ' ':
            board_view, piece_view = en_passant(board_view, piece_view, piece, final_position, colour)
        return initial_file_given(board_view, piece_view, piece, extra, final_position, colour)
    return new_piece_view(board_view, piece_view, piece, final_position, colour)

def capture(board_view, piece_view, piece, extra, final_position, colour):
   
    piece_captured = board_view[final_position]
    board_view[final_position] = ' '
    piece_view[piece_captured].pop(piece_view[piece_captured].index(final_position))
    
    if extra[0] in "abcdefgh":
        return board_view,piece_view
    return new_piece_view(board_view, piece_view, piece, final_position, colour)

def initial_file_given(board_view, piece_view, piece, extra, final_position, colour):
    if 'x' in extra:
        board_view, piece_view = capture(board_view, piece_view, piece, extra, final_position, colour)
        extra = extra.replace('x', '')
    
    for position in piece_view[piece]:
        if position[0] == extra:
            return update_piece_view(board_view, piece_view, piece, piece_view[piece].index(position), final_position, colour)
        
def update_piece_view(board_view, piece_view, piece, position, final_position, colour):
    board_view[piece_view[piece][position]] = ' '
    board_view[final_position] = piece
    piece_view[piece][position] = final_position
    return board_view, piece_view


def new_piece_view(board_view, piece_view, piece, final_positon, colour):
    for positon in range(0, len(piece_view[piece])):
        if is_valid_move(piece.upper(), piece_view[piece][positon], final_position, colour):
            return update_piece_view(board_view, piece_view, piece, positon, final_position, colour)

board_view, piece_view=setup()
moves = pre_process_moves(pgn_to_moves("pgn.txt"))
for move in moves:
    colour='W'
    for mov in move:
        mov = mov.replace('+', '')
        piece, extra, final_positon = mov[0], mov[1:-2], mov[-2:]
        
        if mov == 'O-O' or mov =='o-o':
            board_view, piece_view = king_castling(board_view, piece_view, colour)
        
        elif mov =='O-O-O' or mov=='o-o-o':
            board_view, piece_view = queen_castling(board+view, piece_view, colour)
        elif  extra != '':
            if piece.lower() =='p':
                board_view, piece_view = make_pawn_move(board_view, piece_view, piece, extra, final_position, colour)
            else:
                if  extra == 'x':
                    board_view, piece_view = capture(board_view, piece_view, piece, extra, final_position, colour)
                else :
                    board_view, piece_view = initial_file_given(board_view, piece_view, piece, extra, final_position, colour)
                    
        else:
            board_view, piece_view = new_piece_view(board_view, piece_view, piece, final_positon, colour)
        colour ='B'
 print(piece_view)
