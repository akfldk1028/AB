from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime

app = FastAPI(title="Tic-Tac-Toe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Player(str, Enum):
    X = "X"
    O = "O"
    EMPTY = ""

class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"

class MoveRequest(BaseModel):
    row: int
    col: int
    player: Player

class GameState(BaseModel):
    id: str
    board: List[List[str]]
    current_player: Player
    status: GameStatus
    winner: Optional[Player] = None
    created_at: datetime
    updated_at: datetime
    moves_count: int

class GameResponse(BaseModel):
    game: GameState
    message: str

games_db: Dict[str, GameState] = {}

def create_empty_board() -> List[List[str]]:
    return [["" for _ in range(3)] for _ in range(3)]

def check_winner(board: List[List[str]]) -> Optional[Player]:
    for row in board:
        if row[0] and row[0] == row[1] == row[2]:
            return Player(row[0])
    
    for col in range(3):
        if board[0][col] and board[0][col] == board[1][col] == board[2][col]:
            return Player(board[0][col])
    
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return Player(board[0][0])
    
    if board[0][2] and board[0][2] == board[1][0] == board[2][1]:
        return Player(board[0][2])
    
    return None

def is_board_full(board: List[List[str]]) -> bool:
    return all(board[row][col] != "" for row in range(3) for col in range(3))

def get_game_status(board: List[List[str]]) -> tuple[GameStatus, Optional[Player]]:
    winner = check_winner(board)
    if winner == Player.X:
        return GameStatus.X_WINS, Player.X
    elif winner == Player.O:
        return GameStatus.O_WINS, Player.O
    elif is_board_full(board):
        return GameStatus.DRAW, None
    else:
        return GameStatus.IN_PROGRESS, None

@app.get("/")
async def root():
    return {"message": "Tic-Tac-Toe API", "version": "1.0.0", "endpoints": [
        "/games - GET all games",
        "/games/new - POST create new game",
        "/games/{game_id} - GET game state",
        "/games/{game_id}/move - POST make a move",
        "/games/{game_id}/reset - POST reset game",
        "/games/{game_id} - DELETE delete game"
    ]}

@app.get("/games", response_model=List[GameState])
async def get_all_games():
    return list(games_db.values())

@app.post("/games/new", response_model=GameResponse)
async def create_new_game():
    game_id = str(uuid.uuid4())
    now = datetime.now()
    
    game = GameState(
        id=game_id,
        board=create_empty_board(),
        current_player=Player.X,
        status=GameStatus.IN_PROGRESS,
        winner=None,
        created_at=now,
        updated_at=now,
        moves_count=0
    )
    
    games_db[game_id] = game
    
    return GameResponse(
        game=game,
        message=f"New game created with ID: {game_id}"
    )

@app.get("/games/{game_id}", response_model=GameState)
async def get_game(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return games_db[game_id]

@app.post("/games/{game_id}/move", response_model=GameResponse)
async def make_move(game_id: str, move: MoveRequest):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games_db[game_id]
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail=f"Game is already finished with status: {game.status}")
    
    if move.row < 0 or move.row > 2 or move.col < 0 or move.col > 2:
        raise HTTPException(status_code=400, detail="Invalid move: row and col must be between 0 and 2")
    
    if game.board[move.row][move.col] != "":
        raise HTTPException(status_code=400, detail="Invalid move: cell is already occupied")
    
    if move.player != game.current_player:
        raise HTTPException(status_code=400, detail=f"Invalid move: it's {game.current_player}'s turn")
    
    game.board[move.row][move.col] = move.player.value
    game.moves_count += 1
    game.updated_at = datetime.now()
    
    status, winner = get_game_status(game.board)
    game.status = status
    game.winner = winner
    
    if game.status == GameStatus.IN_PROGRESS:
        game.current_player = Player.O if game.current_player == Player.X else Player.X
        message = f"Move successful. Next player: {game.current_player}"
    else:
        if game.winner:
            message = f"Game over! {game.winner} wins!"
        else:
            message = "Game over! It's a draw!"
    
    games_db[game_id] = game
    
    return GameResponse(game=game, message=message)

@app.post("/games/{game_id}/reset", response_model=GameResponse)
async def reset_game(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    now = datetime.now()
    game = games_db[game_id]
    
    game.board = create_empty_board()
    game.current_player = Player.X
    game.status = GameStatus.IN_PROGRESS
    game.winner = None
    game.updated_at = now
    game.moves_count = 0
    
    games_db[game_id] = game
    
    return GameResponse(
        game=game,
        message="Game has been reset"
    )

@app.delete("/games/{game_id}")
async def delete_game(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del games_db[game_id]
    return {"message": f"Game {game_id} has been deleted"}

@app.get("/games/{game_id}/ai-move", response_model=GameResponse)
async def get_ai_move(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games_db[game_id]
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail=f"Game is already finished")
    
    def minimax(board: List[List[str]], depth: int, is_maximizing: bool, player: str) -> int:
        opponent = "X" if player == "O" else "O"
        
        winner = check_winner(board)
        if winner == player:
            return 10 - depth
        elif winner == opponent:
            return depth - 10
        elif is_board_full(board):
            return 0
        
        if is_maximizing:
            max_eval = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = player
                        eval_score = minimax(board, depth + 1, False, player)
                        board[i][j] = ""
                        max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = opponent
                        eval_score = minimax(board, depth + 1, True, player)
                        board[i][j] = ""
                        min_eval = min(min_eval, eval_score)
            return min_eval
    
    best_move = None
    best_score = float('-inf')
    ai_player = game.current_player.value
    
    for i in range(3):
        for j in range(3):
            if game.board[i][j] == "":
                game.board[i][j] = ai_player
                score = minimax(game.board, 0, False, ai_player)
                game.board[i][j] = ""
                
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    
    if best_move:
        move_request = MoveRequest(
            row=best_move[0],
            col=best_move[1],
            player=game.current_player
        )
        return await make_move(game_id, move_request)
    else:
        raise HTTPException(status_code=400, detail="No valid moves available")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)