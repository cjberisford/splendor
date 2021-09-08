
"""
COM3610 - Dissertation Project
aca18cjb, (c) Chris Berisford 2021

player.py - Contains all information relating to a player
"""

import settings, random, math
import numpy as np

# Disables calls to UI for testing
TESTING_MODE = settings.TESTING_MODE


class Player:
    def __init__(self, name, id, tokens, cards, reservations, nobles):
        self.id = id
        self.name = name
        self.tokens = tokens
        self.cards = cards
        self.reservations = reservations
        self.nobles = nobles
        self.holding_tokens = [0, 0, 0, 0, 0, 0]
        self.w_noble = {}
        self.w_card = {}
        self.w_card_r = {}
        self.w_card_fd = {}
        self.w_token = {}
        self.probabilities = {}
        self.ai_type = 1
        self.desired_types = []

    def __str__(self):
        return "PLAYER #{} || Tokens: {}, Development Cards: {}, Reservations: {}, Nobles: {} Current Score: {}".format(
            self.id,
            self.tokens,
            self.cards,
            self.reservations,
            self.nobles,
            self.score()
        )

    def score(self):
        """Returns player's current score"""
        nobles_score = len(self.nobles) * 3
        card_score = 0
        for card in self.cards:
            card_score += card.pointValue
        return nobles_score + card_score

    def count_wealth(self):
        """Calculates resource value of development cards"""
        count = [0, 0, 0, 0, 0, 0]

        for card in self.cards:
            if card.gemType == settings.RESOURCE_COLOURS[0]:
                count[0] += 1
            if card.gemType == settings.RESOURCE_COLOURS[1]:
                count[1] += 1
            if card.gemType == settings.RESOURCE_COLOURS[2]:
                count[2] += 1
            if card.gemType == settings.RESOURCE_COLOURS[3]:
                count[3] += 1
            if card.gemType == settings.RESOURCE_COLOURS[4]:
                count[4] += 1
        return count

    def get_euclidian_distance(self, vector_x, vector_y):
        """Calculate how far player is from obtaining noble"""
        x = np.array(vector_x)
        y = np.array(vector_y)
        error = np.linalg.norm(x-y)
        return error

    def affordability_check(self, card):
        """Checks if AI has sufficient combination of resources to purchase a card"""

        # Apply development card discount with np array
        purchaseCost = np.array(card.purchaseCost + [0])
        playerResources = np.array(self.count_wealth())
        effective_wealth = np.array(self.tokens)

        effective_cost = purchaseCost - playerResources
        # This cannot go below zero
        effective_cost = [i if i > 0 else 0 for i in effective_cost]

        net_cost = effective_wealth - effective_cost
        costOverflow = sum(gemCost for gemCost in net_cost if gemCost < 0)
        if np.min(net_cost) < 0:
            if abs(costOverflow) > 0 and abs(costOverflow) <= self.tokens[5]:
                # Special case where AI can use gold tokens to buy card
                return True
            else:
                return False
        else:
            return True

    def get_all_affordable_cards(self):
        """Return lists of affordable cards together with their weights"""

        affordable_cards = {}
        for card, value in self.w_card.items():
            if self.affordability_check(card):
                affordable_cards[card] = value

        affordable_reservations = {}
        for card, value in self.w_card_r.items():
            if self.affordability_check(card):
                affordable_reservations[card] = value

        return affordable_cards, affordable_reservations

    def get_desired_types(self):
        """Ascertain priority development card colours"""
        if len(self.w_noble) > 0:
            target_noble = max(self.w_noble, key=self.w_noble.get)
            for i in range(len(target_noble.prerequisites)):
                if target_noble.prerequisites[i] > 0:
                    self.desired_types.append(settings.RESOURCE_COLOURS[i])
        else:
            self.desired_types = settings.RESOURCE_COLOURS

    def get_probabilities(self, dealt):
        """Calculate probability of next card being a given colour"""

        probabilities = {}
        for gem in settings.RESOURCE_COLOURS[:-1]:
            probabilities[gem] = 18

        # Behaviour modification #1 - Memory limitation
        if self.ai_type == 1:
            # Incoporate some variance to this figure
            how_tired_am_i = 5 + random.randint(0, 4)
            dealt = dealt[:how_tired_am_i]

        for card in dealt:
            probabilities[card.gemType] -= 1

        factor = 1.0/sum(probabilities.values())
        for k in probabilities:
            probabilities[k] = (probabilities[k]*factor) * 100

        self.probabilities = probabilities

    def get_faceup_cards(self, gamestate):
        """Return all development cards in play"""
        faceup_cards = [card for tier in gamestate.development_cards[1]
                        for card in tier if tier.index(card) != 0]
        return faceup_cards

    def get_facedown_cards(self, gamestate):
        """Return all development cards in play"""
        facedown_cards = [card for tier in gamestate.development_cards[1]
                          for card in tier if tier.index(card) == 0]
        return facedown_cards

    def get_w_noble(self, gamestate):
        """Compute distance to each noble and return weight vector"""

        # Behaviour modification #2 - Strategy reshuffle
        shuffle_weights = False
        if self.ai_type == 1 and random.randint(0, 100) <= 1:
            shuffle_weights = True

        w_noble = {}
        for noble in gamestate.noble_cards[1]:
            pr = noble.prerequisites + [0]
            r = self.count_wealth()
            if len(self.cards) == 0 or shuffle_weights:
                # Artificially skew weighting before first card bought
                w_noble[noble] = np.random.gamma(
                    1, settings.NOBLE_WEIGHT_FACTOR)
            else:
                # Calculate w_noble
                distance = self.get_euclidian_distance(pr, r)
                w_noble[noble] = 1/(1+distance)
        return w_noble

    def get_w_card(self, gamestate, cards):
        """Calculate development card weight vector"""

        w_card = {}
        for i in range(len(cards)):
            # Calculate w_card
            card = cards[i]
            cp = card.pointValue * 0.2  # Scale point value between 0 and 1
            c = np.array(card.purchaseCost + [0])
            r = np.array(self.count_wealth()) + np.array(self.tokens)
            cg = card.gemType
            pc = list(self.probabilities.values())[
                settings.RESOURCE_COLOURS.index(cg)]
            wcg = 0
            for noble in gamestate.noble_cards[1]:
                if noble.prerequisites[settings.RESOURCE_COLOURS.index(cg)] > 0:
                    wcg += self.w_noble[noble]

            d = self.get_euclidian_distance(c, r)
            w_card[card] = cp+wcg/1+(d*pc)

        # Return sorted for convenience
        w_card = dict(
            sorted(w_card.items(), key=lambda item: item[1], reverse=True))

        return w_card

    def get_w_token(self, gamestate):
        """Calculate token weight vector"""

        w_token = {}
        count = 0

        # Count weights of in play development cards
        for tier in gamestate.development_cards[1]:
            for card in tier[1:5]:
                c = np.array(card.purchaseCost)/card.level
                w_c = self.w_card[card]
                count += c*w_c

        # Count weights of reserved development cards
        for card in self.reservations:
            c = np.array(card.purchaseCost)/card.level
            w_c = self.w_card_r[card]
            count += c*w_c

        for gem in settings.RESOURCE_TYPES[:5]:
            w_token[gem] = count[settings.RESOURCE_TYPES.index(gem)]

        return w_token

    # def calculate_similarity(self, gamestate):
    #     """Score similarity with AI player"""

    #     self.w_noble = self.get_w_noble(gamestate)

    #     # Get weights for affordable development cards
    #     faceup_cards = self.get_faceup_cards(gamestate)
    #     facedown_cards = self.get_facedown_cards(gamestate)
    #     self.w_card = self.get_w_card(gamestate, faceup_cards)
    #     affordable_cards = {}
    #     for card, value in self.w_card.items():
    #         if self.affordability_check(card):
    #             affordable_cards[card] = value

    #     # Calculate token weights
    #     self.w_token = self.get_w_token(gamestate)

    #     # Get weights for affordable reservations
    #     reserved_cards = self.reservations
    #     self.w_card_r = self.get_w_card(gamestate, reserved_cards)
    #     affordable_reservations = {}
    #     for card, value in self.w_card_r.items():
    #         if self.affordability_check(card):
    #             affordable_reservations[card] = value

    #     # print(self.w_token)

    def get_weights(self, gamestate):
        # Step 1 - Get noble weights
        self.w_noble = self.get_w_noble(gamestate)

        # Step 2 - Get weights for affordable development cards
        faceup_cards = self.get_faceup_cards(gamestate)
        facedown_cards = self.get_facedown_cards(gamestate)
        self.w_card = self.get_w_card(gamestate, faceup_cards)
        self.w_card_fd = self.get_w_card(gamestate, facedown_cards)
        self.w_card_r = self.get_w_card(gamestate, self.reservations)

        # Step 3 - Calculate token weights
        self.w_token = self.get_w_token(gamestate)


