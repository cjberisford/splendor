import settings
settings.TESTING_MODE = True

import gamestate
import pytest
import player

@pytest.fixture
def test_gamestate():
  gs = gamestate.GameState()
  return gs

@pytest.fixture
def test_player(test_gamestate):
  player = test_gamestate.players[0]
  return player

@pytest.fixture
def test_card(test_gamestate):
  card = gamestate.GameState.DevelopmentCard(1, "Red", 1, [0, 0, 0, 0, 0])
  return card

@pytest.fixture
def test_noble(test_gamestate):
  card = gamestate.GameState.NobleCard([0, 0, 0, 0, 0])
  return card

def test_score(test_gamestate, test_player, test_noble, test_card):
  """Test score calculation by adding a noble and development card to player hand"""
  gamestate.GameState.acquire_card(test_gamestate, 0, [test_card], 0, "board", None) 
  gamestate.GameState.acquire_noble(test_gamestate, 0, test_noble, 0, None)
  test_player_score = player.Player.score(test_player)
  assert test_player_score == 4

def test_count_wealth(test_gamestate, test_player, test_card):
  """Test resource calculation function"""
  gamestate.GameState.acquire_card(test_gamestate, 0, [test_card], 0, "board", None) 
  assert player.Player.count_wealth(test_player) == [0, 0, 0, 1, 0, 0]

