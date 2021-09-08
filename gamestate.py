
"""
COM3610 - Dissertation Project
aca18cjb, (c) Chris Berisford 2021

gamestate.py - Contains all information related to the gamestate
"""

import random, math, csv, settings
import player as p, numpy as np

# Disables calls to UI for testing
TESTING_MODE = settings.TESTING_MODE

class GameState:
    def __init__(self, n_humans, n_total, ai_type):
        """Sets up gameboard, deals all cards and adds players"""
        development_cards = []
        noble_cards = []
        self.players = []
        self.dealt = []
        self.ai_type = ai_type

        # add players to game
        for x in range(n_humans):
            self.add_human_player(x)

        for x in range(n_total - n_humans):
            self.add_ai_player(x, self.ai_type)

        # import, shuffle and deal_cards development cards
        with open('data/development_cards.csv', mode='r')as file:
            csvFile = csv.reader(file)
            next(csvFile)
            for lines in csvFile:
                level = int(lines[0])
                gemType = lines[1]
                pointValue = int(lines[2])
                purchaseCost = [int(lines[3]), int(lines[4]), int(
                    lines[5]), int(lines[6]), int(lines[7])]
                add_card = self.DevelopmentCard(
                    level, gemType, pointValue, purchaseCost)
                development_cards.append(add_card)

        random.shuffle(development_cards)
        dev_1_deck = [card for card in development_cards if card.level == 1]
        dev_2_deck = [card for card in development_cards if card.level == 2]
        dev_3_deck = [card for card in development_cards if card.level == 3]

        dev_1_deck, dev_1_flop = self.deal_cards([], dev_1_deck, 5, 0)
        dev_2_deck, dev_2_flop = self.deal_cards([], dev_2_deck, 5, 0)
        dev_3_deck, dev_3_flop = self.deal_cards([], dev_3_deck, 5, 0)

        # import, shuffle and deal_cards noble cards
        with open('data/noble_cards.csv', mode='r')as file:
            csvFile = csv.reader(file)
            next(csvFile)
            for lines in csvFile:
                prerequisites = [int(lines[0]), int(lines[1]), int(
                    lines[2]), int(lines[3]), int(lines[4])]
                add_card = self.NobleCard(prerequisites)
                noble_cards.append(add_card)

        random.shuffle(noble_cards)
        noble_deck, noble_flop = self.deal_cards(
            [], noble_cards, len(self.players) + 1, 0)

        dev_card_flop = [dev_1_flop, dev_2_flop, dev_3_flop]
        dev_card_deck = [dev_1_deck, dev_2_deck, dev_3_deck]
        development_cards = [dev_card_deck, dev_card_flop]

        noble_card_flop = noble_flop
        noble_card_deck = noble_deck
        noble_cards = [noble_card_deck, noble_card_flop]

        if len(self.players) == 2:
            token_pool = [4, 4, 4, 4, 4, 5]
        elif len(self.players) == 3:
            token_pool = [5, 5, 5, 5, 5, 5]
        else:
            token_pool = [7, 7, 7, 7, 7, 5]

        self.noble_cards = noble_cards
        self.skipNobleCheck = False
        self.token_pool = token_pool
        self.temp_pool = [0, 0, 0, 0, 0, 0]
        self.development_cards = development_cards
        self.turn = 0
        self.final_round = False
        self.game_summary = self.GameSummary(self)
        self.round_number = int((math.floor(self.turn) / len(self.players)) + 1)

    def __str__(self):
        return "TURN #{} || Player Count: {}, Cards In Play: {}, Nobles In Play: {}, Token Pool: {}".format(
            self.turn,
            len(self.players),
            len(self.development_cards[1][0] + self.development_cards[1]
                [1] + self.development_cards[1][2]),
            len(self.noble_cards[1]),
            self.token_pool
        )

    def add_human_player(self, id):
        """Adds human player to the game"""
        # print("Human player added.")
        self.players.append(p.Player("Player " + str(id + 1),
                                     id, [0, 0, 0, 0, 0, 0], [], [], []))

    def add_ai_player(self, id, ai_type):
        """Adds AI player to the game"""
        # print("AI player added.")
        self.players.append(p.AI("Player " + str(settings.NUMBER_OF_PLAYERS +
                                                 id) + " (AI)", settings.NUMBER_OF_PLAYERS + id, [0, 0, 0, 0, 0, 0], [], [], [], ai_type))

    def remove_players(self):
        """Removes all current players from game"""
        self.players.clear()

    def allocate_tokens(self, player_id, stack):
        """Adds tokens to player pool"""

        updated_player_assets = []
        player = self.players[player_id]

        # add to player assets
        zip_object = zip(player.tokens, stack)
        for x, y in zip_object:
            updated_player_assets.append(x + y)

        # update token pools
        self.temp_pool = [0, 0, 0, 0, 0, 0]
        self.players[player_id].tokens = updated_player_assets

    def disable_ui(self, UI):
        """Disables class interaction with UI"""
        if not TESTING_MODE:
            UI.links_enabled = False
            UI.update_gui()

    def acquire_noble(self, player, card, index, UI):
        """Adds noble to player hand"""
        difference = []
        is_affordable = False

        zip_object = zip(
            self.players[player].count_wealth(), card.prerequisites)
        for x, y in zip_object:
            difference.append(x - y)

        if min(difference) >= 0:
            is_affordable = True

        if is_affordable:
            card_to_append = self.noble_cards[1][index]
            self.noble_cards[1].pop(index)
            self.players[player].nobles.append(card_to_append)
            if not TESTING_MODE:
                UI.display_message(
                    "> Player " + str(player + 1) + " has acquired a noble.")
                UI.nobles_enabled = False
                UI.links_enabled = True
            self.skipNobleCheck = True
            self.increment_turn(UI)

        else:
            if not TESTING_MODE:
                UI.display_message(
                    "[Error] You do not meet the requirements for this noble")

    def acquire_card(self, player_id, deck, index, calledFrom, UI):
        """Moves card to player ownership pool"""

        player = self.players[player_id]
        player_tokens = np.array(player.tokens)
        holding_tokens = np.array(player.holding_tokens)
        dev_card_contribution = np.array(player.count_wealth())
        raw_card_cost = np.array(deck[index].purchaseCost + [0])

        # Apply gold token discount
        effective_wealth = player_tokens + holding_tokens
        # Apply development card discount
        effective_cost = raw_card_cost - dev_card_contribution
        # This cannot go below zero
        effective_cost = [i if i > 0 else 0 for i in effective_cost]

        if np.min(effective_wealth - effective_cost) >= 0:

            # Player can afford card - have they used any gold?
            if np.sum(holding_tokens) > 0:
                self.token_pool[5] += np.sum(holding_tokens)

                req_holding_tokens = player_tokens - effective_cost
                req_holding_tokens = np.array(
                    [abs(i) if i < 0 else 0 for i in req_holding_tokens])
                redundant_holding_tokens = holding_tokens - req_holding_tokens

                # Convoluted - hope this works! (seems to, so far)
                player.tokens[5] += np.sum(redundant_holding_tokens)
                self.token_pool += redundant_holding_tokens
                self.token_pool -= holding_tokens
                self.token_pool[5] -= np.sum(redundant_holding_tokens)

            # Add spent tokens to game pool
            self.token_pool = np.array(self.token_pool) + effective_cost

            # Remove spent tokens from player hand (can't go below zero)
            updated_player_tokens = np.array(player.tokens) - effective_cost
            updated_player_tokens = [
                i if i > 0 else 0 for i in updated_player_tokens]
            player.tokens = updated_player_tokens

            # Add session log entry
            round_number = math.floor(self.turn / len(self.players)) + 1
            self.game_summary.turn_data[player_id][round_number] = "B" + str(deck[index].level)

            # Add card to player hand
            player.cards.append(deck[index])

            # Remove card from its deck
            level = deck[index].level
            del(deck[index])

            # Redeal if necessesary, i.e. not purchased from player reservations
            if calledFrom == "board":
                if not TESTING_MODE:
                    UI.display_message(
                        "> Player " + str(player_id + 1) + " acquired a card.")
                flop = self.development_cards[1][level-1]
                drawfrom = self.development_cards[0][level-1]
                self.development_cards[0][level-1], self.development_cards[1][level -
                                                                              1] = self.deal_cards(flop, drawfrom, 1, index)
            else:
                if not TESTING_MODE:
                    UI.display_message(
                        "> Player " + str(player_id + 1) + " acquired a card form their reservations.")

            # Pay holding tokens that were spent, otherwise no change made to player assets
            # Reset holding tokens and advance turn
            self.players[player_id].holding_tokens = [0, 0, 0, 0, 0, 0]
            self.noble_requirements_met(player, player_id, UI)

        else:
            # Player cannot afford card

            # Convert holding tokens to gold tokens and refund to player
            tokens_to_add = sum(player.holding_tokens)
            self.players[player_id].tokens[5] += tokens_to_add

            # Reset holding tokens
            player.holding_tokens = [0, 0, 0, 0, 0, 0]

            # Inform player
            if not TESTING_MODE:
                UI.display_message("[Error] You cannot afford this card.")
                UI.redraw_player(player_id)

    def reserve_card(self, player, deck, index, UI):
        """Moves card to player reservation pool"""

        # Calculate value threshold to be categorised as aggressive
        cardToReserve = deck[index] 

        # Need to determine weights first
        aggressive_reservation = False
        if index != 0:
            for p in self.players:
                p.get_probabilities(self.dealt)
                p.get_weights(self)
                p.get_desired_types()
                v = list(p.w_card.values())
                value_threshold = max([np.mean(v) + (1.5 * np.std(v)), 0])
                if p.w_card[cardToReserve] >= value_threshold:
                    aggressive_reservation = True

        self.players[player].reservations.append(deck[index])
        level = deck[index].level
        del(deck[index])
        flop = self.development_cards[1][level-1]
        drawfrom = self.development_cards[0][level-1]

        self.development_cards[0][level-1], self.development_cards[1][level -
                                                                      1] = self.deal_cards(flop, drawfrom, 1, index)
        
        # Add to session log
        round_number = math.floor(self.turn / len(self.players)) + 1

        # What kind of reservation do we classify this as?
        if aggressive_reservation:
            self.game_summary.turn_data[player][round_number] = "RA"
            self.game_summary.risk_data[player]["R2"] += 1
        else:
            self.game_summary.turn_data[player][round_number] = "RB"
            self.game_summary.risk_data[player]["R1"] += 1


        # Check if player could have afforded any cards
        affordable_cards, affordable_reservations = self.players[player].get_all_affordable_cards()
        if len(affordable_cards) > 0 or len(affordable_reservations) > 0:
            # This is a risk, so should be recorded
            self.game_summary.risk_data[player]["R4"] += 1


        # Is the card facedown?
        if index == 0:
            # Facedown reservation
            self.game_summary.risk_data[player]["R3"] += 1

        message = ""
        available_capacity = 10 - sum(self.players[player].tokens)

        if self.token_pool[5] > 0:
            if available_capacity > 0:
                message = "> Player " + \
                    str((self.turn % len(self.players)) + 1) + \
                    " reserved a card and acquired a gold token."
                self.allocate_tokens(player, [0, 0, 0, 0, 0, 1])
                self.token_pool[5] -= 1
            else:
                message = "> Player " + str((self.turn % len(self.players)) + 1) + \
                    " reserved a card but did not acquire a gold token as they have reached their token limit."
        else:
            message = "> Player " + str((self.turn % len(self.players)) + 1) + \
                " reserved a card but did not acquire a gold token as there are none left."

        if not TESTING_MODE:
            UI.display_message(message)

    def deal_cards(self, flop, deck, n, beginAt):
        """Deals n cards from deck. Returns deck, flop"""
        for card in deck[:n]:
            if isinstance(card, self.DevelopmentCard):
                self.dealt.insert(0, card)
        return deck[n:], flop[:beginAt] + deck[:n] + flop[beginAt:]

    def check_for_winner(self):
        """Check if any player has achieved victory condition"""
        for player in self.players:
            if player.score() >= settings.VICTORY_POINTS_REQUIRED:
                self.final_round = True

    def start_game(self, UI):
        if isinstance(self.players[0], p.AI):
            p.AI.evaluation(self.players[0], self, UI)

    def end_game(self, UI):
        """Calculates game winner and prints out message"""

        # We no longer need this
        self.disable_ui(UI)

        # Get all players that have met victory condition
        player_scores = [x.score() for x in self.players]
        winner = [i for i, x in enumerate(
            player_scores) if x == max(player_scores)]

        # Separate winning players by number of development cards held
        if len(winner) > 1:
            tie_break = {}
            for id in winner:
                tie_break[id] = len(self.players[id].cards)
            tie_break = dict(
                sorted(tie_break.items(), key=lambda item: item[1]))

            winner = list(tie_break.keys())[0]
        else:
            winner = winner[0]

        # Update game summary, print message, and close instance
        self.game_summary.winning_player = winner + 1
        self.game_summary.rounds = math.floor(self.turn / len(self.players))

        if not TESTING_MODE:
            UI.display_message(
                "Game Over! Congratulations player " + str(winner + 1))
            UI.display_message(
                "Please look in program directory for 'session_data.txt' and email it to cjberisford@live.co.uk. Thank you!")

        self.game_summary.game_completed = True
        UI.root.update()
        UI.root.destroy()

    def noble_requirements_met(self, player, player_id, UI):
        """determine if player has met requirements for a noble"""

        potential_matches = []

        player_wealth = player.count_wealth()
        for noble in self.noble_cards[1]:
            difference = []
            zip_object = zip(player_wealth, noble.prerequisites)
            for x, y in zip_object:
                if y > 0:
                    difference.append(x - y)
            if min(difference) >= 0:
                potential_matches.append(noble)

        if len(potential_matches) > 0:
            if not TESTING_MODE:
                UI.display_message("> Player " + str(player_id + 1) +
                                   " has been visited by one or more nobles. Please select a noble tile.")
                UI.nobles_enabled = True
            self.disable_ui(UI)
        else:
            self.increment_turn(UI)

    def increment_turn(self, UI):
        """Increases turn count by one as well as performing end of turn checks"""

        player_id = self.turn % len(self.players)
        player = self.players[player_id]
        next_player_id = (self.turn + 1) % len(self.players)
        next_player = self.players[next_player_id]

        # Increase turn counter
        self.turn += 1

        # Check for winner if start of new round
        if not TESTING_MODE:
            if self.turn % len(self.players) == 0:
                self.check_for_winner()
        # Has anyone won?
        if self.final_round == True:
            self.end_game(UI)
            
        # Is the AI stuck?
        elif self.game_summary.errors >= 50:
            UI.root.update()
            UI.root.destroy()
        else:
            if not TESTING_MODE:
                UI.update_gui()
                # Check for AI turn
                if isinstance(next_player, p.AI):
                    p.AI.evaluation(self.players[next_player_id], self, UI)

    class DevelopmentCard:
        def __init__(self, level, gemType, pointValue, purchaseCost):
            self.level = level
            self.gemType = gemType
            self.pointValue = pointValue
            self.purchaseCost = purchaseCost

        def __str__(self):
            return "Development Card (Level: {}, Gem Type: {}, Point Value: {}, Cost: {})".format(
                self.level,
                self.gemType,
                self.pointValue,
                self.purchaseCost
            )

    class NobleCard:
        def __init__(self, prerequisites):
            self.prerequisites = prerequisites

        def __str__(self):
            return "Noble Card (Prerequisites: {})".format(self.prerequisites)

    class GameSummary:
        def __init__(self, gamestate):
            self.ai_type = gamestate.ai_type
            self.rounds = 0
            self.risk_counter = 0
            self.winning_player = 0
            self.errors = 0
            self.game_completed = False

            self.turn_data = {}
            for player in gamestate.players:
                self.turn_data[player.id] = {}
                # "B1": 0, # Buy tier 1 development card
                # "B2": 0, # Buy tier 2 development card
                # "B3": 0, # Buy tier 3 development card
                # "T2": 0, # Pick up two tokens
                # "T3": 0, # Pick up three tokens
                # "RB": 0, # Reserve beneficially
                # "RA": 0, # Reserve offensively
                # "E": 0 # Error occurred
        
            self.risk_data = {}
            for player in gamestate.players:
                self.risk_data[player.id] = {
                    "R1": 0, # Beneficial reservation
                    "R2": 0, # Attacking reservation
                    "R3": 0, # Reserve facedown card
                    "R4": 0, # Hold off from buying card
                    "R5": 0 # Pick up two tokens
                }

        def __str__(self):
            return "Game over! Player {} wins in {} rounds. {} AI errors detected. {}".format(
                self.winning_player,
                self.rounds,
                self.errors,
                self.turn_data
            )
