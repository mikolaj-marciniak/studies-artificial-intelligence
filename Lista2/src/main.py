from models.game import Game
from models.player import Player
from heuristics import (
    advancement_heuristic,
    furthest_pawn_heuristic,
    material_heuristic,
    pawn_structure_heuristic,
)
from minimax import get_visited_nodes, reset_visited_nodes
import sys
import time


DEPTH = 4
AVAILABLE_HEURISTICS = [
    furthest_pawn_heuristic,
    material_heuristic,
    pawn_structure_heuristic,
    advancement_heuristic,
]

if __name__ == "__main__":
    first_player = Player(sign="W", heuristics=AVAILABLE_HEURISTICS, depth=DEPTH)
    second_player = Player(sign="B", heuristics=AVAILABLE_HEURISTICS, depth=DEPTH)


    game = Game(first_player, second_player)
    reset_visited_nodes()
    start_time = time.perf_counter()
    game.play()
    end_time = time.perf_counter()

    print(f"Odwiedzone wezly: {get_visited_nodes()}", file=sys.stderr)
    print(f"Czas dzialania: {end_time - start_time:.4f}s", file=sys.stderr)
