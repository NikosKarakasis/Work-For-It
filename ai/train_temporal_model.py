"""Optional PyTorch upgrade over train_classifier.py's hand-engineered features.

Only worth reaching for if the scikit-learn baseline in train_classifier.py
isn't accurate enough on the labeled eval set. Trains a small 1D-CNN directly
on the resampled raw angle sequence of each rep window, instead of hand-picked
min/max/mean features.

labels_csv format is the same as train_classifier.py (video, rep_index, valid).

Usage:
    python train_temporal_model.py --exercise push-up --angles_csv data/push_up_angles.csv --labels_csv data/push_up_rep_labels.csv
"""

import argparse

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, random_split

from baseline_state_machine import calibrate_thresholds, count_reps, smooth
from features import EXERCISE_CONFIGS

RESAMPLE_LEN = 32  # fixed number of timesteps every rep window is resampled to


def resample_to_length(values: np.ndarray, length: int) -> np.ndarray:
    x_old = np.linspace(0, 1, num=len(values))
    x_new = np.linspace(0, 1, num=length)
    return np.interp(x_new, x_old, values)


class RepWindowDataset(Dataset):
    def __init__(self, exercise: str, angles_csv: str, labels_csv: str):
        config = EXERCISE_CONFIGS[exercise]
        self.angle_names = list(config["angles"].keys())
        df = pd.read_csv(angles_csv)
        labels = pd.read_csv(labels_csv)

        self.samples = []  # list of (channels x RESAMPLE_LEN, label)
        for video_name, group in df.groupby("video"):
            group = group.sort_values("frame").reset_index(drop=True)
            smoothed_primary = smooth(group[config["primary_angle"]]).to_numpy()
            down, up = calibrate_thresholds(smoothed_primary)
            _, reps = count_reps(smoothed_primary, down, up)

            video_labels = labels[labels["video"] == video_name]
            for rep_index, (start, end) in enumerate(reps):
                label_row = video_labels[video_labels["rep_index"] == rep_index]
                if label_row.empty:
                    continue
                segment = group.iloc[start:end + 1]
                channels = [resample_to_length(segment[name].to_numpy(), RESAMPLE_LEN) for name in self.angle_names]
                self.samples.append((np.stack(channels).astype(np.float32), int(label_row.iloc[0]["valid"])))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        return torch.from_numpy(x), torch.tensor(y, dtype=torch.float32)


class RepValidityCNN(nn.Module):
    def __init__(self, num_channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(num_channels, 16, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Linear(32, 1)

    def forward(self, x):
        features = self.net(x).squeeze(-1)
        return self.head(features).squeeze(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--angles_csv", required=True)
    parser.add_argument("--labels_csv", required=True)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    dataset = RepWindowDataset(args.exercise, args.angles_csv, args.labels_csv)
    if len(dataset) < 10:
        raise SystemExit(f"Only {len(dataset)} labeled reps found — label more reps before training.")

    val_size = max(1, len(dataset) // 5)
    train_ds, val_ds = random_split(dataset, [len(dataset) - val_size, val_size])
    train_loader = DataLoader(train_ds, batch_size=8, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=8)

    model = RepValidityCNN(num_channels=len(dataset.angle_names))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.BCEWithLogitsLoss()

    for epoch in range(args.epochs):
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            optimizer.step()

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in val_loader:
            preds = (torch.sigmoid(model(x)) > 0.5).float()
            correct += (preds == y).sum().item()
            total += len(y)
    print(f"{args.exercise}: validation accuracy = {correct / total:.3f} ({total} held-out reps)")

    out_path = f"data/{args.exercise.replace('-', '_')}_cnn.pt"
    torch.save(model.state_dict(), out_path)
    print(f"Saved trained model to {out_path}")


if __name__ == "__main__":
    main()
