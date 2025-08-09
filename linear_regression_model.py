"""
This script loads a CSV dataset where the the dependent variable is in the last column, trains a Linear Regression model,
evaluates it using multiple metrics (R², Adjusted R², Explained Variance,
RMSE, MAE, MSE), and optionally saves the trained model as a .joblib file.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    explained_variance_score,
    mean_squared_error,
    mean_absolute_error
)
from joblib import dump

# Prompt for file path
file_path = input("File Directory: ").strip()

# Check if the file exists
if not os.path.exists(file_path):
    print(f"The file at '{file_path}' was not found. Please check the path and try again.")
    exit()

# Load dataset (assuming CSV format)
data = pd.read_csv(file_path)

# Split features (X) and target variable (y)
X = data.iloc[:, :-1]  # All columns except the last
y = data.iloc[:, -1]   # Last column as target

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train Linear Regression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Predict test set results
y_pred = lr_model.predict(X_test)

# R² Score
r2 = r2_score(y_test, y_pred)
print(f"R² Score: {r2}")

# Adjusted R² Score
n = len(y_test)  # Number of observations
k = X_test.shape[1]  # Number of features
adjusted_r2 = 1 - (((1 - r2) * (n - 1)) / (n - k - 1))
print(f"Adjusted R² Score: {adjusted_r2}")

# Explained Variance Score
explained_variance = explained_variance_score(y_test, y_pred)
print(f"Explained Variance Score: {explained_variance}")

# RMSE
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Root Mean Squared Error (RMSE): {rmse}")

# MAE
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error (MAE): {mae}")

# MSE
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Ask user if they want to save the model
while True:
    save_model = input("Do you want to save the model? (yes/no): ").strip().lower()

    if save_model in ("yes", "y"):
        model_name = input("Model name (with the extension .joblib): ").strip()
        save_directory = input("Save directory: ").strip()

        if not os.path.exists(save_directory):
            print(f"The directory '{save_directory}' does not exist. Creating directory...")
            os.makedirs(save_directory)

        full_path = os.path.join(save_directory, model_name)
        dump(lr_model, full_path)
        print(f"Model saved as '{model_name}' in '{save_directory}'")
        break

    elif save_model in ("no", "n"):
        print("End of analysis.")
        break

    else:
        print("Invalid answer, please enter 'yes' or 'no'.")
