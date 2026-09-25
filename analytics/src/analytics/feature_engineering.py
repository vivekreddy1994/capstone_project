from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd

def create_feature_engineering_pipeline(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    return preprocessor

def engineer_features(data):
    # Example feature engineering steps
    data['new_feature'] = data['existing_feature'] * 2  # Example transformation
    return data

def transform_data(data, preprocessor):
    # Apply feature engineering
    data = engineer_features(data)
    
    # Separate features and target
    X = data.drop('target', axis=1)
    y = data['target']
    
    # Fit and transform the features
    X_transformed = preprocessor.fit_transform(X)
    
    return X_transformed, y