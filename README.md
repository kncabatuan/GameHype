# 🎮 GameHype

An extremely simple **game rating aggregator and sentiment analyzer** for Windows. 

Ever wonder if a game actually lives up to the hype without wading through hundreds of mixed user reviews? **GameHype** solves this by calculating a statistically adjusted "Hype Score" and verdict in real time!


---


## Features

- **Steam API Integration:** Fetches live review counts and sentiment percentages.
- **Bayesian Score Normalization:** Applies statistical dampening to prevent low-sample review bias.
- **RAWG Fallback:** Automatically fetches metadata and community ratings for non-Steam titles.
- **Instant Verdicts:** Categorizes game ratings into quick, clear visual summary.


---


## Running From Source

If you want to work with the **source code**:  

```bash
git clone https://github.com/kncabatuan/GameHype.git
cd GameHype
pip install -r requirements.txt
python gamehype.py
```


---


## Tips

Make sure Python 3.10+ is installed if running from source.


---


## This project would not be possible without:

    - Steam Web API – Used for live user reviews and player metrics.    
    - RAWG API – Used for broader game catalog data and secondary ratings.


---


## ⚠ Disclaimer

This tool is for educational and personal use only.

All game titles, artwork, and trademarks belong to their respective owners.


---


## 📜 License

This project is licensed under the MIT License.