"""
COM3610 - Dissertation Project
aca18cjb, (c) Chris Berisford 2021

UI.py - Configures and updates the UI
"""

import tkinter as tk
import math, sys, settings, splendor

class UI:
    def __init__(self, root, gamestate):
        self.root = root
        root.title("Splendor")
        root.state('zoomed')

        # keep game minimised if it contains no human players
        if settings.NUMBER_OF_PLAYERS == 0:
            root.withdraw()

        self.gamestate = gamestate

        # create and configure menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Restart", command=lambda: self.restart())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=lambda: self.kill())
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="About")
        self.root.config(menu=menubar)

        # set weights of root columns
        self.root.grid_rowconfigure(0, weight=1, uniform='row')
        self.root.grid_columnconfigure((0, 2), weight=1, uniform='row')
        self.root.grid_columnconfigure(1, weight=4, uniform='row')

        # create left, centre and right frames
        self.left = tk.Frame(self.root, bg='yellow')
        self.centre = tk.Frame(self.root, bg='white')
        self.right = tk.Frame(self.root, bg='yellow')
        self.left.grid(column=0, row=0, sticky="nsew")
        self.centre.grid(column=1, row=0, sticky="nsew")
        self.right.grid(column=2, row=0, sticky="nsew")
        self.status_bar = tk.Frame(
            self.root, bg="white", borderwidth=1, relief=tk.RIDGE)
        self.status_bar.grid(column=0, row=2, columnspan=3, sticky="nsew")

        # set weights of child columns
        self.left.grid_rowconfigure((0, 1), weight=1)
        self.left.grid_columnconfigure(0, weight=1)
        self.centre.grid_rowconfigure(0, weight=1)
        self.centre.grid_columnconfigure(0, weight=1)
        self.right.grid_rowconfigure((0, 1), weight=1)
        self.right.grid_columnconfigure(0, weight=1)
        self.status_bar.grid_rowconfigure(0, weight=1)
        self.status_bar.grid_columnconfigure(0, weight=1)

        # create player frames
        self.left_upper = tk.Frame(
            self.left, bg='#F0F0F0', padx=2, pady=2, borderwidth=settings.UI_BORDERWIDTH)
        self.left_lower = tk.Frame(
            self.left, bg='#F0F0F0', padx=2, pady=2, borderwidth=settings.UI_BORDERWIDTH)
        self.left_upper.grid(column=0, row=0, sticky="nsew")
        self.left_lower.grid(column=0, row=1, sticky="nsew")

        self.right_upper = tk.Frame(
            self.right, bg='#F0F0F0', padx=2, pady=2, borderwidth=settings.UI_BORDERWIDTH)
        self.right_lower = tk.Frame(
            self.right, bg='#F0F0F0', padx=2, pady=2, borderwidth=settings.UI_BORDERWIDTH)
        self.right_upper.grid(column=0, row=0, sticky="nsew")
        self.right_lower.grid(column=0, row=1, sticky="nsew")

        # set weights of child columns
        self.left_upper.grid_rowconfigure(0, weight=1)
        self.left_upper.grid_columnconfigure((0), weight=1)
        self.left_lower.grid_rowconfigure(0, weight=1)
        self.left_lower.grid_columnconfigure((0), weight=1)
        self.right_upper.grid_rowconfigure(0, weight=1)
        self.right_upper.grid_columnconfigure((0), weight=1)
        self.right_lower.grid_rowconfigure(0, weight=1)
        self.right_lower.grid_columnconfigure((0), weight=1)

        # development card layout configuration
        self.centre.grid_rowconfigure((0, 2), weight=0)
        self.centre.grid_rowconfigure(1, weight=1)
        self.centre.grid_columnconfigure(0, weight=1)

        self.centre_upper = tk.Frame(self.centre, bg="#F0F0F0")
        self.centre_middle = tk.Frame(self.centre, bg="#F0F0F0")
        self.centre_lower = tk.Frame(self.centre, bg="#F0F0F0", padx=2, pady=2)
        self.centre_upper.grid(column=0, row=0, sticky="nsew")
        self.centre_middle.grid(column=0, row=1, sticky="nsew")
        self.centre_lower.grid(column=0, row=2, sticky="nsew")

        self.centre_upper.grid_rowconfigure(0, weight=1)
        self.centre_upper.grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1, uniform="col8")
        self.centre_middle.grid_rowconfigure(0, weight=1)
        self.centre_middle.grid_columnconfigure(0, weight=1)
        self.centre_lower.grid_rowconfigure(0, weight=1)
        self.centre_lower.grid_columnconfigure(0, weight=1)

        # initialise and display info box
        self.display_info_box = tk.Text(
            self.centre_lower, height=8, state="disabled", padx=5, pady=5)
        self.display_info_box.grid(row=0, column=0, sticky='nsew')

        self.display_message("Welcome to Splendor! Take your turn to begin.")

        self.scrollbar = tk.Scrollbar(
            self.centre_lower, command=self.display_info_box.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')

        self.links_enabled = True
        self.nobles_enabled = False
        self.root = root

        self.clear_gui()
        self.update_gui()

        # Don't ask me why this is here - I don't know.
        self.gamestate.start_game(self)

    def restart(self):
        self.root.destroy()
        splendor.start()
        del self

    def kill(self):
        sys.exit()

    def display_message(self, string):
        self.display_info_box.config(state="normal")
        self.display_info_box.insert(tk.END, string + '\n')
        self.display_info_box.config(state="disabled")
        self.display_info_box.see("end")

    def pop_token(self, gemType):
        """Removes token from temporary pool when using gold tokens"""
        gem_index = settings.RESOURCE_COLOURS.index(gemType)

        if self.gamestate.token_pool[gem_index] > 0:
            self.gamestate.temp_pool[gem_index] += 1
            self.gamestate.token_pool[gem_index] -= 1
            self.redraw_top()
        else:
            self.display_message(
                "[Error] There are no " + gemType + " tokens to pick up.")

    def push_token(self, gemType):
        """Adds token to temporary pool when using gold tokens"""
        gem_index = settings.RESOURCE_COLOURS.index(gemType)

        if self.gamestate.temp_pool[gem_index] == 0:
            self.display_message(
                "[Error] You are not holding a " + gemType + " token.")
        else:
            self.gamestate.temp_pool[gem_index] -= 1
            self.gamestate.token_pool[gem_index] += 1
            self.redraw_top()

    def validate_token_selection(self, gamestate):
        """Event handler for button - checks if token selection is valid"""

        current_player = gamestate.turn % len(gamestate.players)
        stack = gamestate.temp_pool

        available_capacity = 10 - sum(gamestate.players[current_player].tokens)

        stack_width = sum(x for x in stack)
        stack_height = max(stack)

        success = False

        if available_capacity >= 3:
            if stack_width > 3 or stack_height > 2 or (stack_height > 1 and stack_width > 2):
                self.display_message(
                    "[Error] You can pick up to a maximum of three tokens and not more than two of one type per turn.")
            else:
                success = True
        elif available_capacity == 2:
            if (stack_width > 2) or (stack_height > 1 and stack_width > 2):
                self.display_message(
                    "[Error] You must not exceed the token limit of 10.")
            else:
                success = True
        elif available_capacity == 1:
            if stack_width > 1:
                self.display_message(
                    "[Error] You must not exceed the token limit of 10.")
            else:
                success = True
        else:
            self.display_message(
                "[Error] You have reached the token limit of 10. Please select another action.")

        if stack_height == 2:
            gem_index = list.index(stack, max(stack))
            if gamestate.token_pool[gem_index] < 2:
                self.display_message(
                    "[Error] When taking two tokens, you must leave at least two of that particular gem type.")
                success = False

        if success:
            
            # Check if player could have afforded any cards
            affordable_cards, affordable_reservations = gamestate.players[current_player].get_all_affordable_cards()
            if len(affordable_cards) > 0 or len(affordable_reservations) > 0:
                # This is a risk, so should be recorded
                gamestate.game_summary.risk_data[current_player]["R4"] += 1


            round_number = math.floor(gamestate.turn / len(gamestate.players)) + 1
            if stack_height == 2:
                gamestate.game_summary.turn_data[current_player][round_number] = "T2"
                # This is a risk, so should be recorded
                gamestate.game_summary.risk_data[current_player]["R5"] += 1
 
            else:
                gamestate.game_summary.turn_data[current_player][round_number] = "T3"

            gamestate.allocate_tokens(current_player, stack)
            string = ""
            for i in range(5):
                if stack[i] > 0:
                    string = string + " " + \
                        str(stack[i]) + "x " + \
                        settings.RESOURCE_TYPES[i] + " token"
            string = string + "."
            self.display_message(
                "> Player " + str(current_player + 1) + " picked up:" + string)
            gamestate.increment_turn(self)

    def reset_token_selection(self, gamestate):
        """Removes all tokens from selection stack"""
        for i in range(len(self.gamestate.temp_pool)):
            self.gamestate.token_pool[i] += self.gamestate.temp_pool[i]
        self.gamestate.temp_pool = [0, 0, 0, 0, 0, 0]
        self.redraw_top()

    def reserve_dev_card(self, event, gamestate, level, index):
        """Event handler for selecting a development card"""
        if len(gamestate.players[gamestate.turn % len(gamestate.players)].reservations) <= 2:
            gamestate.reserve_card((gamestate.turn % len(
                gamestate.players)), gamestate.development_cards[1][level], index, self)
            gamestate.increment_turn(self)
        else:
            self.display_message(
                "[Error] Cannot complete action. You can only reserve up to three cards at once.")

    def acquire_noble(self, event, gamestate, index):
        """Event handler for selecting a noble"""
        gamestate.acquire_noble((gamestate.turn % len(
            gamestate.players)), gamestate.noble_cards[1][index], index, self)

    def buy_dev_card(self, event, gamestate, level, index, player_id, deck, calledFrom):
        """Event handler for selecting a development card"""
        gamestate.acquire_card(player_id, deck, index, calledFrom, self)

    def acquire_reservation(self, event, gamestate, level, index, player_id, deck):
        """Handles purchasing of reserved development card"""

        # Ensure player attempting to reserve owns the reservation
        if gamestate.turn % len(gamestate.players) == player_id:
            gamestate.acquire_card((gamestate.turn % len(
                gamestate.players)), deck, index, "hand", self)
        else:

            self.display_message(
                "[Error] You cannot acquire cards from another player's reservation deck.")

    def draw_dev_card(self, card, target):
        """Draws a development card"""
        dev_card = tk.Frame(target, bg=card.gemType)
        dev_card.columnconfigure(0, weight=1)
        dev_card.rowconfigure(1, weight=1)
        tk.Label(dev_card, text=card.pointValue, font=("Arial", 20),
                 fg=settings.COLOUR_SWITCHER[card.gemType], bg=card.gemType, anchor=tk.W).grid(row=0, column=0, sticky="ew")
        for i in range(len(card.purchaseCost)):
            spaces_inserted = 0
            if card.purchaseCost[i] > 0:
                resource_canvas = tk.Canvas(
                    dev_card, width=15, height=15, bd=0, highlightthickness=0, bg=card.gemType)
                resource_canvas.grid(row=2+i, column=0, sticky="ew")
                for j in range(card.purchaseCost[i]):
                    if settings.RESOURCE_COLOURS[i] == "Black" and card.gemType == "Black":
                        resource_canvas.create_oval(
                            (j*12), 2, (j*12)+10, 12, fill=settings.RESOURCE_COLOURS[i], outline="grey")
                    else:
                        if j % 2 == 0 and j > 0:
                            spaces_inserted += 0
                        resource_canvas.create_oval(
                            ((j+spaces_inserted)*12), 2, ((j+spaces_inserted)*12)+10, 12, fill=settings.RESOURCE_COLOURS[i])

        return dev_card

    def draw_noble_card(self, card, target):
        """Draws a noble card"""
        noble_card = tk.Frame(target, bg="purple")
        noble_card.grid_columnconfigure(0, weight=1)
        noble_card.grid_rowconfigure(1, weight=1)
        tk.Label(noble_card, text="3", font=("Arial", 20), fg="white",
                 bg="purple", anchor=tk.W).grid(row=0, column=0, sticky="ew")

        for i in range(len(card.prerequisites)):
            if card.prerequisites[i] > 0:
                resource_canvas = tk.Canvas(
                    noble_card, width=15, height=15, bd=0, highlightthickness=0, bg="purple")
                resource_canvas.grid(row=2+i, column=0, sticky="nsew")

                resource_canvas.create_rectangle(
                    0, 2, 10, 12, fill=settings.RESOURCE_COLOURS[i])
                resource_canvas.create_text(
                    20, 6, fill="white", text="x" + str(card.prerequisites[i]))

        return noble_card

    def draw_dev_deck(self, topCard, target):
        # """Draws a development card"""
        dev_card = tk.Frame(target, bg="grey")
        photo = tk.PhotoImage(file="images/card_back.png")
        background_label = tk.Label(dev_card, image=photo)
        background_label.image = photo
        background_label.place(
            relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")

        if self.links_enabled:
            background_label.bind("<Button-3>", lambda event, gamestate=self.gamestate,
                                  level=topCard.level-1, index=0: self.reserve_dev_card(event, gamestate, level, index))

        return dev_card

    def draw_player_summary(self, id, target):
        """Draws player information"""

        player_name = self.gamestate.players[id].name
        # CONFIGURE PLAYER FRAME
        player_display = tk.Frame(
            target, bg="white", borderwidth=settings.UI_BORDERWIDTH)
        # ROW 0
        if id == self.gamestate.turn % len(self.gamestate.players):
            tk.Label(player_display, text=player_name, font=("Arial", 11), bg="orange",
                     fg="white").grid(row=0, column=0, columnspan=3, sticky="nsew")
        else:
            tk.Label(player_display, text=player_name, font=("Arial", 11), bg="lightgrey",
                     fg="white").grid(row=0, column=0, columnspan=3, sticky="nsew")
        # ROW 1
        tk.Label(player_display, text="SCORE", bg="white").grid(
            row=1, column=0, columnspan=3, sticky="nsew")
        # ROW 2
        tk.Label(player_display, text=str(self.gamestate.players[id].score())).grid(
            row=2, column=0, columnspan=3, sticky="nsew")
        # ROW 3
        tk.Label(player_display, text="RESOURCES", bg="white").grid(
            row=3, column=0, columnspan=3, sticky="nsew")
        # ROW 4-9
        resource_frame = self.draw_player_resources(id, player_display)
        resource_frame.grid(row=4, column=0, rowspan=6,
                            columnspan=3, sticky="nsew")
        resource_frame.grid_rowconfigure(
            list(range(6)), weight=1, uniform="row5")
        resource_frame.grid_columnconfigure(
            list(range(3)), weight=1, uniform="col5")

        # ROW 10-16
        tk.Label(player_display, text="RESERVATIONS", bg="white").grid(
            row=10, column=0, columnspan=3, sticky="nsew")
        reservation_display = tk.Frame(player_display)
        reservation_display.grid(
            row=11, column=0, rowspan=6, columnspan=3, sticky="nsew")
        reservation_display.grid_rowconfigure((0), weight=1, uniform="row4")
        reservation_display.grid_columnconfigure(
            (0, 1, 2), weight=1, uniform="col4")
        for i in range(len(self.gamestate.players[id].reservations)):
            card = self.gamestate.players[id].reservations[i]
            draw_card = self.draw_dev_card(card, reservation_display)
            draw_card.grid(row=0, column=i, pady=2, padx=2, sticky="nsew")

            # Get all children of development card display
            dev_card_objects = draw_card.winfo_children() + [draw_card]
            for object in dev_card_objects:

                if self.links_enabled:
                    object.bind("<Button-1>", lambda event, gamestate=self.gamestate,
                                level=card.level,
                                index=i,
                                deck=self.gamestate.players[id].reservations,
                                player_id=id: self.acquire_reservation(event, gamestate, level, index, player_id, deck))
                    object.bind('<Control-1>', lambda event, gamestate=self.gamestate,
                                level=card.level,
                                index=i,
                                deck=self.gamestate.players[id].reservations,
                                card=card,
                                player_id=id: self.gold_token_window(event, gamestate, level, index, player_id, card, deck, "hand"))
        # ROW 17-23
        tk.Label(player_display, text="NOBLES", bg="white").grid(
            row=17, column=0, columnspan=3, sticky="nsew")
        nobles_display = tk.Frame(player_display, padx=2, pady=2)
        nobles_display.grid(row=18, column=0, rowspan=6,
                            columnspan=3, sticky="nsew")
        nobles_display.grid_rowconfigure((0), weight=1, uniform="row9")
        nobles_display.grid_columnconfigure(
            (0, 1, 2, 3, 4), weight=1, uniform="col9")
        for i in range(len(self.gamestate.players[id].nobles)):
            card = self.gamestate.players[id].nobles[i]
            draw_card = self.draw_noble_card(card, nobles_display)
            draw_card.grid(row=0, column=i, pady=2, padx=2, sticky="nsew")

        return player_display

    def draw_player_resources(self, id, target):
        resource_frame = tk.Frame(target)
        # ROW 4-9
        for i in range(6):

            gemType = settings.RESOURCE_TYPES[i]
            gemColour = settings.RESOURCE_COLOURS[i]

            tk.Label(resource_frame, text=gemType, anchor=tk.E).grid(
                row=i, column=0, sticky="nsew")
            gem_canvas = tk.Canvas(
                resource_frame, width=5, height=5, highlightthickness=0)
            gem_canvas.grid(row=i, column=1, columnspan=2, sticky="nsew")

            cards_drawn = 0
            tokens_drawn = 0

            # draw development cards
            if gemType != "Gold":
                for j in range(self.gamestate.players[id].count_wealth()[i]):
                    gem_canvas.create_rectangle(
                        (j*12)+10, 5, (j*12)+20, 15, fill=gemColour)
                    cards_drawn += 1

            # draw tokens
            for j in range(self.gamestate.players[id].tokens[i]):
                gem_canvas.create_oval(
                    ((cards_drawn+j)*12)+10, 5, ((cards_drawn+j)*12)+20, 15, fill=gemColour)
                tokens_drawn += 1

        return resource_frame

    def draw_resource_toggle(self, id, target):
        resource_frame = tk.Frame(target, padx=5, pady=5)
        # ROW 4-9
        for i in range(6):

            gemType = settings.RESOURCE_TYPES[i]
            gemColour = settings.RESOURCE_COLOURS[i]
            golds = self.gamestate.players[id].tokens[5]

            tk.Label(resource_frame, text=gemType, anchor=tk.E).grid(
                row=i, column=0, sticky="nsew")
            gem_canvas = tk.Canvas(
                resource_frame, width=5, height=5, highlightthickness=0)
            gem_canvas.grid(row=i, column=1, columnspan=2, sticky="nsew")

            cards_drawn = 0
            tokens_drawn = 0
            drawn_holding = 0

            # draw development cards
            if gemType != "Gold":
                for j in range(self.gamestate.players[id].count_wealth()[i]):
                    gem_canvas.create_rectangle(
                        (j*12)+10, 5, (j*12)+20, 15, fill=gemColour)
                    cards_drawn += 1

            # draw tokens
            draw_offset = cards_drawn
            for j in range(self.gamestate.players[id].tokens[i]):
                gem_canvas.create_oval(
                    ((draw_offset+j)*12)+10, 5, ((draw_offset+j)*12)+20, 15, fill=gemColour)
                tokens_drawn += 1

            # draw holding tokens
            draw_offset = cards_drawn + tokens_drawn
            for j in range(self.gamestate.players[id].holding_tokens[i]):
                gem_canvas.create_oval(
                    ((draw_offset+j)*12)+10, 5, ((draw_offset+j)*12)+20, 15, fill=gemColour, outline="gold", width=2)
                drawn_holding += 1
                gem_canvas.bind("<Button-3>", lambda event, gamestate=self.gamestate, gem_id=i, player_id=id,
                                target=target: self.gold_token_remove(event, gamestate, gem_id, player_id, target))

            # # draw token potential with golds
            if gemType != "Gold":
                draw_offset = cards_drawn + tokens_drawn + drawn_holding
                for j in range(golds):
                    gem_canvas.create_oval(((draw_offset+j)*12)+10, 5, ((
                        draw_offset+j)*12)+20, 15, fill="lightgrey", outline="lightgrey", dash=(3, 1))
                    gem_canvas.bind("<Button-1>", lambda event, gamestate=self.gamestate, gem_id=i, player_id=id,
                                    target=target: self.gold_token_add(event, gamestate, gem_id, player_id, target))

        return resource_frame

    def gold_token_window(self, event, gamestate, level, index, player_id, card, deck, calledFrom):
        # Ensure player attempting to reserve owns the reservation
        if gamestate.turn % len(gamestate.players) == player_id:

            # Check if player has a gold token
            if self.gamestate.players[player_id].tokens[5] > 0:

                gold_window = tk.Toplevel()
                gold_window.title("Gold tokens")
                gold_window.resizable(False, False)

                gold_grid_frame = tk.Frame(gold_window, padx=5, pady=5)
                gold_grid_frame.grid(row=0, column=0)

                gold_grid_frame.grid_columnconfigure(
                    0, weight=5, uniform="col20")
                gold_grid_frame.grid_columnconfigure(
                    1, weight=4, uniform="col20")
                gold_grid_frame.grid_rowconfigure(0, weight=1, uniform="row20")
                gold_grid_frame.grid_rowconfigure(1, weight=5, uniform="row20")
                gold_grid_frame.grid_rowconfigure(2, weight=2, uniform="row20")

                tk.Label(gold_grid_frame, text="Allocate gold tokens",
                         anchor=tk.W, padx=10).grid(row=0, column=0, sticky="ew")

                # Draw player resources on screen
                self.redraw_token_window(gold_grid_frame, player_id)

                # Draw development card to buy
                dev_card_preview = self.draw_dev_card(card, gold_grid_frame)
                dev_card_preview.grid(row=1, column=1, sticky="nsew")

                # Add button to confirm choice
                confirm_button = tk.Button(gold_grid_frame, text="Confirm", padx=5, pady=5, anchor=tk.SE, command=lambda: self.confirm_token_selection(
                    event, gamestate, level, index, player_id, gold_window, deck, calledFrom))
                confirm_button.grid(row=2, column=1, sticky="se")

                # Add button to cancel
                cancel_button = tk.Button(gold_grid_frame, text="Cancel", padx=5,
                                          pady=5, anchor=tk.SW, command=lambda: gold_window.destroy())
                cancel_button.grid(row=2, column=0, sticky="sw")

                windowWidth = gold_window.winfo_reqwidth()
                windowHeight = gold_window.winfo_reqheight()

                x = int(self.root.winfo_screenwidth()/2 - windowWidth)
                y = int(self.root.winfo_screenheight()/2 - windowHeight)
                gold_window.geometry("+{}+{}".format(x, y))

                gold_window.grab_set()

            else:
                self.display_message(
                    "[Error] You do not have any gold tokens.")

        else:
            self.display_message(
                "[Error] You cannot acquire cards from another player's reservation deck.")

    # def cancelGoldWindow(played_id):
    #   self.gamestate.players[player_id].holding_tokens = [0, 0, 0, 0, 0 ,0]

    def confirm_token_selection(self, event, gamestate, level, index, player_id, target, deck, calledFrom):
        target.destroy()
        self.buy_dev_card(event, gamestate, level, index,
                          player_id, deck, calledFrom)

    def gold_token_add(self, event, gamestate, gem_id, player_id, gold_window):
        self.gamestate.players[player_id].holding_tokens[gem_id] += 1
        self.gamestate.players[player_id].tokens[5] -= 1
        self.redraw_token_window(gold_window, player_id)

    def gold_token_remove(self, event, gamestate, gem_id, player_id, gold_window):
        self.gamestate.players[player_id].holding_tokens[gem_id] -= 1
        self.gamestate.players[player_id].tokens[5] += 1
        self.redraw_token_window(gold_window, player_id)

    def clear_gui(self):
        """Clears UI information"""
        for widget in self.centre_middle.winfo_children():
            widget.destroy()
        for widget in self.left_upper.winfo_children():
            widget.destroy()
        for widget in self.left_lower.winfo_children():
            widget.destroy()
        for widget in self.right_upper.winfo_children():
            widget.destroy()
        for widget in self.right_lower.winfo_children():
            widget.destroy()
        for widget in self.centre_upper.winfo_children():
            widget.destroy()

    def update_gui(self):
        """Redraws UI information"""
        self.clear_gui()

        current_player = self.gamestate.turn % len(self.gamestate.players)
        current_turn = current_player + 1

        # display most recent update
        self.display_info_box.see("end")

        # update status bar display
        round_count = math.floor(
            self.gamestate.turn / len(self.gamestate.players)) + 1

        # draw status
        tk.Label(self.status_bar, bg="white", padx=5, text="Round " + str(round_count) +
                 ", Turn " + str(current_turn)).grid(sticky="e", row=0, column=0)

        self.redraw_top()
        self.redraw_centre()

        # draw players
        for i in range(settings.NUMBER_OF_PLAYERS + settings.NUMBER_OF_AI_PLAYERS):
            self.redraw_player(i)

    def redraw_token_window(self, gold_window, player_id):
        resource_frame = self.draw_resource_toggle(player_id, gold_window)
        # resource_canvas = tk.Canvas(gold_window, width=200, height=100)
        # resource_canvas.grid(row=0, column=0)
        resource_frame.grid(row=1, column=0)
        resource_frame.grid_rowconfigure(
            (0, 1, 2, 3, 4, 5), weight=1, uniform="row15")
        resource_frame.grid_columnconfigure(
            (0, 1, 2), weight=1, uniform="col15")

    def redraw_top(self):

        for widget in self.centre_upper.winfo_children():
            widget.destroy()

        # draw tokens
        for i in range(len(self.gamestate.token_pool)):
            token_canvas = tk.Canvas(self.centre_upper, width=120, height=120)
            token_canvas.create_oval(20, 20, 80, 80, fill="gray")
            token_canvas.create_text(
                50, 50, text=settings.RESOURCE_COLOURS[i] + " empty", fill="white")
            if self.gamestate.temp_pool[i] > 0:
                token_canvas.create_text(
                    110, 110, text="+ " + str(self.gamestate.temp_pool[i]))
            for j in range(self.gamestate.token_pool[i]):
                if settings.RESOURCE_COLOURS[i] == "Black":
                    token_canvas.create_oval(20 + (2*(j+1)), 20 - (2*(j+1)), 80 + (2*(j+1)), 80 - (
                        2*(j+1)), fill=settings.RESOURCE_COLOURS[i], outline="gray")
                else:
                    token_canvas.create_oval(20 + (2*(j+1)), 20 - (2*(j+1)), 80 + (
                        2*(j+1)), 80 - (2*(j+1)), fill=settings.RESOURCE_COLOURS[i])

            if i == 5:
                # token is gold and can't be picked up
                token_canvas.grid(sticky="nsew", row=0, column=i+4)
            else:
                token_canvas.grid(sticky="nsew", row=0, column=i)
                if self.links_enabled:
                    token_canvas.bind("<Button-1>", lambda event, gamestate=self.gamestate,
                                      gemType=settings.RESOURCE_COLOURS[i]: self.pop_token(gemType))
                    token_canvas.bind("<Button-3>", lambda event, gamestate=self.gamestate,
                                      gemType=settings.RESOURCE_COLOURS[i]: self.push_token(gemType))

        # draw token button
        if self.gamestate.temp_pool != [0, 0, 0, 0, 0, 0]:
            token_button = tk.Button(self.centre_upper, pady=5, padx=5, text="Pick up tokens",
                                     command=lambda: self.validate_token_selection(self.gamestate))
            token_reset_button = tk.Button(self.centre_upper, pady=5, padx=5, text="Reset selection",
                                           command=lambda: self.reset_token_selection(self.gamestate))
        else:
            token_button = tk.Button(
                self.centre_upper, pady=5, padx=5, text="Pick up tokens", state="disabled")
            token_reset_button = tk.Button(self.centre_upper, pady=5, padx=5, text="Reset selection",
                                           state="disabled")
        token_button.grid(sticky="new", row=0, column=5)
        token_reset_button.grid(sticky="ew", row=0, column=5)

        # draw nobles
        noble_frame = tk.Frame(self.centre_upper)
        noble_frame.grid(sticky="nsew", column=6, row=0, columnspan=3)
        noble_frame.grid_columnconfigure(
            [0, 1, 2, 3, 4], weight=1, uniform="col11")
        noble_frame.grid_rowconfigure(0, weight=1)

        for row in range(len(self.gamestate.noble_cards[1])):
            noble_wrapper = tk.Frame(noble_frame, padx=2, pady=2)
            if self.nobles_enabled:
                noble_wrapper.configure(bg="yellow")
            noble_wrapper.grid(row=0, column=row, sticky="nsew")
            noble_wrapper.grid_columnconfigure(0, weight=1)
            noble_wrapper.grid_rowconfigure(0, weight=1)
            card = self.gamestate.noble_cards[1][row]

            noble_card = self.draw_noble_card(card, noble_wrapper)
            noble_card.grid(row=0, column=0, sticky="nsew")
            if self.nobles_enabled:
                noble_card.bind("<Button-1>", lambda event, gamestate=self.gamestate,
                                index=row: self.acquire_noble(event, gamestate, index))

    def redraw_centre(self):

        for widget in self.centre_middle.winfo_children():
            widget.destroy()

        # draw development cards
        dev_card_frame = tk.Frame(self.centre_middle)
        dev_card_frame.grid(sticky="nsew", column=0, row=0)
        dev_card_frame.grid_columnconfigure(
            (0, 1, 2, 3, 4), weight=1, uniform="col7")
        dev_card_frame.grid_rowconfigure((0, 1, 2), weight=1, uniform="row7")

        for row in range(3):
            for col in range(len(self.gamestate.development_cards[1][row])):
                dev_card_wrapper = tk.Frame(dev_card_frame, padx=2, pady=2)
                dev_card_wrapper.grid(row=2-row, column=col, sticky="nsew")
                dev_card_wrapper.grid_columnconfigure(0, weight=1)
                dev_card_wrapper.grid_rowconfigure(0, weight=1)
                card = self.gamestate.development_cards[1][row][col]
                if col == 0:
                    dev_card = self.draw_dev_deck(card, dev_card_wrapper)
                else:
                    dev_card = self.draw_dev_card(card, dev_card_wrapper)
                dev_card.grid(row=0, column=0, sticky="nsew")

                # Get all children of development card display
                dev_card_objects = dev_card.winfo_children() + [dev_card]
                for object in dev_card_objects:

                    if self.links_enabled:
                        object.bind("<Button-3>", lambda event, gamestate=self.gamestate, level=row,
                                    index=col: self.reserve_dev_card(event, gamestate, level, index))
                        if col != 0:
                            object.bind("<Button-1>", lambda event, gamestate=self.gamestate,
                                        level=row,
                                        index=col,
                                        deck=self.gamestate.development_cards[1][row],
                                        player_id=(self.gamestate.turn % len(self.gamestate.players)): self.buy_dev_card(event, gamestate, level, index, player_id, deck, "board"))
                            object.bind('<Control-1>', lambda event, gamestate=self.gamestate,
                                        level=row,
                                        index=col,
                                        deck=self.gamestate.development_cards[1][row],
                                        card=card,
                                        player_id=(self.gamestate.turn % len(self.gamestate.players)): self.gold_token_window(event, gamestate, level, index, player_id, card, deck, "board"))

    def redraw_player(self, i):
        player_frames = [self.left_upper, self.right_upper,
                         self.left_lower, self.right_lower]

        for widget in player_frames[i].winfo_children():
            widget.destroy()

        frame = player_frames[i]
        active_turn = self.gamestate.turn % len(self.gamestate.players)

        if i == active_turn:
            player_frames[i].configure(bg="orange", padx=5, pady=5)
        else:
            player_frames[i].configure(bg="white")

        player_display = self.draw_player_summary(i, frame)
        player_display.grid_rowconfigure(
            list(range(24)), weight=1, uniform='row3')
        player_display.grid_columnconfigure(
            (0, 1, 2), weight=1, uniform='col3')
        player_display.grid(row=(0), column=0, sticky="nsew")
        player_display.grid_propagate(0)
