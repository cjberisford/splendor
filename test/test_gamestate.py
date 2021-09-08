import settings
settings.TESTING_MODE = True # Force no UI interaction

import gamestate
import numpy as np
import pytest

@pytest.fixture
def test_gamestate():
  gs = gamestate.GameState()
  return gs

@pytest.fixture
def test_card(test_gamestate):
  card = gamestate.GameState.DevelopmentCard(1, "Red", 1, [1, 1, 1, 1, 1])
  return card

@pytest.fixture
def test_noble(test_gamestate):
  card = gamestate.GameState.NobleCard([0, 0, 0, 0, 0])
  return card

def test_add_human_player(test_gamestate):
  """Adds a human player to the game and counts number of players"""
  gamestate.GameState.remove_players(test_gamestate)
  gamestate.GameState.add_human_player(test_gamestate, 0)
  assert len(test_gamestate.players) == 1

def test_add_ai_player(test_gamestate):
  """Adds an AI player to the game and counts number of players"""
  gamestate.GameState.remove_players(test_gamestate)
  gamestate.GameState.add_ai_player(test_gamestate, 0)
  assert len(test_gamestate.players) == 1

def test_remove_players(test_gamestate):
  """Removes all players from game and verifies this has been done"""
  gamestate.GameState.remove_players(test_gamestate)
  assert len(test_gamestate.players) == 0

token_input_update = [
  ([0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]),
  ([0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]),
  ([4, 4, 4, 4, 4, 4], [-1, -1, -1, -1, -1, -1], [3, 3, 3, 3, 3, 3]),
]
@pytest.mark.parametrize("init, update, expected", token_input_update)
def test_allocate_tokens(test_gamestate, init, update, expected):
  """Test adding tokens to player pool"""
  gamestate.GameState.allocate_tokens(test_gamestate, 0, update) 
  generated = np.array(test_gamestate.players[0].tokens) + np.array(init)
  assert list(generated) == list(expected) 

def test_acquire_noble(test_gamestate, test_noble):
  """Test adding a noble to player hand"""
  gamestate.GameState.acquire_noble(test_gamestate, 0, test_noble, 0, None)
  assert len(test_gamestate.players[0].nobles) == 1

def test_acquire_card(test_gamestate):
  """Test adding development card to player hand"""
  test_gamestate.players[0].tokens = [10,10,10,10,10,10]
  gamestate.GameState.acquire_card(test_gamestate, 0, test_gamestate.development_cards[0][0], 0, "board", None) 
  assert len(test_gamestate.players[0].cards) == 1

def test_reserve_card(test_gamestate):
  """Reserve a development card. Check it has been added to player's hand"""
  gamestate.GameState.reserve_card(test_gamestate, 0, test_gamestate.development_cards[0][0], 0, None)
  assert len(test_gamestate.players[0].reservations) == 1

def test_deal_cards(test_gamestate):
  """Deal a single card from a deck"""
  _, test_flop = gamestate.GameState.deal_cards(test_gamestate, [], test_gamestate.development_cards[0], 1, 0)
  assert len(test_flop) == 1

def test_check_for_winner(test_gamestate):
  """Add high level development cards to player hand and check case"""
  for i in range(10):
    test_gamestate.players[0].tokens = [10,10,10,10,10,10]
    gamestate.GameState.acquire_card(test_gamestate, 0, test_gamestate.development_cards[1][2], 0, "board", None)
  gamestate.GameState.check_for_winner(test_gamestate)
  assert test_gamestate.final_round == True

def test_increment_turn(test_gamestate):
  """Check function correctly adds 1 to turn count"""
  gamestate.GameState.increment_turn(test_gamestate, None)
  assert test_gamestate.turn == 1
