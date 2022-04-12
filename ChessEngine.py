#main engine to run game
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.moveFunctions = {
            "p": self.getPawnMoves, 
            "R": self.getRookMoves, 
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #coords for square where en passant capture possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True) #castle any side at beginning of game
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)] #logs rook moved


    #takes move as parameter and moves it
    #doesn't work with castling, pawn promo, en-passant
    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move) #log move to undo later or history
        self.whiteToMove = not self.whiteToMove #swap player turns
        #update kings location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #enpassant capture
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] == "--" #capturing the pawn

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        
        #update enpassantPossible var
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves rook 
                self.board[move.endRow][move.endCol+1] = "--" #erase base rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves rook 2 squares away
                self.board[move.endRow][move.endCol-2] = "--"

        self.enpassantPossibleLog.append(self.enpassantPossible)

        #update castling rights whenever a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))




    #undo last move
    def undoMove(self):
        if len(self.moveLog) != 0: #check if there is move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns
            #update kings position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            #undo castling rights
            self.castleRightsLog.pop() #remove new castle rights from move that we are undoing
            self.currentCastlingRights = self.castleRightsLog[-1]
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside castling
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else: #queenside castling
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

            self.checkmate = False
            self.stalemate = False

    #Update the castle rights given that move
    def updateCastleRights(self,move):
        if move.pieceCaptured == "wR":
            if move.endCol == 0: # left rook
                self.currentCastlingRights.wqs = False
            elif move.endCol == 7: # right rook
                self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0: # left rook
                self.currentCastlingRights.bqs = False
            elif move.endCol == 7: # right rook
                self.currentCastlingRights.bks = False
        
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.bks = False


    #all moves considering checks
    def getValidMoves(self):
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs) #copy current castle rights
        
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                #if knight, must capture knight or move king
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                #get rid of moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not(moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: #double check, king moves
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
                # add stalemate on repeated moves
        else:
            self.checkmate = False
            self.stalemate = False

        self.currentCastlingRights = tempCastleRights
        return moves
                
 
    #check if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    #see if enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponents turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turn back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square under attack
                return True
        return False

    
    #all moves not considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls appropriate move function based on piece
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keeps track of pins
        directions = ((-1, 0), (0, -1), (1,0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, no pin or check possible
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possible things could happen
                        #1) orthognoally away from king and piece is a rook
                        #2) diaganoloy away from king and piece is a bishop
                        #3) 1 square away diagonalloy from king and piece is a pawn
                        #4) any direction and piece is a queen
                        #5) any direction 1 square away and piece is a king (so king can't move to square next to king)
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "p" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == (): #no piece blocking thus check
                                in_check = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:
                            break #enemy piece not applying check 
                else:
                    break #off board

        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N": #enemy knight attacking king
                    in_check = True
                    checks.append((endRow, endCol, m[0], m[1]))
                return in_check, pins, checks


    #get all possible pawn moves for pawn @ rol, col, add moves to list
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--": # 1 sqaure pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2*moveAmount][c] == "--":
                    moves.append(Move((r, c), (r +2*moveAmount, c), self.board))
        if c-1 >= 0: # capture left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c-1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board))
                if (r+moveAmount, c-1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: #king is left of pawn
                            insideRange = range(kingCol + 1, c-1) #between king and pawn
                            outsideRange = range(c+1, 8) # between pawn and border
                        else: #king right of pawn
                            insideRange = range(kingCol-1, c, -1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--": # some piece beside enpassant blocks pawn
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassantMove = True))
        if c+1 < 8: # capture right
            if not piecePinned or pinDirection == (moveAmount, +1):
                if self.board[r+moveAmount][c+1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board))
                if (r+moveAmount, c+1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of pawn
                            insideRange = range(kingCol+1, c)
                            outsideRange = range(c+2, 8)
                        else: # king right of pawn
                            insideRange = range(kingCol-1, c+1, -1)
                            outsideRange = range(c-1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--": #piece blocks enpassant pawn
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square!= "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassantMove = True))



    #get all possible rook moves for pawn @ rol, col, add moves to list
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": # cant remove queen from pin
                    self.pins.remove(self.pins[i])
                break


        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #down, left, up, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #is on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #open space available
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece open
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break #checks another direction
                        else:  #friendly piece
                            break
                else: #off the board
                    break

    def getKnightMoves(self, r, c, moves): 
        piecePinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves: 
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #enemy or empty
                        moves.append(Move((r, c), (endRow, endCol), self.board))
    
    def getBishopMoves(self, r, c, moves): 
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break   
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #all diaganols
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8): #max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #is on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #open space available
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece open
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break #checks another direction
                        else:  #friendly piece
                            break 
                else: #off the board
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #not ally piece, empty/enemy
                # put king on end square and check for checks
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else: 
                        self.blackKingLocation = (endRow, endCol)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    
                    #put king back
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)


    #generate all valid castle moves for king at (r,c) and add to list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #cant castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and \
            not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))
    
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--" and \
            not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"       
        #castle move
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    #overides equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #add real chess notation here (future)
        if self.isPawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.isCastleMove:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.isEnpassantMove:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                self.endCol) + " e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                    self.endCol)
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare + "Q" if self.isPawnPromotion else endSquare

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare



