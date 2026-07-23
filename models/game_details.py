import pandas as pd
import numpy as np
from typing import Dict, Any

#Bayesian Average Constants:
DUMMY_COUNT = 25
DUMMY_RATING = 0.50


class Game:
    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data
        self.title = self.raw_data.get("name", None)
        self.ratings = self.raw_data.get("ratings", [])

    @property
    def calculate_raw_score(self):
        df = pd.DataFrame(self.ratings)
        
        custom_weights = {
            5: 1.00,
            4: 0.75, 
            3: 0.25,
            1: 0.00
        }

        df["custom_weights"] = df["id"].map(custom_weights)
        raw_score = (df["custom_weights"]*df["count"]).sum()
        total_count = df["count"].sum()

        return [raw_score, total_count]

    @property
    def calculate_dampened_score(self):
        if not self.ratings:
            return None
        
        raw_score, total_count = self.calculate_raw_score

        dampened_score = (raw_score + (DUMMY_COUNT * DUMMY_RATING))/(total_count + DUMMY_COUNT)

        return dampened_score
    
    def get_verdict(self):
        score = round(self.calculate_dampened_score * 100, 2)
        verdict = ""

        if score >= 85:
            verdict = "🐐 GOTY Material"
        elif score >= 70:
            verdict = "🔥 Certified Banger"
        elif score >= 50:
            verdict = "🍿 Mid (Wait for Steam Sale)"
        elif score >= 30:
            verdict = "🚨 Overhyped Disappointment"
        else:
            verdict = "🗑️ Nuclear Dumpster Fire"

        return score, verdict
