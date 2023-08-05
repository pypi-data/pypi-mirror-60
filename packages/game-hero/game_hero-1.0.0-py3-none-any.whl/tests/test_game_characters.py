from game_hero.game_characters import Orderus, WildBeast
from game_hero.game_constants import ORDERUS_CONFIG, WILDBEAST_CONFIG


def test_orderus():
    """
    Tests if all the traits of Orderus are wihin expected ranges.
    """
    character = Orderus()
    assert character.name == ORDERUS_CONFIG["name"], "Incorrect name for char!"
    assert ORDERUS_CONFIG[
               "health"][0] <= character.health <= ORDERUS_CONFIG["health"][
        1], "Health is not between standard ranges"
    assert ORDERUS_CONFIG[
               "strength"][0] <= character.strength <= ORDERUS_CONFIG[
        "strength"][1], "strength is not between standard ranges"
    assert ORDERUS_CONFIG[
               "defence"][0] <= character.defence <= ORDERUS_CONFIG["defence"][
        1], "defence is not between standard ranges"
    assert ORDERUS_CONFIG[
               "speed"][0] <= character.speed <= ORDERUS_CONFIG["speed"][
        1], "speed is not between standard ranges"
    assert ORDERUS_CONFIG[
               "luck"][0] <= character.luck <= ORDERUS_CONFIG["luck"][
        1], "luck is not between standard ranges"


def test_wildbeast():
    """
    Tests if all the traits of WildBeast are wihin expected ranges.
    """
    character = WildBeast()
    assert character.name == WILDBEAST_CONFIG["name"], "Incorrect name!"
    assert WILDBEAST_CONFIG[
               "health"][0] <= character.health <= WILDBEAST_CONFIG["health"][
        1], "Health is not between standard ranges"
    assert WILDBEAST_CONFIG[
               "strength"][0] <= character.strength <= WILDBEAST_CONFIG[
        "strength"][1], "strength is not between standard ranges"
    assert WILDBEAST_CONFIG[
               "defence"][0] <= character.defence <= WILDBEAST_CONFIG[
        "defence"][1], "defence is not between standard ranges"
    assert WILDBEAST_CONFIG[
               "speed"][0] <= character.speed <= WILDBEAST_CONFIG["speed"][
        1], "speed is not between standard ranges"
    assert WILDBEAST_CONFIG[
               "luck"][0] <= character.luck <= WILDBEAST_CONFIG["luck"][
        1], "luck is not between standard ranges"
