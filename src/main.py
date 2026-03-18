"""Ponto de entrada do jogo."""

from .game import FreeThrowGame


def main() -> None:
    game = FreeThrowGame()
    game.run()


if __name__ == "__main__":
    main()
