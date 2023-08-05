from game_hero.main_game import HeroGame


def test_start_game():
    """
    Tests output of the game as string
    """
    game_instance = HeroGame()
    game_output = game_instance.start_game()
    assert isinstance(game_output, str), "Output of the game is not string!"


def test_game_instance():
    """
    Tests singleton implementation for the HeroGame instances.
    """
    first_instance = HeroGame()
    second_instance = HeroGame()
    assert first_instance is second_instance, "Different instances for game!"
