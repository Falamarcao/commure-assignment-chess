#!/usr/bin/env python3

from typing import List, Union

import csv
from datetime import datetime, timedelta
from json import dumps as json_dumps

import pandas as pd

from commure_assignment_chess.lichess import Lichess


class Assignment:

    def __init__(self):
        self.today = datetime.today()
        self.lichess = Lichess()

    def is_within_last_30_days(self, check_date) -> bool:
        # Calculate the date 30 days ago
        cutoff_date = self.today - timedelta(days=30)

        # Check if the check_date is between cutoff_date and today
        return cutoff_date <= check_date <= self.today

    def list_n_top_classical_chess_players_usernames(self, n: int) -> List[str]:
        # 1. List the top n classical chess players. Just print their usernames.
        usernames = []
        for user in self.lichess.get_one_leaderboard(nb=n, perfType="classical")[
            "users"
        ]:
            usernames.append(user["username"])

        return usernames

    def rating_history_chess_player(
        self, username: str, complete_date: bool = False, returnDataFrame: bool = False
    ) -> Union[dict, pd.DataFrame]:
        date_format = "%Y-%m-%d" if complete_date else "%b %d"

        rating_history = self.lichess.get_rating_history_of_a_user(username=username)

        data = dict()
        for game in rating_history:
            if game["name"] == "Classical":
                for record in reversed(game["points"]):
                    date = datetime(record[0], record[1] + 1, record[2])
                    if self.is_within_last_30_days(date):
                        data.update({date.strftime(date_format): record[3]})
                    else:
                        break

        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(list(data.items()), columns=["Date", "Value"])

        # Convert 'Date' to datetime format
        df["Date"] = pd.to_datetime(df["Date"], format=date_format)

        # Set the 'Date' as index
        df.set_index("Date", inplace=True)

        # Reindex to include all dates in the last 30 days
        date_range = pd.date_range(end=df.index.max(), periods=30)
        df = df.reindex(date_range)

        # Fill missing values with the last available date's value
        df["Value"] = df["Value"].ffill().bfill().astype(int)

        df.index = df.index.strftime(date_format)

        if returnDataFrame:
            df = df.transpose()
            df.insert(0, "username", username)  # insert collumn username
            return df
        else:
            return df.to_dict()["Value"]

    def rating_history_n_players_30_days_to_csv(self, number_of_players: int) -> None:
        players = self.lichess.get_one_leaderboard(
            nb=number_of_players, perfType="classical"
        )["users"]

        player_dfs = [
            self.rating_history_chess_player(
                username=player["username"], complete_date=True, returnDataFrame=True
            )
            for player in players
        ]

        df = pd.concat(player_dfs)

        df.to_csv(f"rating_history_{number_of_players}_players_30_days.csv", index=False)


if __name__ == "__main__":
    assignment = Assignment()

    print(assignment.list_n_top_classical_chess_players_usernames(n=50))

    player = assignment.lichess.get_one_leaderboard(nb=1, perfType="classical")[
        "users"
    ][0]

    print(
        f'- {player["username"]}, ',
        json_dumps(
            assignment.rating_history_chess_player(username=player["username"]),
            indent=4,
        ),
    )

    assignment.rating_history_n_players_30_days_to_csv(number_of_players=50)
