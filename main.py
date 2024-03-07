import time
from requests import get
from matplotlib.pyplot import ylabel, plot, grid, show, xlabel, title
import os
import dotenv
dotenv.load_dotenv(".env")
bearer = os.environ.get("API_KEY")


game = "csgo"
elo_list = []


def get_id(nickname):
    data = get(f"https://open.faceit.com/data/v4/players?nickname={nickname}",
               headers={"Authorization": "Bearer " + bearer}).json()
    if "errors" in data:
        print("Error:", data["errors"][0]["message"])
        main()
    return data["player_id"]


def get_start_elo(nickname):
    data = get(f"https://open.faceit.com/data/v4/players?nickname={nickname}",
               headers={"Authorization": "Bearer " + bearer}).json()
    if "errors" in data:
        print("Error:",data["errors"][0]["message"])
        main()
    return int(data["games"]["csgo"]["faceit_elo"])


def get_matches(count, offset, user_id):
    time.sleep(1)
    all_matches = get(f"https://open.faceit.com/data/v4/players/{user_id}/history?game={game}"
                               f"&limit={count}&offset={offset}",
                      headers={"Authorization": "Bearer " + bearer}).json()
    if "errors" in all_matches:
        print("Error:",all_matches["errors"][0]["message"])
        main()
    return all_matches["items"]


def get_team(match, user_id):
    for player in match["teams"]["faction1"]["players"]:
        if player["player_id"] == user_id:
            return "faction1"
    for player in match["teams"]["faction2"]["players"]:
        if player["player_id"] == user_id:
            return "faction2"


def return_elo(winner, team):
    if winner == team:
        return +25
    else:
        return -25


def get_elo(match, user_id):
    winner_team = match["results"]["winner"]
    team = get_team(match, user_id)
    return return_elo(winner_team, team)


def show_chart(elo_list):
    elo_list = elo_list[:len(elo_list)-9]
    full_elo = []
    matches = []
    for elo in elo_list[::-1]:
        full_elo.append(elo)

    for i in range(10, len(full_elo) + 10):
        matches.append(i)

    plot(matches, full_elo)
    title('Elo Progression')
    xlabel('Matches')
    ylabel('Elo')
    grid()
    show()

def main():
    username = input("Enter your Faceit Username: ")
    offset = 0
    matches_remaining = True
    user_id = get_id(username)
    start_elo = get_start_elo(username)
    elo_list.append(start_elo)
    match_index = 0
    while matches_remaining:
        matches = get_matches(50, offset, user_id)
        if len(matches) < 50:
            matches_remaining = False
        print("Processing Matches " + str(offset) + " to " + str(offset + len(matches)))
        for match in matches:
            if match["match_type"] == "" and match["game_mode"] == "5v5" and match["organizer_id"] == "faceit":
                elo_list.append(elo_list[match_index] - get_elo(match, user_id))
                match_index += 1
        offset += 50
    show_chart(elo_list)


main()



