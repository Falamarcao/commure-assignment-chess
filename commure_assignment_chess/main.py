#!/usr/bin/env python3

from json import dumps as json_dumps

from datetime import datetime, timedelta

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

    def rating_history_top_chess_player(self):
        player = self.lichess.get_one_leaderboard(nb=1, perfType="classical")["users"][0]

        rating_history = self.lichess.get_rating_history_of_a_user(
            username=player["username"]
        )

        results = dict()
        for game in rating_history:
            if game["name"] == "Classical":
                for record in reversed(game["points"]):
                    if self.is_within_last_30_days(
                        datetime(record[0], record[1] + 1, record[2])
                    ):
                        results.update({f"{self.months[record[1]]} {record[2]}": record[3]})
                    else:
                        break

        return results


if __name__ == "__main__":
    assignment = Assignment()

    print(assignment.list_50_top_classical_chess_players_usernames())

    print(json_dumps(assignment.rating_history_top_chess_player(), indent=4))
