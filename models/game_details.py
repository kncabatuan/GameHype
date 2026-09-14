import pandas as pd
from api import steam_reviews
from typing import Dict, Any

#Bayesian Average Constants:
DUMMY_COUNT_FOR_RAWG = 25
DUMMY_RATING_FOR_RAWG = 0.50
DUMMY_COUNT_FOR_STEAM = 1000
DUMMY_RATING_FOR_STEAM = 0.70


class Game:
    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data
        self.title = self.raw_data.get("name", None)
        self.rawg_ratings = self.raw_data.get("ratings", [])

    @property
    def calculate_raw_score(self):
        df = pd.DataFrame(self.rawg_ratings)
        
        custom_weights = {
            5: 1.00,
            4: 0.85, 
            3: 0.5,
            1: 0.00
        }

        df["custom_weights"] = df["id"].map(custom_weights)
        raw_score = (df["custom_weights"]*df["count"]).sum()
        total_count = df["count"].sum()

        return [raw_score, total_count]

    @property
    def calculate_dampened_score_rawg(self):
        if not self.rawg_ratings:
            return None
        
        raw_score, total_count = self.calculate_raw_score

        dampened_score = (raw_score + (DUMMY_COUNT_FOR_RAWG * DUMMY_RATING_FOR_RAWG))/(total_count + DUMMY_COUNT_FOR_RAWG)

        return dampened_score
    
    def get_verdict(self):
        reviews_data = steam_reviews.get_steam_reviews(self.title)
        if not reviews_data:
            score = self.calculate_dampened_score_rawg
        else:
            positive_count = reviews_data.get("total_positive", 0)
            negative_count = reviews_data.get("total_negative", 0)

            score = self.calculate_dampened_score_steam(positive_count, negative_count)

        return self.get_verdict_label(score)

    def calculate_dampened_score_steam(self, positive_count, negative_count):
        total_count = positive_count + negative_count
        if total_count == 0:
            return
        
        dampened_score = (positive_count + (DUMMY_COUNT_FOR_STEAM * DUMMY_RATING_FOR_STEAM)) / (total_count + DUMMY_COUNT_FOR_STEAM)

        return dampened_score

    def get_verdict_label(self, score):
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
        else:
            verdict = "🗑️ Nuclear Dumpster Fire"

        return rounded_score, verdict
