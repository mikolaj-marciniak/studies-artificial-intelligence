from collections.abc import Callable
from models.board import Board


Heuristic = Callable[[Board, str], int]


def choose_heuristic(board: Board, player_sign: str, heuristics: list[Heuristic]) -> Heuristic:
    if not heuristics:
        raise ValueError("Lista heurystyk nie moze byc pusta")

    opponent_sign = board.get_opponent_sign(player_sign)
    starting_player_pieces = 2 * board.columns

    if (
        furthest_pawn_heuristic in heuristics
        and (
            board.is_furthest_piece_progress_at_least(player_sign, 0.7)
            or board.is_furthest_piece_progress_at_least(opponent_sign, 0.7)
        )
    ):
        return furthest_pawn_heuristic

    elif material_heuristic in heuristics and material_heuristic(board, player_sign) <= -(starting_player_pieces * 0.1):
        return material_heuristic

    elif pawn_structure_heuristic in heuristics and pawn_structure_heuristic(board, player_sign) <= -(starting_player_pieces * 0.25):
        return pawn_structure_heuristic

    elif advancement_heuristic in heuristics:
        return advancement_heuristic

    return heuristics[0]


def material_heuristic(board: Board, player_sign: str) -> int:
    opponent_sign = board.get_opponent_sign(player_sign)
    return board.count_pieces(player_sign) - board.count_pieces(opponent_sign)


def advancement_heuristic(board: Board, player_sign: str) -> int:
    opponent_sign = board.get_opponent_sign(player_sign)
    return board.get_total_progress(player_sign) - board.get_total_progress(opponent_sign)


def pawn_structure_heuristic(board: Board, player_sign: str) -> int:
    opponent_sign = board.get_opponent_sign(player_sign)

    player_pawns = board.count_pawn_types(player_sign)
    opponent_pawns = board.count_pawn_types(opponent_sign)

    player_score = 2 * player_pawns["strong"] + player_pawns["medium"] - player_pawns["weak"]
    opponent_score = 2 * opponent_pawns["strong"] + opponent_pawns["medium"] - opponent_pawns["weak"]

    return player_score - opponent_score


def furthest_pawn_heuristic(board: Board, player_sign: str) -> int:
    opponent_sign = board.get_opponent_sign(player_sign)
    return board.get_furthest_piece_progress(player_sign) - board.get_furthest_piece_progress(opponent_sign)
