from models.player import Player
from models.board import Board


START_MESSAGE = "Start rozgrywki"
END_MESSAGE = "Koniec rozgrywki"
MESSAGE_SEPARATOR = "=" * 40


class Game:
    def __init__(
        self,
        first_player: Player,
        second_player: Player,
        empty_sign: str | None = None,
        last_move_sign: str | None = None,
        rows: int = 8,
        columns: int = 8,
        grid: list[list[str]] | None = None,
    ):
        self.first_player = first_player
        self.first_player.direction = -1

        self.second_player = second_player
        self.second_player.direction = 1

        self.player_to_move = self.first_player
        self.winner: Player | None = None
        self.board = Board(rows, columns, grid, first_player.sign, second_player.sign, empty_sign, last_move_sign)
        self.rounds = 0

    def play(self):
        self.start()
        self.loop()
        self.end()

    def start(self):
        self.display_start()
        self.display_current_state()

    def loop(self):
        while self.winner is None:
            self.play_turn()

    def end(self):
        self.display_current_state()
        self.display_end()

    def display_start(self):
        print(MESSAGE_SEPARATOR)
        print(START_MESSAGE)

    def display_current_state(self):
        print(MESSAGE_SEPARATOR)
        self.board.display()
        print(MESSAGE_SEPARATOR)

    def display_end(self):
        if self.winner is not None:
            print(f"Wygrywa gracz {self.winner.sign}")
        print(f"Liczba rund: {self.rounds}")
        print(END_MESSAGE)
        print(MESSAGE_SEPARATOR)

    def play_turn(self):
        if not self.board.has_moves(self.player_to_move.sign):
            self.winner = (
                self.second_player
                if self.player_to_move is self.first_player
                else self.first_player
            )
            return

        move = self.player_to_move.pick_move(self.board)
        self.board = self.board.make_move(move)
        self.rounds += 1

        self.check_game_over(self.player_to_move)

        if self.winner is not None:
            return

        self.player_to_move = (
            self.second_player
            if self.player_to_move is self.first_player
            else self.first_player
        )

        self.display_current_state()

    def check_game_over(self, player: Player) -> None:
        winner_sign = self.board.check_winner_sign()

        if winner_sign == self.first_player.sign:
            self.winner = self.first_player
        elif winner_sign == self.second_player.sign:
            self.winner = self.second_player
