import os
import unittest

from commure_assignment_chess.common import FileHandler
from commure_assignment_chess.lichess import Lichess


class LichessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.SAVE_TO_FILE = True
        self.handler = FileHandler(__file__)

        self.lichess = Lichess()

    def tearDown(self) -> None:
        self.lichess.close()

    def test_get_one_leaderboard(self):
        leaderboard = self.lichess.get_one_leaderboard(nb=2, perfType="classical")

        if leaderboard and self.SAVE_TO_FILE:
            self.handler.to_file("output/test_get_one_leaderboard.json", leaderboard)

    def test_get_rating_history_of_a_user(self):
        rating_history = self.lichess.get_rating_history_of_a_user(
            username="koalanaattor"
        )

        if rating_history and self.SAVE_TO_FILE:
            self.handler.to_file(
                "output/test_get_rating_history_of_a_user.json", rating_history
            )
