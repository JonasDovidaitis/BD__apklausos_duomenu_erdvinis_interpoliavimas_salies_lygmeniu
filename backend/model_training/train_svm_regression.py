from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

def train_support_vector_regression(X, y):
    state = 42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=state
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    X_scaled = scaler.transform(X)
    svr = SVR()
    param_grid = { 
        'C': [0.5, 1, 10, 100],
        'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.0001],
        'kernel': ['linear', 'rbf', 'sigmoid']
    }
    optimal_params_finder = GridSearchCV(
        estimator=svr, 
        param_grid=param_grid, 
        cv=5,
        scoring='neg_mean_squared_error'
    )
    optimal_params_finder.fit(X_train_scaled, y_train)

    best_svr = SVR(
        C=optimal_params_finder.best_params_['C'],
        gamma=optimal_params_finder.best_params_['gamma'],
        kernel=optimal_params_finder.best_params_['kernel']
    )
    best_svr.fit(X_train_scaled, y_train)

    y_pred = best_svr.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    best_svr.fit(X_scaled, y)

    return { 
        'model': best_svr, 
        'scaler': scaler,
        'metrics': {
            'mse': mse,
            'mae': mae,
            'r2': r2
        }
    }
