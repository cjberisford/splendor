
"""
COM3610 - Dissertation Project
aca18cjb, (c) Chris Berisford 2021

splendor.py - Launches application and performs session analysis
"""

import tkinter as tk
import matplotlib
import gamestate, UI, settings
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pickle, random, time, os
import numpy as np

class Splendor:
    def __init__(self, root):

        # Select AI type randomly
        if settings.SELECT_AI_TYPE_RANDOMLY:
            ai_type = random.randint(0, 1)
        else:
            ai_type = settings.AI_TYPE

        self.gamestate = gamestate.GameState(
            settings.NUMBER_OF_PLAYERS, 
            settings.NUMBER_OF_AI_PLAYERS + settings.NUMBER_OF_PLAYERS, 
            ai_type
        )
        
        self.UI = UI.UI(root, self.gamestate)


def start():
    """Start a game of Splendor"""
    global game
    root = tk.Tk()
    game = Splendor(root)
    root.mainloop()


def restart():
    """Relaunch Splendor"""
    # Number of human players, Number of AI players
    start()


def graph_round_count(round_count):
    """Plots graph of average round count"""
    # example data
    mu = np.mean(round_count)  # mean of distribution
    sigma = np.std(round_count)  # standard deviation of distribution
    x = round_count

    fig, ax = plt.subplots(figsize=(10, 5))

    # the histogram of the data
    n, bins, patches = ax.hist(x,  bins=range(
        min(x), max(x) + 2, 1), density=True, color="midnightblue", ec="skyblue")

    # add a 'best fit' line
    y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
         np.exp(-0.5 * (1 / sigma * (bins - mu))**2))

    ax.plot(bins, y, '--', color="orchid")

    plt.xlim(25, 45)

    ax.set_xlabel('Round length', fontsize=14)
    ax.set_ylabel('Probability', fontsize=14)
    ax.set_title(r'Length of a game of Splendor',  fontsize=16, pad=20)

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()

    return fig, ax


def graph_turn_distribution(turn_data, round_count):
    """Plots graph of distribution of actions taken"""

    results = {}
    for round in range(round_count):
        results[round + 1] = [0, 0, 0, 0, 0, 0]

    for turn_no, action in turn_data:
        if action == 'B1':
            results[turn_no][0] += 1
        if action == 'B2':
            results[turn_no][1] += 1
        if action == 'B3':
            results[turn_no][1] += 1
        if action == 'T2':
            results[turn_no][2] += 1
        if action == 'T3':
            results[turn_no][2] += 1
        if action == 'RB':
            results[turn_no][3] += 1
        if action == 'RA':
            results[turn_no][3] += 1
        if action == 'E':
            results[turn_no][4] += 1

    category_names = ['Buy low level card', 'Buy high level card', 'Pick up tokens',
                      'Reserve card', 'No valid moves']

    data = np.array(list(results.values()))

    # print(data[:, 4].sum())
    print(data.sum())
    row_sums = data.sum(axis=1)

    normalised_data = data / row_sums[:, np.newaxis]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='lightgray', linestyle='dashed')

    width = 0.8
    index = np.arange(round_count)

    b1 = np.array(normalised_data[:, 0])
    b2 = np.array(normalised_data[:, 1])
    tx = np.array(normalised_data[:, 2])
    rx = np.array(normalised_data[:, 3])
    e = np.array(normalised_data[:, 4])

    # Plot purchases
    p1 = plt.bar(index, b1, width, bottom=b2,
                 color='#0b0b30', label=category_names[0])
    p2 = plt.bar(index, b2, width,
                 color='#2424a0', label=category_names[1])

    # Plot tokens
    p4 = plt.bar(index, tx, width, bottom=b1+b2,
                 color='orchid', label=category_names[2])

    # Plot reservations
    p6 = plt.bar(index, rx, width, bottom=b1+b2+tx,
                 color='gold', label=category_names[3])

    # Plot errors
    p8 = plt.bar(index, e, width, bottom=b1+b2+tx+rx,
                 color='darkgrey', label=category_names[4])


    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    plt.xlim(0, 35)

    ax.set_xlabel('Round number', fontsize=14)
    ax.set_ylabel('Proportion of actions', fontsize=14)
    ax.set_title('Action distribution by round number', fontsize=16, pad=20)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(prop={"size": 12}, loc='center left',
              bbox_to_anchor=(1, 0.5), frameon=False)

    return fig, ax

