"""
Game's main module.

The project developed covers a story game based on turn based combat,
where the game hero encounters a wild beast in the forest.

Game character's stats are taken into consideration on each turn,
whilst the hero also possesses some additional skills to help him in battle.
"""
import io
from contextlib import redirect_stdout
from tkinter import messagebox

from game_hero import game_characters
from game_hero import gameplay_mechanics


class HeroGame(metaclass=gameplay_mechanics.Singleton):
    """
    Hero Game instance.
    """
    def __init__(self):
        """
        This instance of the game is used in order to access the game,
        as well as simulate a fight between two characters.

        Exposes the `start_game()` method, which outputs the rounds
        of a turn based fight between the Game's Hero and a Wild Beast.
        """
        self._gameplay_functionality = gameplay_mechanics.Gameplay()

    def start_game(self):
        """
        Start of the game, therefore execution of the fight rounds
        between the Game's Hero and the encountered Wild Beast.

        Both of the Game's characters have their stats pre-initialized
        at the start of the game, with each turn subtracting health from
        the defender, based on attacker's strength and defender's defence stats

        The game ends when one of the player's health reaches zero.

        :return: Output of the game, with information from each turn.
        """
        # Using a string buffer whilst redirecting STDOUT to it
        with io.StringIO() as buffer, redirect_stdout(buffer):
            # The actual simulation of the fight
            self._gameplay_functionality.simulate_fight(
                game_hero=game_characters.Orderus(),
                magical_beast=game_characters.WildBeast())
            game_output = buffer.getvalue()

        print(game_output)
        # Show info window with the output of the game, besides command line.
        messagebox.showinfo("Hero Game", game_output)
        return game_output
