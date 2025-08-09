"""
This script loads a CSV dataset, applies Recursive Feature Elimination (RFE)
using a Linear Regression model to select the best features, 
and saves the resulting dataset with only the selected features and target variable.
"""

import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

# Prompt for file path
file_path = input("Enter the CSV file path: ").strip()

# Load dataset
data = pd.read_csv(file_path)

# Split features (X) and target variable (y)
X = data.iloc[:, :-1]  # All columns except the last
y = data.iloc[:, -1]   # Last column as target

# Create the regression model
model = LinearRegression()

# Create RFE object and select top 32 features
rfe = RFE(estimator=model, n_features_to_select=32, step=1)

# Fit RFE on the dataset
rfe = rfe.fit(X, y)

# Get selected feature names
selected_features = X.columns[rfe.support_]
print("Selected features:", list(selected_features))

# Create a new DataFrame with selected features
X_selected = X.loc[:, selected_features]

# Add target variable
final_data = X_selected.copy()
final_data['target'] = y

# Prompt for save path
save_path = input("Enter the path to save the new CSV file: ").strip()
final_data.to_csv(save_path, index=False)

print(f"File saved successfully at: {save_path}")
