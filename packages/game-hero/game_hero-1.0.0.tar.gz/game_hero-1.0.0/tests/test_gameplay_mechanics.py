import io
from contextlib import redirect_stdout

from game_hero.gameplay_mechanics import Gameplay
from game_hero.game_characters import Orderus, WildBeast


def test_gameplay_instance():
    """
    Tests singleton implementation for the Gameplay instances.
    """
    first_instance = Gameplay()
    second_instance = Gameplay()
    assert first_instance is second_instance, "Gameplay on different instances"


def test_simulate_round():
    """
    Tests round simulation and effects on health of the characters.
    """
    gameplay = Gameplay()
    orderus = Orderus()
    beast = WildBeast()
    pre_fight_orderus_health = orderus.health
    pre_fight_beast_health = beast.health
    gameplay.simulate_round(attacker=orderus, defender=beast)
    assert orderus.health == pre_fight_orderus_health, "Attacker health change"
    assert beast.health != pre_fight_beast_health, "Defender health unchanged!"


# noinspection PyProtectedMember
def test_simulate_fight():
    """
    Tests fight simulation
    Checks on health of the characters, win resolution and attack order.
    """
    gameplay = Gameplay()
    orderus = Orderus()
    beast = WildBeast()
    # Using a string buffer whilst redirecting STDOUT to it
    with io.StringIO() as buffer, redirect_stdout(buffer):
        # The actual simulation of the fight
        gameplay.simulate_fight(game_hero=orderus, magical_beast=beast)
        fight_output = buffer.getvalue()
    assert "wins" in fight_output, "None of the characters won"
    if f"{orderus.name} wins" in fight_output:
        assert orderus.health > beast.health, "Incorrect win based on health!"
        assert gameplay._last_attacker == orderus, "Incorrect attack order!"
    else:
        assert beast.health > orderus.health, "Incorrect win based on health!"
        assert gameplay._last_attacker == beast, "Incorrect attack order!"
