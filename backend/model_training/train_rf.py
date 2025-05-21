from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_random_forest(X, y, useBalanced):
  state = 42
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, random_state=state
  )
  random_forest = RandomForestClassifier(
      random_state=state,
      class_weight='balanced' if useBalanced == True else None
  )
  param_grid = { 
    'n_estimators': [100, 200, 500],
    'min_samples_leaf': [3,4,5,6],
    'max_depth' : [None,5,7,9]
  }
  optimal_params_finder = GridSearchCV(
      estimator=random_forest, 
      param_grid=param_grid, 
      cv=5,
      scoring= 'balanced_accuracy' if useBalanced == True else 'accuracy'
  )
  optimal_params_finder.fit(X_train, y_train)

  best_random_forest = RandomForestClassifier(
      random_state=state,
      class_weight='balanced' if useBalanced else None,
      n_estimators = optimal_params_finder.best_params_['n_estimators'],
      min_samples_leaf = optimal_params_finder.best_params_['min_samples_leaf'],
      max_depth = optimal_params_finder.best_params_['max_depth']
  )

  best_random_forest.fit(X_train, y_train)

  y_pred = best_random_forest.predict(X_test)
  accuracy = accuracy_score(y_test, y_pred)
  precision = precision_score(y_test, y_pred, average='macro')
  recall = recall_score(y_test, y_pred, average='macro')
  f1 = f1_score(y_test, y_pred, average='macro')
  best_random_forest.fit(X, y)

  return { 
    'model': best_random_forest, 
    'metrics': {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
  }