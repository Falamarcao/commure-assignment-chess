#!/usr/bin/env python3

from typing import List, Union
import csv
from datetime import datetime, timedelta
from json import dumps as json_dumps

import polars as pl  # Import Polars

from commure_assignment_chess.lichess import Lichess


class Assignment:

    def __init__(self):
        self.today = datetime.today()
        self.lichess = Lichess()

    def is_within_last_30_days(self, check_date: datetime) -> bool:
        # Calculate the date 30 days ago
        cutoff_date = self.today - timedelta(days=30)
        # Check if the check_date is between cutoff_date and today
        return cutoff_date <= check_date <= self.today

    def list_n_top_classical_chess_players_usernames(self, n: int) -> List[str]:
        # List the top n classical chess players and return their usernames
        usernames = [
            user["username"]
            for user in self.lichess.get_one_leaderboard(nb=n, perfType="classical")[
                "users"
            ]
        ]
        return usernames

    def rating_history_chess_player(
        self, username: str, complete_date: bool = False, returnDataFrame: bool = False
    ) -> Union[dict, pl.DataFrame]:

        date_format = "%Y-%m-%d" if complete_date else "%b %d"
        rating_history = self.lichess.get_rating_history_of_a_user(username=username)

        # Use a list comprehension to create data
        data = [
            {"Date": datetime(record[0], record[1] + 1, record[2]), "Value": record[3]}
            for game in rating_history
            if game["name"] == "Classical"
            for record in reversed(game["points"])
            if self.is_within_last_30_days(
                datetime(record[0], record[1] + 1, record[2])
            )
        ]

        # Create a Polars DataFrame from the data
        df = pl.DataFrame(data)

        # Convert 'Date' to date format in Polars
        df = df.with_columns(pl.col("Date").cast(pl.Date))

        # Create a date range for the last 30 days
        end_date = self.today.date()  # Ensure end_date is just a date
        date_range = [(end_date - timedelta(days=i)) for i in range(30)][::-1]

        # Create a DataFrame from the date range list directly
        date_range_df = pl.DataFrame({"Date": date_range})

        # Ensure the 'Date' column in date_range_df is of type date
        date_range_df = date_range_df.with_columns(
            pl.col("Date").cast(pl.Date).dt.strftime(date_format)
        )
        df = df.with_columns(pl.col("Date").cast(pl.Date).dt.strftime(date_format))

        # Join to include all dates in the last 30 days
        df = date_range_df.join(df, on="Date", how="full").drop("Date_right")

        # Fill missing values with the last available date's value
        df = df.fill_null(strategy="forward").fill_null(strategy="backward")

        # Convert values to integers
        df = df.with_columns(pl.col("Value").cast(pl.Int32))

        # Add username column as first column
        if returnDataFrame:
            headers = df["Date"].to_list()
            df = df.drop("Date").transpose(include_header=False)
            df.columns = headers
            return df.with_columns(pl.lit(username).alias("username")).select(
                ["username"] + df.columns
            ) # add username column as first column
        else:
            df = df.transpose()
            return {k: v for k, v in df.iter_columns()}

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

        df = pl.concat(player_dfs)

        print(df.head())

        # Write to CSV
        df.write_csv(f"rating_history_{number_of_players}_players_30_days.csv")


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
