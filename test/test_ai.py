import settings
settings.TESTING_MODE = True

import gamestate
import numpy as np
import pytest
import player

@pytest.fixture
def test_gamestate():
  return gamestate.GameState()

@pytest.fixture
def test_ai(test_gamestate):
  return player.AI("Player 0 (AI)", 0, [0, 0, 0, 0, 0, 0], [], [], [])

@pytest.fixture
def token_weights():
  return {"Onyx": "1", "Sapphire": "1", "Emerald": "1", "Ruby": "1", "Diamond": "1", "Gold": "1"}

@pytest.fixture
def test_card():
  return gamestate.GameState.DevelopmentCard(1, "Red", 1, [0, 0, 0, 0, 0])

def test_calculate_token_selection(test_ai, test_gamestate, token_weights):
  """Predict output of token selection """
  calculated_stack = player.AI.calculate_token_selection(test_ai, test_gamestate, token_weights)
  assert calculated_stack == [1, 1, 1, 0, 0, 0]

def test_acquire_tokens(test_ai, test_gamestate, token_weights):
  """Acquire tokens and test for expected result"""
  player.AI.acquire_tokens(test_ai, test_gamestate, token_weights, 0, None)
  assert test_gamestate.players[0].tokens == [1, 1, 1, 0, 0, 0]

def test_affordability_check(test_ai, test_gamestate):
  """Choose some card and test whether AI player can afford it"""
  tier_3_card = test_gamestate.development_cards[1][2][0]
  assert False == player.AI.affordability_check(test_ai, tier_3_card)

def test_acquire_card(test_ai, test_gamestate, test_card):
  """Add card to AI player hand"""
  card_dict = {test_card : 1}
  player.AI.acquire_card(test_ai, test_gamestate, card_dict, 0, None, "board")
  assert len(test_gamestate.players[0].cards) == 1

def test_reserve_card(test_ai, test_gamestate, test_card):
  """Add card to AI player hand"""
  player.AI.reserve_card(test_ai, test_gamestate, [test_card], {}, 0, None)
  assert len(test_gamestate.players[0].reservations) == 1
   