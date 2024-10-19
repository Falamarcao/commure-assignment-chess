#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
from json import dumps as json_dumps

import pandas as pd

from commure_assignment_chess.lichess import Lichess


class Assignment:

    def __init__(self):
        self.today = datetime.today()
        self.date_list = [self.today.year, self.today.month, self.today.day]

        self.months = {
            0: "Jan",
            1: "Feb",
            2: "Mar",
            3: "Apr",
            4: "May",
            5: "Jun",
            6: "Jul",
            7: "Aug",
            8: "Sep",
            9: "Oct",
            10: "Nov",
            11: "Dec",
        }

        self.lichess = Lichess()

    def is_within_last_30_days(self, check_date):
        # Calculate the date 30 days ago
        cutoff_date = self.today - timedelta(days=30)

        # Check if the check_date is between cutoff_date and today
        return cutoff_date <= check_date <= self.today

    def list_50_top_classical_chess_players_usernames(self):
        # 1. List the top 50 classical chess players. Just print their usernames.
        usernames = []
        for user in self.lichess.get_one_leaderboard(nb=50, perfType="classical")[
            "users"
        ]:
            usernames.append(user["username"])

        return usernames

    def rating_history_chess_player(self, username: str, complete_date: bool = False):
        rating_history = self.lichess.get_rating_history_of_a_user(username=username)

        data = dict()
        for game in rating_history:
            if game["name"] == "Classical":
                for record in reversed(game["points"]):
                    date = datetime(record[0], record[1] + 1, record[2])
                    if self.is_within_last_30_days(date):
                        if complete_date:
                            data.update({date.strftime("%Y-%m-%d"): record[3]})
                        else:
                            data.update(
                                {f"{self.months[record[1]]} {record[2]}": record[3]}
                            )
                    else:
                        break

        date_format = "%Y-%m-%d" if complete_date else "%b %d"

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
        df["Value"] = (
            df["Value"].ffill().bfill()
        )  # Use ffill and bfill directly on the Series

        # Convert the index (Timestamps) back to strings for dict compatibility
        return {
            date.strftime(date_format): int(value)
            for date, value in df["Value"].to_dict().items()
        }

    def rating_history_n_players_30_days_to_csv(self, number_of_players: int):
        players = self.lichess.get_one_leaderboard(
            nb=number_of_players, perfType="classical"
        )["users"]

        data = []
        for player in players:
            data.append(
                {
                    player["username"]: self.rating_history_chess_player(
                        player["username"], complete_date=True
                    )
                }
            )

        # Extract the first user's dates (since they are the same and in order)
        dates = list(data[0][list(data[0].keys())[0]].keys())

        # Prepare the data for CSV
        csv_data = []

        for entry in data:
            for username, values in entry.items():
                row = [username]  # Start the row with the username
                row.extend(
                    [values.get(date, 'N/A') for date in dates]
                )  # Add the values in date order
                csv_data.append(row)

        # Define the CSV file path
        csv_file_path = f"rating_history_{number_of_players}_players_30_days.csv"

        # Write to CSV
        with open(csv_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write the header: "Username" followed by the dates
            writer.writerow(["Username"] + dates)
            # Write the rows: username followed by values for each date
            writer.writerows(csv_data)


if __name__ == "__main__":
    assignment = Assignment()

    print(assignment.list_50_top_classical_chess_players_usernames())

    player = assignment.lichess.get_one_leaderboard(nb=1, perfType="classical")[
        "users"
    ][0]

    print(f'- {player["username"]}, ', 
        json_dumps(
            assignment.rating_history_chess_player(username=player["username"]),
            indent=4,
        )
    )

    assignment.rating_history_n_players_30_days_to_csv(number_of_players=50)
