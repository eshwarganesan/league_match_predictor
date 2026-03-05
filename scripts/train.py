import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd

from models.ChampSelectMatchPredictor import ChampSelectMatchPredictor   # <-- your model file


# ========================================
# 1. Dataset Class
# ========================================

class LoLDataset(Dataset):
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        # Helper function: extract 10 player values
        def get_cols(prefix, dtype=torch.long):
            values = [row[f"{prefix}_{i}"] for i in range(10)]
            return torch.tensor(values, dtype=dtype)

        batch = {
            "champion_ids": get_cols("champ", torch.long),
            "roles": get_cols("role", torch.long),
            "ranks": get_cols("rank", torch.long),

            "spell1": get_cols("spell1", torch.long),
            "spell2": get_cols("spell2", torch.long),

            "rune_primary": get_cols("rune1", torch.long),
            "rune_secondary": get_cols("rune2", torch.long),

            "mastery_points": get_cols("mastery", torch.float),
            "winrate_player": get_cols("winrateP", torch.float),
            "winrate_champion": get_cols("winrateC", torch.float),

            "label": torch.tensor(row["label"], dtype=torch.float)
        }

        return batch


# ========================================
# 2. Training Function
# ========================================

def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0

    for batch in loader:
        # Move tensors to GPU/CPU
        for key in batch:
            batch[key] = batch[key].to(device)

        labels = batch["label"].unsqueeze(1)

        # Forward
        probs = model(batch)

        # Loss
        loss = criterion(probs, labels)

        # Backprop
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(loader)


# ========================================
# 3. Evaluation Function
# ========================================

def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in loader:
            for key in batch:
                batch[key] = batch[key].to(device)

            labels = batch["label"].unsqueeze(1)

            probs = model(batch)

            preds = (probs > 0.5).float()

            correct += (preds == labels).sum().item()
            total += labels.size(0)

    return correct / total


# ========================================
# 4. Main Training Script
# ========================================

def main():
    csv_path = "matches.csv"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Load dataset
    dataset = LoLDataset(csv_path)

    # Split dataset
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size

    train_set, test_set = random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=64)

    # Model
    model = LoLWinPredictor().to(device)

    # Loss + Optimizer
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Training loop
    epochs = 20

    for epoch in range(epochs):
        loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        acc = evaluate(model, test_loader, device)

        print(f"Epoch {epoch+1}/{epochs} | Loss={loss:.4f} | Test Acc={acc:.4f}")

    # Save model
    torch.save(model.state_dict(), "lol_predictor.pt")
    print("Model saved as lol_predictor.pt")


if __name__ == "__main__":
    main()
