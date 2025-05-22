from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_random_forest_regression(X, y):
    state = 42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=state
    )
    random_forest = RandomForestRegressor(
        random_state=state
    )
    param_grid = { 
        'n_estimators': [100, 200, 500],
        'min_samples_leaf': [3, 4, 5, 6],
        'max_depth' : [None, 5, 7, 9]
    }
    optimal_params_finder = GridSearchCV(
        estimator=random_forest, 
        param_grid=param_grid, 
        cv=5,
        scoring='neg_mean_squared_error'
    )
    optimal_params_finder.fit(X_train, y_train)

    best_params = optimal_params_finder.best_params_
    best_random_forest = RandomForestRegressor(
        random_state=state,
        n_estimators=best_params['n_estimators'],
        min_samples_leaf=best_params['min_samples_leaf'],
        max_depth=best_params['max_depth']
    )

    best_random_forest.fit(X_train, y_train)

    y_pred = best_random_forest.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    best_random_forest.fit(X, y)

    return { 
        'model': best_random_forest, 
        'metrics': {
            'mse': mse,
            'mae': mae,
            'r2': r2
        }
    }
