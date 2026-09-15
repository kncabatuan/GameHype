import pandas as pd
from api import steam_reviews
from typing import Dict, Any

# Bayesian Average Constants:
DUMMY_COUNT_FOR_RAWG: int = 25
DUMMY_RATING_FOR_RAWG: float = 0.50
DUMMY_COUNT_FOR_STEAM: int = 1000
DUMMY_RATING_FOR_STEAM: float = 0.70


class Game:
    """Creates a class to contain the data related to the selected game"""

    def __init__(self, raw_data: Dict[str, Any]) -> None:
        """
        Initializes the Game class

        Args:
            raw_data (Dict[str, Any]): The selected game's data fetched from RAWG API
        """
        self.raw_data = raw_data
        self.title = self.raw_data.get("name", None)
        self.rawg_ratings = self.raw_data.get("ratings", [])

    def get_verdict(self) -> tuple[str, str]:
        """
        Handles the calculation of the final score and returns the verdict label based on the score.

        Returns:
            tuple[str, str]: A tuple containing the rounded score and the verdict label.
        """
        reviews_data = steam_reviews.get_steam_reviews(self.title)
        if not reviews_data:
            score = self.calculate_dampened_score_rawg
        else:
            positive_count = reviews_data.get("total_positive", 0)
            negative_count = reviews_data.get("total_negative", 0)

            score = self.calculate_dampened_score_steam(positive_count, negative_count)

        return self.get_verdict_label(score)

    @property
    def calculate_raw_score(self) -> list[float, int]:
        """
        Calculates the raw score based on the RAWG ratings and returns the raw score and total count.

        Returns:
            list[float, int]: A list containing the raw score and total count of ratings.
        """
        if not self.rawg_ratings:
            return [0, 0]

        df = pd.DataFrame(self.rawg_ratings)

        custom_weights = {5: 1.00, 4: 0.85, 3: 0.5, 1: 0.00}

        df["custom_weights"] = df["id"].map(custom_weights)
        raw_score = (df["custom_weights"] * df["count"]).sum()
        total_count = df["count"].sum()

        return [raw_score, total_count]

    @property
    def calculate_dampened_score_rawg(self) -> float | None:
        """
        Handles the calculation of the dampened score based on RAWG ratings using bayesian average formula.

        Returns:
            float | None: The dampened score or None if there are no RAWG ratings.
        """
        if not self.rawg_ratings:
            return None

        raw_score, total_count = self.calculate_raw_score

        dampened_score = (
            raw_score + (DUMMY_COUNT_FOR_RAWG * DUMMY_RATING_FOR_RAWG)
        ) / (total_count + DUMMY_COUNT_FOR_RAWG)

        return dampened_score

    def calculate_dampened_score_steam(
        self, positive_count: int, negative_count: int
    ) -> float | None:
        """
        Handles the calculation of the damepened score based on Steam reviews using bayesian average formula

        Returns:
            float | None: The dampened score or None if there are no Steam reviews.
        """
        total_count = positive_count + negative_count
        if total_count == 0:
            return

        dampened_score = (
            positive_count + (DUMMY_COUNT_FOR_STEAM * DUMMY_RATING_FOR_STEAM)
        ) / (total_count + DUMMY_COUNT_FOR_STEAM)

        return dampened_score

    def get_verdict_label(self, score: float) -> tuple[float, str]:
        """
        Returns the appropriate verdict label based on calculated score

        Args:
            score (float): The calculated score for the game.

        Returns:
            tuple[float, str]: A tuple containing the rounded score and the verdict label.
        """
        if not score:
            return "N/A", "N/A"

        rounded_score = round(score * 100, 2)
        verdict = ""

        if rounded_score >= 90:
            verdict = "🐐 GOTY Material"
        elif rounded_score >= 70:
            verdict = "🔥 Certified Banger"
        elif rounded_score >= 50:
            verdict = "🍿 Mid (Wait for Steam Sale)"
        elif rounded_score >= 30:
            verdict = "🚨 Overhyped Disappointment"
        elif rounded_score > 0:
            verdict = "🗑️ Nuclear Dumpster Fire"
        else:
            rounded_score = "N/A"
            verdict = "N/A"

        return rounded_score, verdict
