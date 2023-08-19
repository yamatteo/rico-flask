import pytest
from rich import print

from . import *

def test_a_game():
    game = Game.start_new(["Ada", "Bert", "Carl", "Dan"])
    first, second, third, fourth = [game.players[name] for name in game.play_order]

    assert first.is_governor
    with pytest.raises(RuleError):
        game.take_action(RoleAction(player_name=second.name, role_subclass="settler"))

    # First player take the settler role
    game.take_action(RoleAction(player_name=first.name, role_subclass="settler"))
    game.take_action(TileAction(player_name=first.name, tile_subclass="quarry"))
    with pytest.raises(RuleError):
        # Taking a quarry is a priviledge of the settler
        game.take_action(TileAction(player_name=second.name, tile_subclass="quarry"))
    tiles = [ tile.subclass for tile in game.exposed_tiles]
    game.take_action(TileAction(player_name=second.name, tile_subclass=tiles[0]))
    game.take_action(TileAction(player_name=third.name, tile_subclass=tiles[1]))
    game.take_action(TileAction(player_name=fourth.name, tile_subclass=tiles[2]))

    # Second player take the mayor role
    game.take_action(Action(subclass="Role", player_name=second.name, role_subclass="mayor"))
    assert second.people == 2  # Mayor's priviledge
    assert all(player.people == 1 for player in [first, third, fourth])  # Others get 1 person
    second.give_people(second.tiles[0], 1)
    second.give_people(second.tiles[1], 1)
    game.take_action(PeopleAction(player_name=second.name, whole_player=second))
 
    third.give_people(third.tiles[0], 1)
    game.take_action(PeopleAction(player_name=third.name, whole_player=third))
 
    fourth.give_people(fourth.tiles[0], 1)
    with pytest.raises(RuleError):
        # Check safeguards: fourth can't became third
        game.take_action(PeopleAction(player_name=fourth.name, whole_player=third))
    game.take_action(PeopleAction(player_name=fourth.name, whole_player=fourth))

    first.give_people(first.tiles[1], 1)  # Put the person in the quarry
    game.take_action(PeopleAction(player_name=first.name, whole_player=first))

    # Third player take the builder role
    game.take_action(RoleAction(player_name=third.name, role_subclass="builder"))
    # He can build the sugar mill because he has three money and the mill cost four, but he has builder's priviledge
    game.take_action(BuildingAction(player_name=third.name, building_subclass="sugar_mill"))

    # Integers are not referenced, but this is WEIRD!!!
    # TODO: understand why this happens
    first, second, third, fourth = [game.players[name] for name in game.play_order]
    assert third.money == 0
    with pytest.raises(RuleError):
        # Fourth can't, because he don't have the money
        game.take_action(BuildingAction(player_name=fourth.name, building_subclass="sugar_mill"))
    game.take_action(BuildingAction(player_name=fourth.name, building_subclass="construction_hut"))
    # First can build hospice (cost: 4) because he has a quarry
    game.take_action(BuildingAction(player_name=first.name, building_subclass="hospice"))
    game.take_action(BuildingAction(player_name=second.name, building_subclass="indigo_plant"))

    # Fourth player take the craftsman role
    game.take_action(RoleAction(player_name=fourth.name, role_subclass="craftsman"))

    # Integers are not referenced, but this is WEIRD!!!
    # TODO: understand why this happens
    first, second, third, fourth = [game.players[name] for name in game.play_order]
    assert third.corn == 1 and fourth.corn == 1
    game.take_action(CraftsmanAction(player_name=fourth.name, selected_good="corn"))
    assert fourth.corn == 2
    
    # Second round: second is governor
    assert second.is_governor
    game.take_action(RoleAction(player_name=second.name, role_subclass="prospector"))
    assert second.money == 2
    
    
    # Third take trader 
    game.take_action(RoleAction(player_name=third.name, role_subclass="trader"))
    game.take_action(TraderAction(player_name=third.name, selected_good="corn"))
    game.take_action(RefuseAction(player_name=fourth.name))
    game.take_action(RefuseAction(player_name=first.name))
    game.take_action(RefuseAction(player_name=second.name))
    assert third.money == 2  # One from selling (corn = 0 + trader's prviledge = 1) and one from the card bonus.
    assert game.market.corn == 1

    # Fourth take the captain role
    game.take_action(RoleAction(player_name=fourth.name, role_subclass="captain"))
    game.take_action(CaptainAction(player_name=fourth.name, selected_ship=7, selected_good="corn"))
    game.take_action(RefuseAction(player_name=first.name))
    game.take_action(RefuseAction(player_name=second.name))
    game.take_action(RefuseAction(player_name=third.name))
    game.take_action(RefuseAction(player_name=fourth.name))