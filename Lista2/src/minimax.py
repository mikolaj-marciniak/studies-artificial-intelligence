from math import inf

from heuristics import Heuristic, choose_heuristic
from models.board import Board
from models.move import Move


VISITED_NODES = 0


def reset_visited_nodes() -> None:
    global VISITED_NODES
    VISITED_NODES = 0


def get_visited_nodes() -> int:
    return VISITED_NODES


def minimax(
    player_sign: str,
    board: Board,
    heuristics: list[Heuristic],
    depth: int,
    heuristic: Heuristic | None = None,
) -> Move:
    if heuristic is None:
        heuristic = choose_heuristic(board, player_sign, heuristics)

    _, best_move = true_minimax(
        player_sign=player_sign,
        board=board,
        heuristic=heuristic,
        depth=depth,
        maximizing_sign=player_sign,
        maximizing_player=True,
    )

    if best_move is None:
        raise ValueError("Brak legalnych ruchow")

    return best_move


def true_minimax(
    player_sign: str,
    board: Board,
    heuristic: Heuristic,
    depth: int,
    maximizing_sign: str,
    maximizing_player: bool = True,
    alpha: float = -inf,
    beta: float = inf,
) -> tuple[float, Move | None]:
    global VISITED_NODES
    VISITED_NODES += 1

    winner_sign = board.check_winner_sign()
    if winner_sign == maximizing_sign:
        return inf, None
    if winner_sign is not None:
        return -inf, None
    
    if depth == 0:
        return heuristic(board, maximizing_sign), None
    
    if maximizing_player:
        max_eval = -inf
        best_move = None
        for move in board.get_moves(player_sign):
            next_board = board.make_move(move)
            eval, _ = true_minimax(
                player_sign=player_sign,
                board=next_board,
                heuristic=heuristic,
                depth=depth - 1,
                maximizing_sign=player_sign,
                maximizing_player=False,
                alpha=alpha,
                beta=beta,
            )
            if best_move is None or eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    
    else:
        min_eval = +inf
        best_move = None
        opponent_sign = board.get_opponent_sign(player_sign)
        for move in board.get_moves(opponent_sign):
            next_board = board.make_move(move)
            eval, _ = true_minimax(
                player_sign=player_sign,
                board=next_board,
                heuristic=heuristic,
                depth=depth - 1,
                maximizing_sign=player_sign,
                maximizing_player=True,
                alpha=alpha,
                beta=beta,
            )
            if best_move is None or eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move
