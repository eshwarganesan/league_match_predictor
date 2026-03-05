from torch.utils.data import Dataset
import torch


class LoLDataset(Dataset):
    def __init__(self, data):
        self.data = data  # list of match dicts

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        match = self.data[idx]

        batch = {
            "champion_ids": torch.tensor(match["champion_ids"], dtype=torch.long),
            "roles": torch.tensor(match["roles"], dtype=torch.long),
            "ranks": torch.tensor(match["ranks"], dtype=torch.long),

            "spell1": torch.tensor(match["spell1"], dtype=torch.long),
            "spell2": torch.tensor(match["spell2"], dtype=torch.long),

            "rune_primary": torch.tensor(match["rune_primary"], dtype=torch.long),
            "rune_secondary": torch.tensor(match["rune_secondary"], dtype=torch.long),

            "mastery_points": torch.tensor(match["mastery_points"], dtype=torch.float),
            "winrate_player": torch.tensor(match["winrate_player"], dtype=torch.float),
            "winrate_champion": torch.tensor(match["winrate_champion"], dtype=torch.float),

            "label": torch.tensor(match["label"], dtype=torch.float)
        }

        return batch
