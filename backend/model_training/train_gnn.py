import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv
from torch_geometric.data import Data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.neighbors import NearestNeighbors
from shapely import wkt
import numpy as np

from constants import CONFIG_COLUMN_TO_PREDICT, GENERATED_POINT_COLUMN

torch.manual_seed(42)

class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, weight=None):
        super().__init__()
        self.gamma = gamma
        self.weight = weight

    def forward(self, input, target):
        logp = F.log_softmax(input, dim=1)
        p = torch.exp(logp)
        loss = F.nll_loss(((1 - p) ** self.gamma) * logp, target, weight=self.weight)
        return loss

class GNNClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super().__init__()
        self.conv1 = GATv2Conv(input_dim, hidden_dim)
        self.conv2 = GATv2Conv(hidden_dim, hidden_dim)
        self.conv3 = GATv2Conv(hidden_dim, hidden_dim)
        self.conv4 = GATv2Conv(hidden_dim, num_classes)

    def forward(self, x, edge_index):
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.conv3(x, edge_index)
        x = F.relu(x)
        x = self.conv4(x, edge_index)
        return x

def train_graph_neural_network(config, survey_df, columns_to_train):
    X = survey_df[columns_to_train].fillna(0).values
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    X = torch.tensor(X, dtype=torch.float32)

    y = torch.tensor(survey_df[config[CONFIG_COLUMN_TO_PREDICT]].values, dtype=torch.long)

    train_idx, test_idx = train_test_split(
        np.arange(len(y)), test_size=0.2, stratify=y, random_state=42
    )

    survey_df['point_geom'] = survey_df[GENERATED_POINT_COLUMN].apply(wkt.loads)
    survey_coords = np.array([[pt.x, pt.y] for pt in survey_df['point_geom']])
    nbrs_survey = NearestNeighbors(n_neighbors=6).fit(survey_coords)
    _, indices_survey = nbrs_survey.kneighbors(survey_coords)
    edges_survey = [[i, j] for i, neighbors in enumerate(indices_survey) for j in neighbors if i != j]
    edge_index_survey = torch.tensor(edges_survey, dtype=torch.long).t().contiguous()

    model = GNNClassifier(input_dim=X.shape[1], hidden_dim=128, num_classes=len(np.unique(y)))
    weights = compute_class_weight(class_weight='balanced', classes=np.unique(y.numpy()), y=y.numpy())
    class_weights = torch.tensor(weights, dtype=torch.float32)
    loss_fn = FocalLoss(gamma=1.5, weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    data = Data(x=X, edge_index=edge_index_survey, y=y)
    train_mask = torch.zeros(len(y), dtype=torch.bool)
    test_mask = torch.zeros(len(y), dtype=torch.bool)
    train_mask[train_idx] = True
    test_mask[test_idx] = True

    for epoch in range(300):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = loss_fn(out[train_mask], data.y[train_mask])
        loss.backward()
        optimizer.step()
        if epoch % 50 == 0:
            print(f"Epoch {epoch+1} | Loss: {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        logits = model(data.x, data.edge_index)
        y_pred = torch.argmax(logits[test_mask], dim=1)
        y_true = data.y[test_mask]

    accuracy = accuracy_score(y_true.numpy(), y_pred.numpy())
    precision = precision_score(y_true.numpy(), y_pred.numpy(), average='macro')
    recall = recall_score(y_true.numpy(), y_pred.numpy(), average='macro')
    f1 = f1_score(y_true.numpy(), y_pred.numpy(), average='macro')

    return {
        'model': model,
        'scaler': scaler,
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    }