class AI(Player):
    def __init__(self, id, name, tokens, cards, reservations, nobles, ai_type):
        super().__init__(id, name, tokens, cards, reservations, nobles)
        self.ai_type = ai_type
        # self.targetNoble = None

    def __str__(self):
        return "AI #{} || Tokens: {}, Development Cards: {}, Reservations: {}, Nobles: {} Current Score: {}".format(
            self.id,
            self.tokens,
            self.cards,
            self.reservations,
            self.nobles,
            self.targetNoble,
            self.score()
        )

    def calculate_token_selection(self, gamestate, weights):
        """Calculate combination of tokens to pick up based on weights"""

        stack = [0, 0, 0, 0, 0, 0]
        current_player_id = gamestate.turn % len(gamestate.players)
        round_number = math.floor(gamestate.turn / len(gamestate.players)) + 1

        # Sort weights by token type
        sorted_token_weights = dict(
            sorted(weights.items(), key=lambda item: item[1], reverse=True))

        # Which tokens are available?
        available_tokens = gamestate.token_pool[:6]

        # Remove gemtypes which are not available
        null_gem_indices = []
        for i in range(5):
            if available_tokens[i] == 0:
                null_gem_indices.append(i)
        for null_gem_index in null_gem_indices:
            gem_type_from_index = settings.RESOURCE_TYPES[null_gem_index]
            del sorted_token_weights[gem_type_from_index]

        # Determine if favoured gem type exists
        favoured_gem_type = None
        favoured_gem_type_index = 0
        favoured_gem_multiplier = 1.25
        if self.ai_type == 0:
            favoured_gem_multiplier += 0.5

        favoured_token_threshold = np.mean(list(sorted_token_weights.values(
        ))) + (favoured_gem_multiplier * np.std(list(sorted_token_weights.values())))

        # Check if there are sufficient tokens remaining to make this comparison
        if len(sorted_token_weights) >= 2:
            if list(sorted_token_weights.items())[0][1] >= favoured_token_threshold:
                favoured_gem_type = list(sorted_token_weights.items())[0]
                favoured_gem_type_index = settings.RESOURCE_TYPES.index(
                    favoured_gem_type[0])

        if favoured_gem_type is not None and available_tokens[favoured_gem_type_index] >= 4:
            # Pick up two of a colour
            gamestate.game_summary.risk_data[current_player_id]["R5"] += 1
            gem_type_to_pick_up = list(sorted_token_weights.items())[0]
            gem_to_pick_up = settings.RESOURCE_TYPES.index(
                gem_type_to_pick_up[0])
            if sum(self.tokens) <= 8:
                if isinstance(self, AI):
                    gamestate.game_summary.turn_data[self.id][round_number] = "T2"
                stack[gem_to_pick_up] += 2
            else:
                stack[gem_to_pick_up] += 1
        elif len(sorted_token_weights) >= 2 and sum(self.tokens) <= 7:
            # Pick up three best weighted gems
            gems_to_pick_up = list(sorted_token_weights.items())[:3]
            for gem in gems_to_pick_up:
                gem_to_pick_up = settings.RESOURCE_TYPES.index(gem[0])
                if isinstance(self, AI):
                    gamestate.game_summary.turn_data[self.id][round_number] = "T3"
                stack[gem_to_pick_up] += 1
        else:
            # Pick up best weighted gem until no longer can
            picked_up = 0
            for gem in sorted_token_weights.keys():
                gem_to_pick_up = settings.RESOURCE_TYPES.index(gem)
                if (sum(self.tokens) + picked_up) < 10:
                    picked_up += 1
                    stack[gem_to_pick_up] += 1

        return stack

    def acquire_tokens(self, gamestate, weights, current_player_id, UI):
        """Perform AI action of acquiring tokens"""

        # Determine combination of tokens to pick up
        stack = self.calculate_token_selection(gamestate, weights)

        # Remove picked up tokens from token pool
        subtracted_pool = []
        to_subtract = zip(gamestate.token_pool, stack)
        for x, y in to_subtract:
            subtracted_pool.append(x - y)
        gamestate.token_pool = subtracted_pool

        # Add selected tokens to player resources
        gamestate.allocate_tokens(current_player_id, stack)

        # Print turn details to message box
        string = ""
        for i in range(5):
            if stack[i] > 0:
                string = string + " " + \
                    str(stack[i]) + "x " + \
                    settings.RESOURCE_TYPES[i] + " token"
        string = string + "."
        if not TESTING_MODE:
            UI.display_message(
                "> Player " + str(current_player_id + 1) + " (AI) picked up:" + string)

    def acquire_card(self, gamestate, cards, current_player_id, UI, calledFrom):
        """Perform AI action of buying development card"""

        round_number = math.floor(gamestate.turn / len(gamestate.players)) + 1

        # Sort the list and buy the one with the highest weight
        sorted_cards = dict(
            sorted(cards.items(), key=lambda item: item[1], reverse=True))
        cardToAcquire = list(sorted_cards.items())[0][0]

        # Add card to player hand
        gamestate.players[current_player_id].cards.append(cardToAcquire)

        # Find index of card to acquire
        level = cardToAcquire.level
        index = self.find_index(gamestate, cardToAcquire, level, calledFrom)

        # Register purchase of game in game session log
        gamestate.game_summary.turn_data[current_player_id][round_number] = "B" + str(
            cardToAcquire.level)

        if calledFrom == "board":
            # Remove it from gamestate and draw another
            del(gamestate.development_cards[1][level-1][index])
            flop = gamestate.development_cards[1][level-1]
            drawfrom = gamestate.development_cards[0][level-1]
            gamestate.development_cards[0][level-1], gamestate.development_cards[1][level -
                                                                                    1] = gamestate.deal_cards(flop, drawfrom, 1, index)
        else:
            # Remove it from reservations
            del(self.reservations[index])

        purchase_cost = np.array(cardToAcquire.purchaseCost + [0])
        player_resources = np.array(self.count_wealth())
        player_wealth = np.array(self.tokens)
        effective_cost = purchase_cost - player_resources
        token_pool = np.array(gamestate.token_pool)
        # This cannot go below zero
        effective_cost = [i if i > 0 else 0 for i in effective_cost]
        net_cost = player_wealth - effective_cost
        costOverflow = sum(gemCost for gemCost in net_cost if gemCost < 0)

        if abs(costOverflow) > 0:
            # Buy card with gold tokens

            # Subtract gold tokens first
            net_cost_mask = np.array([i if i < 0 else 0 for i in net_cost])
            price_paid = effective_cost + net_cost_mask

            gamestate.token_pool = list(price_paid + token_pool)
            # Add gold tokens back to game
            gamestate.token_pool[5] += abs(costOverflow)

            # This cannot go below zero; add back gold tokens
            net_cost = [i if i > 0 else 0 for i in net_cost]

            self.tokens = list(net_cost)
            self.tokens[5] -= abs(costOverflow)
            if not TESTING_MODE:
                if calledFrom == "board":
                    UI.display_message(
                        "> Player " + str(current_player_id + 1) + " (AI) acquired a card using gold tokens.")
                else:
                    UI.display_message("> Player " + str(current_player_id + 1) +
                                       " (AI) acquired a card from their reservations using gold tokens.")
        else:
            gamestate.token_pool = list(effective_cost + token_pool)
            self.tokens = list(player_wealth - effective_cost)

            if not TESTING_MODE:
                if calledFrom == "board":
                    UI.display_message(
                        "> Player " + str(current_player_id + 1) + " (AI) acquired a card.")
                else:
                    UI.display_message("> Player " + str(current_player_id + 1) +
                                       " (AI) acquired a card from their reservations.")

    def reserve_card(self, gamestate, cards, current_player_id, UI):
        """Perform AI action of reserving development card and acquiring gold token"""

        # Sort the list and reserve the one with the highest weight
        sorted_cards = dict(
            sorted(cards.items(), key=lambda item: item[1], reverse=True))
        cardToAcquire = list(sorted_cards.items())[0][0]

        # Add card to player reservations
        gamestate.players[current_player_id].reservations.append(cardToAcquire)

        # LOGIC FOR ATTACKING RESERVATION GOES HERE!

        # Find index of card to reserve
        level = cardToAcquire.level
        index = self.find_index(gamestate, cardToAcquire, level, "board")

        # Remove it from gamestate and draw another
        del(gamestate.development_cards[1][level-1][index])
        flop = gamestate.development_cards[1][level-1]
        drawfrom = gamestate.development_cards[0][level-1]
        gamestate.development_cards[0][level-1], gamestate.development_cards[1][level -
                                                                                1] = gamestate.deal_cards(flop, drawfrom, 1, index)

        # Acquire gold token
        gold_token_pool = gamestate.token_pool[5]
        available_capacity = 10 - sum(self.tokens)

        # Gold token logic + display message
        if gold_token_pool > 0:
            if available_capacity > 0:
                if not TESTING_MODE:
                    UI.display_message("> Player " + str(current_player_id + 1) +
                                       " (AI) reserved a card and acquired a gold token.")
                gamestate.allocate_tokens(
                    current_player_id, [0, 0, 0, 0, 0, 1])
                gamestate.token_pool[5] -= 1
            else:
                if not TESTING_MODE:
                    UI.display_message("> Player " + str(current_player_id + 1) +
                                       " (AI) reserved a card but did not acquire a gold token as they have reached their token limit.")
        else:
            if not TESTING_MODE:
                UI.display_message("> Player " + str(current_player_id + 1) +
                                   " (AI) reserved a card but did not acquire a gold token as there are none left.")

    def find_index(self, gamestate, card, level, calledFrom):
        """Return the position of a card as it is displayed"""
        index = 0

        if calledFrom == "board":
            # Check for equivalency to find position of card in flop
            for i in range(len(gamestate.development_cards[1][level-1])):
                comparison_card = gamestate.development_cards[1][level-1][i]
                if card.purchaseCost == comparison_card.purchaseCost and card.gemType == comparison_card.gemType and card.pointValue == comparison_card.pointValue:
                    index = i
        else:
            # Check for equivalency in reservations to get position
            for i in range(len(self.reservations)):
                comparison_card = self.reservations[i]
                if card.purchaseCost == comparison_card.purchaseCost and card.gemType == comparison_card.gemType and card.pointValue == comparison_card.pointValue:
                    index = i
        return index

    def noble_requirements_met(self, gamestate, UI):
        """Allows AI to select and acquire noble"""
        potential_matches = []

        # Get list of nobles where prerequisites are met
        for noble in gamestate.noble_cards[1]:
            prereqs = np.array(noble.prerequisites + [0])
            resources = np.array(self.count_wealth())
            if np.min(resources - prereqs) >= 0:
                potential_matches.append(noble)

        # Can influence AI decision on which noble to pick up, but is this important?

        # Take first of the list an add it to hand
        if len(potential_matches) > 0:
            card_to_append = potential_matches[0]
            gamestate.noble_cards[1].remove(card_to_append)
            self.nobles.append(card_to_append)
            if not TESTING_MODE:
                UI.display_message(
                    "> Player " + str(settings.NUMBER_OF_PLAYERS + (self.id + 1)) + " (AI) has acquired a noble.")
            self.skipNobleCheck = True

        gamestate.increment_turn(UI)

    def determine_best_cards(self, affordable_cards, affordable_reservations):
        """Take best values from each list"""
        if len(affordable_reservations) > 0:
            best_reservation = max(affordable_reservations.values())
        else:
            best_reservation = 0

        if len(affordable_cards) > 0:
            best_card = max(affordable_cards.values())
        else:
            best_card = 0
        return best_reservation, best_card

    def get_aggressive_reservation_list(self, gamestate):
        """Gets high value cards from perspective of each player"""
        aggressive_reservation_list = {}

        for player in gamestate.players:
            if player != self:
                # Create dictionary of all affordable cards for another player
                card_values = {}
                opponents_affordable_cards, _ = player.get_all_affordable_cards()
                for card in opponents_affordable_cards:
                    card_values[card] = player.w_card[card]

                # Get values of cards to player
                v = list(player.w_card.values())
                value_threshold = max([np.mean(v) + (1.5 * np.std(v)), 0])

                # Take the most valuable card and add it to list
                if len(opponents_affordable_cards) > 0:
                    most_desired_card = max(opponents_affordable_cards, key=opponents_affordable_cards.get)

                    if card_values[most_desired_card] > value_threshold:
                        aggressive_reservation_list[player.id] = most_desired_card

        return aggressive_reservation_list

    def standard_ai(self, gamestate, UI, affordable_cards, affordable_reservations):
        """Decision tree for standard AI"""
        current_player_id = gamestate.turn % len(gamestate.players)
        round_number = math.floor(gamestate.turn / len(gamestate.players)) + 1

        # Step 1 - Help me decide whether I want to buy a reservation or not
        best_reservation, best_card = self.determine_best_cards(
            affordable_cards, affordable_reservations)

        # Step 2 - AI decision tree
        if best_reservation >= best_card and len(affordable_reservations) > 0:
            # Action - Buy reservation
            self.acquire_card(gamestate, affordable_reservations,
                              current_player_id, UI, "hand")
        elif len(affordable_cards) > 0:
            # Action - Buy development card
            self.acquire_card(gamestate, affordable_cards,
                              current_player_id, UI, "board")
        else:
            if sum(self.tokens) < 10:
                # Action - Pick up tokens
                if max(gamestate.token_pool[:5]) > 0:
                    self.acquire_tokens(
                        gamestate, self.w_token, current_player_id, UI)
                else:
                    # Error - No tokens available to pick up
                    gamestate.game_summary.errors += 1
            else:
                if len(self.reservations) <= 2:
                    # Action - Reserve a card
                    gamestate.game_summary.risk_data[current_player_id]["R1"] += 1
                    gamestate.game_summary.turn_data[current_player_id][round_number] = "RB"
                    self.reserve_card(gamestate, self.w_card,
                                      current_player_id, UI)
                else:
                    # Error - No viable moves
                    gamestate.game_summary.turn_data[current_player_id][round_number] = "E"
                    gamestate.game_summary.errors += 1

    def modified_ai(self, gamestate, UI, affordable_cards, affordable_reservations):
        """Decision tree for modified AI"""

        current_player_id = gamestate.turn % len(gamestate.players)
        round_number = math.floor(gamestate.turn / len(gamestate.players)) + 1

        highest_value_card = list(self.w_card.values())[0]

        # Is there a card another player really wants? - This gets the most valuable card for each player
        aggressive_reservation_list = self.get_aggressive_reservation_list(gamestate)
        
        for player, card in aggressive_reservation_list.items():
            # Assign artificially large values for cards on list
            self.w_card[card] = max(self.w_card.values()) + 1  

        desired_card_in_bottom_row = False
        for card in gamestate.development_cards[1][0]:
            if card.gemType in self.desired_types:
                desired_card_in_bottom_row = True

        v = list(self.w_card.values())
        upper_value_threshold = max([np.mean(v) + (2 * np.std(v)), 0])
        lower_value_threshold = max([np.mean(v) - (1.75 * np.std(v)), 0])

        if len(affordable_cards) + len(affordable_reservations) > 0:
            if max(list(affordable_reservations.values()) + list(affordable_cards.values()) + [0]) < lower_value_threshold:
                # AI will take a risk in this condition, so record it
                # print("Pass up opportunity")
                gamestate.game_summary.risk_data[current_player_id]["R4"] += 1

        if len(aggressive_reservation_list) == 1 and len(self.reservations) <= 2:
            # Aggressive reservation
            self.reserve_card(gamestate, self.w_card,
                                  current_player_id, UI)
            gamestate.game_summary.risk_data[current_player_id]["R2"] += 1
            gamestate.game_summary.turn_data[current_player_id][round_number] = "RA"

        elif highest_value_card >= upper_value_threshold and self.ai_type == 1 and len(self.reservations) <= 2:
            # Behaviour modification #3 - Reserve/buy valuable cards
            gamestate.game_summary.risk_data[current_player_id]["R1"] += 1
            
            if highest_value_card in affordable_cards:
                self.acquire_card(gamestate, affordable_cards,
                                  current_player_id, UI, "board")
            else:
                gamestate.game_summary.turn_data[current_player_id][round_number] = "RB"
                self.reserve_card(gamestate, self.w_card,
                                  current_player_id, UI)

        elif max(list(affordable_reservations.values()) + list(affordable_cards.values()) + [0]) > lower_value_threshold:
            # Behaviour modification #4 - Only buy cards above a certain threshold

            best_reservation, best_card = self.determine_best_cards(
                affordable_cards, affordable_reservations)
            if best_reservation >= best_card:
                self.acquire_card(gamestate, affordable_reservations,
                                  current_player_id, UI, "hand")
            else:
                self.acquire_card(gamestate, affordable_cards,
                                  current_player_id, UI, "board")
        elif not desired_card_in_bottom_row and len(self.reservations) <= 2:
            # Behaviour modification #6 - Reserve facedown development card
            gamestate.game_summary.risk_data[current_player_id]["R3"] += 1

            self.reserve_card(gamestate, self.w_card_fd, current_player_id, UI)
        elif sum(self.tokens) < 10:
            # Action - Pick up tokens
            if max(gamestate.token_pool[:5]) > 0:
                self.acquire_tokens(
                    gamestate, self.w_token, current_player_id, UI)
            else:
                # Error - No tokens available to pick up
                gamestate.game_summary.errors += 1
        elif len(self.reservations) <= 2:
            # Action - Reserve a card
            gamestate.game_summary.turn_data[current_player_id][round_number] = "RB"
            self.reserve_card(gamestate, self.w_card,
                              current_player_id, UI)
        else:
            # Error - No viable moves
            gamestate.game_summary.turn_data[current_player_id][round_number] = "E"
            gamestate.game_summary.errors += 1

    def evaluation(self, gamestate, UI):
        """Main loop for AI control"""


        # Get gamestate information and weights
        # self.get_probabilities(gamestate.dealt)
        # self.get_weights(gamestate)

        # Calculate weights for all players
        for player in gamestate.players:
            player.get_probabilities(gamestate.dealt)
            player.get_weights(gamestate)
            player.get_desired_types()

        affordable_cards, affordable_reservations = self.get_all_affordable_cards()

        # Call different decision tree based on AI setting
        if gamestate.ai_type == 0:
            self.standard_ai(gamestate, UI, affordable_cards, affordable_reservations)
        else:
            self.modified_ai(gamestate, UI, affordable_cards, affordable_reservations)

        # Set to true to watch AI take turns live. It's great fun...!
        if False:
            UI.root.update()

        self.noble_requirements_met(gamestate, UI)
