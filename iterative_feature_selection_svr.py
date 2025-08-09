"""
Recursive Feature Elimination (RFE) with SVR for feature selection and model optimization.

This script:
- Loads a CSV dataset,
- Iteratively applies RFE using SVR to select features,
- Trains Linear Regression models on selected features,
- Tracks model performance metrics (R², RMSE, MAE, Explained Variance),
- Stops when the minimum number of features is reached,
- Saves the best-performing model and its selected features to a user-defined directory.

User inputs:
- CSV file path,
- RFE step size (how many features to remove at each RFE sub-step),
- Number of features to remove each iteration,
- Minimum number of features to keep,
- Directory to save outputs,
- Whether to save the best model.

"""

import os
import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, explained_variance_score
from sklearn.feature_selection import RFE
from joblib import dump

def train_model(data):
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        'R²': r2_score(y_test, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
        'MAE': mean_absolute_error(y_test, y_pred),
        'Explained Variance': explained_variance_score(y_test, y_pred)
    }

    return model, metrics

def feature_selection(data, step, remove_count):
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    svr = SVR(kernel='linear')
    n_features = X.shape[1] - remove_count
    if n_features < 1:
        n_features = 1  # Ensure at least one feature remains

    rfe = RFE(estimator=svr, step=step, n_features_to_select=n_features)
    rfe.fit(X, y)

    selected_features = X.columns[rfe.support_]
    X_selected = X.loc[:, selected_features]

    final_data = X_selected.copy()
    final_data['target'] = y

    return final_data, selected_features

def optimize_model(file_path, step, remove_count, min_features, save_dir):
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        return

    data = pd.read_csv(file_path)
    models_metrics = []
    initial_features = data.shape[1] - 1

    print(f"Initial features count: {initial_features}")
    print("Training initial model...")
    initial_model, initial_metrics = train_model(data)
    models_metrics.append(("initial_model", initial_metrics, data))

    iteration = 1
    current_features = initial_features

    while True:
        print(f"\nFeature selection iteration {iteration}...")

        if current_features <= min_features:
            print(f"Reached minimum number of features ({min_features}). Stopping.")
            break

        data, selected_features = feature_selection(data, step, remove_count)
        current_features = len(selected_features)
        print(f"Selected features ({current_features}): {selected_features.tolist()}")

        print(f"Training model iteration {iteration}...")
        model, metrics = train_model(data)
        models_metrics.append((f"model_iteration_{iteration}", metrics, data))

        iteration += 1

    best_model = max(models_metrics, key=lambda x: x[1]['R²'])
    best_model_name, best_metrics, best_data = best_model

    print("\nBest model found:")
    print(f"Model name: {best_model_name}")
    print(f"Metrics: {best_metrics}")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    best_model_file = os.path.join(save_dir, f"best_model_{best_model_name}.joblib")
    best_features_file = os.path.join(save_dir, f"best_features_{best_model_name}.csv")

    final_model = LinearRegression().fit(best_data.iloc[:, :-1], best_data.iloc[:, -1])

    save_model = input("Do you want to save the best model? (yes/no): ").strip().lower()
    if save_model in ('yes', 'y'):
        dump(final_model, best_model_file)
        print(f"Best model saved to {best_model_file}")

    best_data.to_csv(best_features_file, index=False)
    print(f"Best features saved to {best_features_file}")

if __name__ == "__main__":
    file_path = input("Enter the CSV file path: ").strip()
    step = int(input("Enter RFE step (features to remove each RFE sub-step): ").strip())
    remove_count = int(input("Enter how many features to remove each iteration: ").strip())
    min_features = int(input("Enter the minimum number of features to keep: ").strip())
    save_dir = input("Enter directory path to save results: ").strip()

    optimize_model(file_path, step, remove_count, min_features, save_dir)
