import json
import pandas as pd

# Lane order is fixed
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]

# Rank encoding helper
TIERS = {
    "IRON": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
    "PLATINUM": 4,
    "EMERALD": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9
}

DIVISIONS = {
    "IV": 0,
    "III": 1,
    "II": 2,
    "I": 3
}


# ==========================================
# Convert Rank → Single Integer
# ==========================================

def rank_to_number(rank_dict):
    tier = rank_dict["Tier"]
    division = rank_dict["Division"]

    tier_val = TIERS[tier]

    # Master+ tiers have no division
    div_val = DIVISIONS.get(division, 0)

    return tier_val * 4 + div_val


# ==========================================
# Main Conversion Function
# ==========================================

def convert_matches_to_csv(json_file, output_csv):
    with open(json_file, "r") as f:
        matches = json.load(f)

    rows = []

    for match in matches:

        row = {}
      
        # Label: Team A win = 1, Team B win = 0
        row["label"] = 1 if match["Winner"] == "Team A" else 0

        player_index = 0

        # -----------------------------
        # Process Team A then Team B
        # -----------------------------
        for team_key in ["Team A", "Team B"]:
            team = match[team_key]

            for role in ROLE_ORDER:
                player = team[role]

                champ_id = player["ChampionID"]

                rune_primary = player["Runes"]["Primary"]
                rune_secondary = player["Runes"]["Secondary"]

                spell1, spell2 = player["SummonerSpells"]

                mastery = player["Mastery"]

                rank_num = rank_to_number(player["Rank"])

                # Fill row columns
                row[f"champ_{player_index}"] = champ_id
                row[f"role_{player_index}"] = ROLE_ORDER.index(role)

                row[f"rank_{player_index}"] = rank_num

                row[f"spell1_{player_index}"] = spell1
                row[f"spell2_{player_index}"] = spell2

                row[f"rune1_{player_index}"] = rune_primary
                row[f"rune2_{player_index}"] = rune_secondary

                row[f"mastery_{player_index}"] = mastery

                player_index += 1

        rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Save
    df.to_csv(output_csv, index=False)

    print("Saved:", output_csv)
    print("Total matches:", len(df))


# ==========================================
# Run Script
# ==========================================

if __name__ == "__main__":
    convert_matches_to_csv(
        json_file="debug.json",
        output_csv="matches.csv"
    )
