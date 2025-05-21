from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

def train_support_vector_machine(X, y, useBalanced):
  state = 42
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, random_state=state
  )
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)

  X_scaled = scaler.transform(X)
  svc = SVC(
      random_state=state,
      class_weight='balanced' if useBalanced else None
  )
  param_grid = { 
    'C': [0.5, 1, 10, 100],
    'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.0001],
    'kernel': ['linear', 'rbf', 'sigmoid']
  }
  optimal_params_finder = GridSearchCV(
      estimator=svc, 
      param_grid=param_grid, 
      cv=5,
      scoring= 'balanced_accuracy' if useBalanced else 'accuracy'
  )
  optimal_params_finder.fit(X_train_scaled, y_train)

  best_svc = SVC(
      random_state=state,
      class_weight='balanced' if useBalanced else None,
      C=optimal_params_finder.best_params_['C'],
      gamma=optimal_params_finder.best_params_['gamma'],
      kernel=optimal_params_finder.best_params_['kernel']
  )
  best_svc.fit(X_train_scaled, y_train)

  y_pred = best_svc.predict(X_test_scaled)
  accuracy = accuracy_score(y_test, y_pred)
  precision = precision_score(y_test, y_pred, average='macro')
  recall = recall_score(y_test, y_pred, average='macro')
  f1 = f1_score(y_test, y_pred, average='macro')
  best_svc.fit(X_scaled, y)

  return { 
    'model': best_svc, 
    'scaler': scaler,
    'metrics': {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
  }