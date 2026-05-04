from typing import TYPE_CHECKING

from models.move import Move

if TYPE_CHECKING:
    from models.player import Player


MIN_ROWS = 4
MIN_COLUMNS = 2

FIRST_PLAYER_SIGN = "W"
SECOND_PLAYER_SIGN = "B"
EMPTY_SIGN = "-"
LAST_MOVED_SIGN = "o"

FIRST_PLAYER_DIRECTION = -1
SECOND_PLAYER_DIRECTION = 1


class Board:
    def __init__(
        self,
        rows: int = 8,
        columns: int = 8,
        grid: list[list[str]] | None = None,
        first_player_sign: str | None = None,
        second_player_sign: str | None = None,
        empty_sign: str | None = None,
        last_moved_sign: str | None = None,
    ):
        self.first_player_sign = (
            FIRST_PLAYER_SIGN if first_player_sign is None else first_player_sign
        )
        self.second_player_sign = (
            SECOND_PLAYER_SIGN if second_player_sign is None else second_player_sign
        )
        self.empty_sign = EMPTY_SIGN if empty_sign is None else empty_sign
        self.last_moved_sign = (
            LAST_MOVED_SIGN if last_moved_sign is None else last_moved_sign
        )

        allowed_values = {
            self.first_player_sign,
            self.second_player_sign,
            self.empty_sign,
            self.last_moved_sign,
        }

        if len(allowed_values) != 4:
            raise ValueError("Znaki graczy i planszy musza byc rozne")

        if grid is None:
            if rows < MIN_ROWS:
                raise ValueError(f"Minimalna liczba wierszy: {MIN_ROWS}")
            if columns < MIN_COLUMNS:
                raise ValueError(f"Minimalna liczba kolumn: {MIN_COLUMNS}")

            self.rows = rows
            self.columns = columns
            self.grid: list[list[str]] = []

            for row_index in range(rows):
                row: list[str] = []
                for _ in range(columns):
                    if row_index in (0, 1):
                        row.append(self.second_player_sign)
                    elif row_index in (rows - 2, rows - 1):
                        row.append(self.first_player_sign)
                    else:
                        row.append(self.empty_sign)
                self.grid.append(row)
            return

        if not grid:
            raise ValueError("Plansza nie moze byc pusta")
        if len(grid) < MIN_ROWS:
            raise ValueError(f"Minimalna liczba wierszy: {MIN_ROWS}")
        if any(len(row) != len(grid[0]) for row in grid):
            raise ValueError("Wszystkie wiersze musza miec te sama dlugosc")
        if len(grid[0]) < MIN_COLUMNS:
            raise ValueError(f"Minimalna liczba kolumn: {MIN_COLUMNS}")
        if any(cell not in allowed_values for row in grid for cell in row):
            raise ValueError("Plansza zawiera niedozwolone znaki")
        if sum(cell == self.last_moved_sign for row in grid for cell in row) > 1:
            raise ValueError("Na planszy moze byc maksymalnie jedno pole ostatniego ruchu")

        self.rows = len(grid)
        self.columns = len(grid[0])
        self.grid = [row.copy() for row in grid]

    def display(self) -> None:
        for row in self.grid:
            print(" ".join(row))

    def _is_empty_cell(self, cell: str) -> bool:
        return cell in {self.empty_sign, self.last_moved_sign}

    def copy(self) -> "Board":
        return Board(
            grid=[row.copy() for row in self.grid],
            first_player_sign=self.first_player_sign,
            second_player_sign=self.second_player_sign,
            empty_sign=self.empty_sign,
            last_moved_sign=self.last_moved_sign,
        )

    def make_move(self, move: Move) -> "Board":
        if not self.is_legal_move(move):
            raise ValueError("Nielegalny ruch")

        piece = self.grid[move.from_row][move.from_col]

        new_board = self.copy()
        for row_index, row in enumerate(new_board.grid):
            for col_index, cell in enumerate(row):
                if cell == self.last_moved_sign:
                    new_board.grid[row_index][col_index] = self.empty_sign

        new_board.grid[move.from_row][move.from_col] = self.last_moved_sign
        new_board.grid[move.to_row][move.to_col] = piece
        return new_board

    def _is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.columns

    def get_opponent_sign(self, player_sign: str) -> str:
        if player_sign == self.first_player_sign:
            return self.second_player_sign
        if player_sign == self.second_player_sign:
            return self.first_player_sign
        raise ValueError("Nieznany znak gracza")

    def get_piece_progress(self, row: int, player_sign: str) -> int:
        if player_sign == self.first_player_sign:
            return (self.rows - 1) - row
        if player_sign == self.second_player_sign:
            return row
        raise ValueError("Nieznany znak gracza")

    def get_total_progress(self, player_sign: str) -> int:
        if player_sign not in {self.first_player_sign, self.second_player_sign}:
            raise ValueError("Nieznany znak gracza")

        total_progress = 0
        for row_index, row in enumerate(self.grid):
            for cell in row:
                if cell == player_sign:
                    total_progress += self.get_piece_progress(row_index, player_sign)

        return total_progress

    def get_furthest_piece_progress(self, player_sign: str) -> int:
        if player_sign not in {self.first_player_sign, self.second_player_sign}:
            raise ValueError("Nieznany znak gracza")

        furthest_progress = 0
        for row_index, row in enumerate(self.grid):
            for cell in row:
                if cell == player_sign:
                    piece_progress = self.get_piece_progress(row_index, player_sign)
                    furthest_progress = max(furthest_progress, piece_progress)

        return furthest_progress

    def is_furthest_piece_progress_at_least(self, player_sign: str, percentage: float) -> bool:
        if not 0 <= percentage <= 1:
            raise ValueError("Procent musi byc z przedzialu od 0 do 1")

        max_progress = self.rows - 1
        if max_progress <= 0:
            return False

        return self.get_furthest_piece_progress(player_sign) / max_progress >= percentage

    def is_piece_defended(self, row: int, col: int, player_sign: str) -> bool:
        if not self._is_on_board(row, col):
            return False
        if self.grid[row][col] != player_sign:
            return False

        if player_sign == self.first_player_sign:
            defender_row = row + 1
        elif player_sign == self.second_player_sign:
            defender_row = row - 1
        else:
            raise ValueError("Nieznany znak gracza")

        for defender_col in (col - 1, col + 1):
            if self._is_on_board(defender_row, defender_col):
                if self.grid[defender_row][defender_col] == player_sign:
                    return True

        return False

    def is_piece_attacked(self, row: int, col: int, player_sign: str) -> bool:
        if not self._is_on_board(row, col):
            return False
        if self.grid[row][col] != player_sign:
            return False

        opponent_sign = self.get_opponent_sign(player_sign)

        if opponent_sign == self.first_player_sign:
            attacker_row = row + 1
        else:
            attacker_row = row - 1

        for attacker_col in (col - 1, col + 1):
            if self._is_on_board(attacker_row, attacker_col):
                if self.grid[attacker_row][attacker_col] == opponent_sign:
                    return True

        return False

    def classify_piece(self, row: int, col: int, player_sign: str) -> str:
        defended = self.is_piece_defended(row, col, player_sign)
        attacked = self.is_piece_attacked(row, col, player_sign)

        if defended and not attacked:
            return "strong"
        if attacked and not defended:
            return "weak"
        return "medium"

    def count_pawn_types(self, player_sign: str) -> dict[str, int]:
        if player_sign not in {self.first_player_sign, self.second_player_sign}:
            raise ValueError("Nieznany znak gracza")

        counts = {"strong": 0, "medium": 0, "weak": 0}

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if cell == player_sign:
                    pawn_type = self.classify_piece(row_index, col_index, player_sign)
                    counts[pawn_type] += 1

        return counts

    def _get_moves_for_square(self, row: int, col: int, player_sign: str, direction: int) -> list[Move]:
        moves: list[Move] = []
        next_row = row + direction

        if not self._is_on_board(next_row, col):
            return moves

        if self._is_empty_cell(self.grid[next_row][col]):
            moves.append(
                Move(
                    from_row=row,
                    from_col=col,
                    to_row=next_row,
                    to_col=col,
                )
            )

        for next_col in (col - 1, col + 1):
            if not self._is_on_board(next_row, next_col):
                continue
            destination = self.grid[next_row][next_col]
            if destination == player_sign:
                continue

            moves.append(
                Move(
                    from_row=row,
                    from_col=col,
                    to_row=next_row,
                    to_col=next_col,
                )
            )

        return moves

    def is_legal_move(self, move: Move) -> bool:
        if not self._is_on_board(move.from_row, move.from_col):
            return False
        if not self._is_on_board(move.to_row, move.to_col):
            return False

        piece = self.grid[move.from_row][move.from_col]
        if piece not in {self.first_player_sign, self.second_player_sign}:
            return False

        opponent_sign = self.get_opponent_sign(piece)
        row_difference = move.to_row - move.from_row
        col_difference = move.to_col - move.from_col
        expected_direction = (
            FIRST_PLAYER_DIRECTION
            if piece == self.first_player_sign
            else SECOND_PLAYER_DIRECTION
        )

        if row_difference != expected_direction:
            return False
        if col_difference not in {-1, 0, 1}:
            return False

        destination = self.grid[move.to_row][move.to_col]

        if col_difference == 0:
            return self._is_empty_cell(destination)

        return destination == opponent_sign or self._is_empty_cell(destination)

    def get_moves(self, player_sign: str) -> list[Move]:
        if player_sign == self.first_player_sign:
            player_direction = FIRST_PLAYER_DIRECTION
        elif player_sign == self.second_player_sign:
            player_direction = SECOND_PLAYER_DIRECTION
        else:
            raise ValueError("Nieznany znak gracza")

        all_moves: list[Move] = []
        for row in range(self.rows):
            for col in range(self.columns):
                if self.grid[row][col] == player_sign:
                    all_moves.extend(
                        self._get_moves_for_square(row, col, player_sign, player_direction)
                    )

        return all_moves

    def count_pieces(self, player_sign: str) -> int:
        if player_sign not in {self.first_player_sign, self.second_player_sign}:
            raise ValueError("Nieznany znak gracza")

        return sum(cell == player_sign for row in self.grid for cell in row)

    def has_moves(self, player_sign: str) -> bool:
        return bool(self.get_moves(player_sign))

    def check_win(self, player: "Player") -> bool:
        if player.sign == self.first_player_sign:
            row_to_check = 0
        else:
            row_to_check = self.rows - 1

        for column in range(self.columns):
            if self.grid[row_to_check][column] == player.sign:
                return True
        return False

    def check_winner_sign(self) -> str | None:
        if any(cell == self.first_player_sign for cell in self.grid[0]):
            return self.first_player_sign
        if any(cell == self.second_player_sign for cell in self.grid[self.rows - 1]):
            return self.second_player_sign
        if self.count_pieces(self.first_player_sign) == 0:
            return self.second_player_sign
        if self.count_pieces(self.second_player_sign) == 0:
            return self.first_player_sign
        return None
