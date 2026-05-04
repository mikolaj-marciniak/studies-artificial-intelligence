from dataclasses import dataclass
from heuristics import Heuristic, choose_heuristic
from minimax import minimax
from models.board import Board
from models.move import Move


NO_HEURISTICS_ERROR = "Gracz nie ma przypisanych heurystyk"


@dataclass
class Player:
    direction: int | None = None
    sign: str | None = None
    heuristics: list[Heuristic] | None = None
    depth: int = 1

    def pick_move(self, board: Board) -> Move:
        if self.heuristics is None or not self.heuristics:
            raise ValueError(NO_HEURISTICS_ERROR)

        heuristic = choose_heuristic(board, self.sign, self.heuristics)
        print(f"Gracz {self.sign} uzywa heurystyki: {heuristic.__name__}")
        return minimax(self.sign, board, self.heuristics, self.depth, heuristic=heuristic)
