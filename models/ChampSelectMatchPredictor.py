import torch
import torch.nn as nn
import torch.nn.functional as F


class ChampSelectMatchPredictor(nn.Module):
    def __init__(
        self,
        num_champions=172,
        num_roles=5,
        num_ranks=9,
        num_spells=15,
        num_rune_trees=5,
        player_embed_dim=128
    ):
        super().__init__()

        # ============================
        # Embeddings (Categorical Inputs)
        # ============================

        self.champ_embed = nn.Embedding(num_champions, 32)
        self.role_embed = nn.Embedding(num_roles, 4)
        self.rank_embed = nn.Embedding(num_ranks, 4)
        self.spell_embed = nn.Embedding(num_spells, 4)
        self.rune_embed = nn.Embedding(num_rune_trees, 4)
        # self.mastery_embed = nn.Embedding(num_mastery_levels, 4)

        # Total per-player feature size
        self.player_input_dim = (
            32 + 4 + 4 +
            4 + 4 +
            4 + 4 +
            3   # numeric stats
        )

        # ============================
        # Player Encoder Network
        # ============================

        self.player_encoder = nn.Sequential(
            nn.Linear(self.player_input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),

            nn.Linear(256, player_embed_dim),
            nn.ReLU()
        )

        # ============================
        # Match-Level Network
        # ============================

        # Match vector includes:
        # TeamA pooled + TeamB pooled + difference
        # Lane matchups (5 lanes)
        match_input_dim = (
            player_embed_dim * 3 +      # TeamA, TeamB, TeamA-TeamB
            player_embed_dim * 5        # lane matchup vectors
        )

        self.match_mlp = nn.Sequential(
            nn.Linear(match_input_dim, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),

            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),

            nn.Linear(256, 128),
            nn.ReLU(),

            nn.Linear(128, 1)
        )

        self.matchup_fc = nn.Sequential(
            nn.Linear(player_embed_dim * 2, player_embed_dim),
            nn.ReLU(),
            nn.Linear(player_embed_dim, player_embed_dim)
        )

    # ============================
    # Forward Pass
    # ============================

    def forward(self, batch):
        """
        batch tensors must have shape (B, 10)

        Slots:
        0-4 = Team A (Top, Jg, Mid, ADC, Sup)
        5-9 = Team B (Top, Jg, Mid, ADC, Sup)
        """

        B = batch["champion_ids"].shape[0]

        # ---- Embeddings ----
        champ = self.champ_embed(batch["champion_ids"])
        role = self.role_embed(batch["roles"])
        rank = self.rank_embed(batch["ranks"])

        spell1 = self.spell_embed(batch["spell1"])
        spell2 = self.spell_embed(batch["spell2"])

        rune1 = self.rune_embed(batch["rune_primary"])
        rune2 = self.rune_embed(batch["rune_secondary"])

        # mastery_lvl = self.mastery_embed(batch["mastery_level"])

        # ---- Numeric features ----
        mastery_pts = batch["mastery_points"].unsqueeze(-1)
        winrate_player = batch["winrate_player"].unsqueeze(-1)
        winrate_champ = batch["winrate_champion"].unsqueeze(-1)

        # ---- Combine per-player features ----
        player_raw = torch.cat([
            champ, role, rank,
            spell1, spell2,
            rune1, rune2,
            mastery_pts,
            winrate_player,
            winrate_champ
        ], dim=-1)

        # Shape: (B, 10, feature_dim)
        player_raw = player_raw.view(B * 10, -1)

        # ---- Encode each player ----
        player_vec = self.player_encoder(player_raw)

        # Reshape back: (B, 10, embed_dim)
        player_vec = player_vec.view(B, 10, -1)

        # ============================
        # Split into Teams
        # ============================

        teamA = player_vec[:, :5, :]   # (B, 5, D)
        teamB = player_vec[:, 5:, :]   # (B, 5, D)

        # ============================
        # Team Synergy Pooling
        # ============================

        teamA_pool = teamA.mean(dim=1)   # (B, D)
        teamB_pool = teamB.mean(dim=1)   # (B, D)

        team_diff = teamA_pool - teamB_pool

        # ============================
        # Lane Matchup Modeling
        # ============================

        lane_matchups = []

        for i in range(5):
            laneA = teamA[:, i, :]
            laneB = teamB[:, i, :]

            matchup_vec = self.matchup_fc(torch.cat([laneA, laneB], dim=-1))
            lane_matchups.append(matchup_vec)

        # Shape: (B, 5*D)
        lane_matchups = torch.cat(lane_matchups, dim=1)

        # ============================
        # Final Match Vector
        # ============================

        match_vec = torch.cat([
            teamA_pool,
            teamB_pool,
            team_diff,
            lane_matchups
        ], dim=1)

        # ============================
        # Output Probability
        # ============================

        logits = self.match_mlp(match_vec)
        # prob = torch.sigmoid(logits)

        return logits