def graph_risk_distribution(turn_data):
    """Draw pie chart of risk breakdown"""

    labels = ["Beneficial reservation", 
    "Attacking reservation",
    "Reserve facedown card",
    "Hold off buying card",
    "Pick up two tokens"]
    to_plot = np.array([i for i in turn_data.values() if i > 0])

    percent = 100.*to_plot/to_plot.sum()

    # patches, texts = plt.pie(to_plot, startangle=90, radius=1.2)
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, percent)]
    colors = ['#0b0b30','#2424a0', 'darkgrey', 'orchid','gold']



    # explode = [0] * len(to_plot)
    explode = (0, 0, 0, 0.15, 0)


    fig1, ax1 = plt.subplots()
    ax1.pie(to_plot, explode=explode, colors=colors, labels=None,
        shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.legend(labels=labels)

    plt.title('Human risk taking profile', weight='bold', size=14)
    plt.tight_layout()

    plt.show()



def run_simulation():
    """Execute automated simulation"""

    ID_TO_LOG = 0

    failed_games = 0
    round_count = []
    turn_data = []
    risk_count = 0
    errors = 0
    total_turns = 0
    for i in range(settings.EPOCHS):
        print("Simulating game", i+1, "of", settings.EPOCHS)
        start()
        game_summary = game.gamestate.game_summary
        if game_summary.game_completed == True:

            round_count.append(game_summary.rounds)
            risk_count += sum(value for value in game_summary.risk_data[ID_TO_LOG].values())

            # for player in game.gamestate.players:
            #     for move_number, action in game_summary.turn_data[player.id].items():
            #         turn_data.append((move_number, action))

            for move_number, action in game_summary.turn_data[ID_TO_LOG].items():
                turn_data.append((move_number, action))

            errors += game.gamestate.game_summary.errors
            total_turns += game.gamestate.game_summary.rounds
        else:
            failed_games += 1
    gcr = (len(round_count) / settings.EPOCHS) * 100

    epr = (errors / total_turns) * 100
    print("Game completion rate =", gcr, "%",
          "Total errors", errors, "Error rate:", epr, "%", "Failed games:", failed_games)
    graph_turn_distribution(turn_data, max(round_count))
    graph_round_count(round_count)
    print("Risk count = "+ str(risk_count))
    print("Average risk/game = "+ str(risk_count / settings.EPOCHS))


    plt.show()



def run_scenario():
    """Play a game featuring a human player"""
    # Need to pass params here. AI type, number of AI players, etc.
    start()

    game_summary = game.gamestate.game_summary

    # file_to_write = open("data.pkl", "wb")

    # pickle.dump(game_summary, file_to_write)
    # file_to_write.close()
    # What do we do with the game data? Probably graph it. What data do we need?
    # Human player data.
    # AI player data when it plays against a human
    # Dump this information to a file.

    # What data do you want to write to the file?
    ############################################################################
 
    # Create game summary dictionary object
    session_log = {}
    session_log["ai_type"] = game_summary.ai_type
    session_log["turn_data"] = game_summary.turn_data
    session_log["risk_data"] = game_summary.risk_data
    session_log["rounds"] = game_summary.rounds
    session_log["winning_player"] = game_summary.winning_player
    session_log["errors"] = game_summary.errors
    session_log["game_completed"] = game_summary.game_completed

    if session_log["game_completed"] == True:
        # Only record logs of completed games
        print("Game exited, logging session...")
        file_name = "session_logs/session-id-" + time.strftime("%Y-%b-%d__%H_%M_%S",time.localtime()) + ".pickle"
        file_to_write = open(file_name, "wb")
        pickle.dump(session_log, file_to_write)
        file_to_write.close()
    else:
         print("Game exited before completion - data not logged.")


def process_data():
    """Collate all session log files and process the data""" 
    
   # List all files in a directory using scandir()
    game_data = {}
    file_count = 0
    basepath = 'session_logs/'
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.is_file():

                file_count += 1

                # reading the data from the file
                with open(entry, 'rb') as handle:
                    data = handle.read()
                
                # reconstructing the data as dictionary
                d = pickle.loads(data)
                game_data[file_count] = d

    print("Scanner detected "+str(file_count)+ " session log files...")   

    # Print results of games from both AI types
    turn_data = []
    round_count_total = []

    for ai_type in range(2):
        print()
        if ai_type == 0:
            print("Searching for standard AI game logs...")
        else:
            print("Searching for modified AI game logs...")

        # Do something with the game data here
        human_wins = 0
        total_games = 0
        player_risks = 0
        ai_risks = 0
        round_count = []
        human_risk_distribution = {
                "R1": 0, # Beneficial reservation
                "R2": 0, # Attacking reservation
                "R3": 0, # Reserve facedown card
                "R4": 0, # Hold off from buying card
                "R5": 0 # Pick up two tokens
            }

        ai_type_count = 0
        for game in game_data.values():
            if game["game_completed"] and game["ai_type"] == ai_type:
                ai_type_count += 1
                # Add winner to count
                if game["winning_player"] == 1:
                    human_wins += 1
                # Add game to total count
                total_games += 1
                # Count number of risks taken by player
                player_risks += sum(value for value in game["risk_data"][0].values())
                # Count number of risks taken by AI
                ai_risks += sum(value for value in game["risk_data"][1].values())
                # print(game["risk_data"][1].values()) -- USE THIS TO DO RISK BREAKDOWN
                # Append round length
                round_length = game["rounds"]
                round_count.append(round_length)
                round_count_total.append(round_length)
                # Append turn data
                for move_number, action in game["turn_data"][0].items():
                    turn_data.append((move_number, action))

                # Append risk data -- set to 0 for human
                for risk, count in game["risk_data"][0].items():
                    human_risk_distribution[risk] += count

                    

        # Calculate and print game aggregate data
        if total_games == 0:
            print("No completed games found in session log files!")
        else:
            print("Found " + str(ai_type_count) + " matching files")
            win_percentage = human_wins / total_games * 100
            total_risks = player_risks / total_games
            total_ai_risks = ai_risks / total_games
            print("Human win percentage: " + str(win_percentage) + "%")
            print("Risks taken by human per game: " + str(total_risks))
            print("Risks taken by AI per game: " + str(total_ai_risks))
            print("Average round length: " + str(np.mean(np.array(round_count))))
            # Graph human action distribution 

        print(human_risk_distribution)

    
    graph_turn_distribution(turn_data, max(round_count_total))
    graph_round_count(round_count_total)
    graph_risk_distribution(human_risk_distribution)
    plt.show()


if __name__ == "__main__":
    print("=*=*=*=*=*=*=*=*=*=ENVIRONMENT=*=*=*=*=*=*=*=*=*=")
    print('tkinter: {}'.format(tk.TkVersion))
    print('matplotlib: {}'.format(matplotlib.__version__))
    print('numpy: {}'.format(np.__version__))
    print("=*=*=*=*=*=*=*=*=*=*=SESSION=*=*=*=*=*=*=*=*=*=*=")

    if settings.PROCESS_DATA:
        process_data()
    else:
        # If no human players in game, run AI simulation
        if settings.NUMBER_OF_PLAYERS == 0:
            # Params: Number of times to run,
            run_simulation()
        else:
            print("Launching game window...")
            run_scenario()
        
