import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import lime
import lime.lime_tabular

import os
import joblib
import json

from app.pipeline_utils import log_tf_feature_names  # <--- IMPORT HERE

# --- Get X_train ready for LIME ---
PATH_DATA_PROCESSED = "/home/oreo/hmeq/app/assets/data/processed"
X_train_processed = pd.read_csv(os.path.join(PATH_DATA_PROCESSED, "X_train.csv"))

# --- Setting up LIME ---
PATH_ASSETS = "/home/oreo/hmeq/app/assets"
feature_processed_names = json.load(
    open(os.path.join(PATH_ASSETS, "feature_preprocessed_names.json"), "r")
)


explainer_lime = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train_processed.values,
    feature_names=feature_processed_names,
    class_names=["Paid", "Default"],
    mode="classification",
    categorical_features=[10, 11, 12, 13, 14, 15, 16],
)


def lime_explain_instance(
    pipeline: Pipeline, instance: np.ndarray
) -> lime.lime_tabular.LimeTabularExplainer:
    """
    Explain a single instance using LIME

    Args:
        instance: np.ndarray
            The instance to explain. It should be an array of values, with the same features as the training data.
    Returns:
        lime_explanation: lime.lime_tabular.LimeTabularExplainer
            The LIME explanation for the instance.
    """

    def _predict_fn_lime(data_for_prediction):
        return pipeline.named_steps["model"].predict_proba(data_for_prediction)

    # Get the explanation
    lime_explanation = explainer_lime.explain_instance(
        data_row=instance,
        predict_fn=_predict_fn_lime,
        num_features=10,
    )
    return lime_explanation


# --- PIPELINEs
# 1 --- extract features
cat_features = ['REASON', 'JOB']
num_features_log_iter = ['LOAN', 'VALUE', 'MORTDUE', 'YOJ', 'CLAGE', 'DEBTINC'] # log transform -> iterative impute -> scale
num_features_mode = ['DELINQ', 'DEROG', 'NINQ', 'CLNO'] # mode impute


# 2 --- IMPUTER
# ----- impute ['REASON', 'JOB'] with "Other"
cat_imputer = SimpleImputer(strategy='constant', fill_value='Other')
# ----- impute with mode() value
num_imputer_mode = SimpleImputer(strategy='most_frequent') # mode imputation
# ----- impute numerical cols with IterativeImputer (or EM Impute later)
num_imputer_iter = IterativeImputer(random_state=13, max_iter=10)


# 3 --- ENCODER, SCALER
# ----- OneHot encoding for categorical
categories_to_drop = ['Other'] * len(cat_features)
oh_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore', drop=categories_to_drop)
# ----- Log transform for right-skewed

log_transformer = FunctionTransformer(np.log1p, validate=True, feature_names_out=log_tf_feature_names)
# ----- Scaling for numerical features
num_scaler = StandardScaler()


# 4 --- PIPELINE
# ----- pipeline for each type of features
categorical_transformer = Pipeline(
    steps=[
        ('imputer', cat_imputer),
        ('onehot', oh_encoder)
    ]
)

numerical_log_iterative_transformer = Pipeline(steps=[
    ('imputer', num_imputer_iter),
    ('logtransform', log_transformer), # Apply log transform AFTER imputation
    ('scaler', num_scaler) # then scaling
])

numerical_mode_transformer = Pipeline(steps=[
    ('imputer', num_imputer_mode),
    ('scaler', num_scaler) # Scale mode-imputed features for consistency
])

# --- COLUMN TRANSFORMER
# ----- Column Transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num_log_iter', numerical_log_iterative_transformer, num_features_log_iter),
        ('num_mode', numerical_mode_transformer, num_features_mode),
        ('cat', categorical_transformer, cat_features)
    ],
    remainder='passthrough'
)

# ----- Overall pipeline
preprocessing_pipeline = Pipeline(
    steps=[
        ('preprocessor', preprocessor)
    ]
)
preprocessing_pipeline.set_output(transform="pandas")

if __name__ == "__main__":
    """
    This script is used to fit the pipelines and dump them to the assets folder.
    ONLY RUN THIS ONCE TO FIT THE PIPELINES.
    """
    DATA_PATH_CLEANED = "/home/oreo/hmeq/app/assets/data/cleaned"
    X_train = pd.read_csv(os.path.join(DATA_PATH_CLEANED, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(DATA_PATH_CLEANED, "X_test.csv"))

    X_train_processed = preprocessing_pipeline.fit_transform(X_train)

    DATA_PATH_RESAMPLED = "/home/oreo/hmeq/app/assets/data/processed"
    X_train_resampled = pd.read_csv(os.path.join(DATA_PATH_RESAMPLED, "X_train.csv"))
    y_train_resampled = pd.read_csv(os.path.join(DATA_PATH_RESAMPLED, "y_train.csv"))


    # ----- DecisionTree
    print("Fitting DecisionTree")
    dt = DecisionTreeClassifier(class_weight='balanced', random_state=13,
                                criterion='gini', max_depth=10, max_features='sqrt',
                                min_samples_split=30, min_samples_leaf=10)
    dt.fit(X_train_resampled, y_train_resampled.values.ravel())

    # ----- RandomForest
    print("Fitting RandomForest")
    rf = RandomForestClassifier(random_state=13, class_weight='balanced',
                                criterion='entropy', max_features='sqrt',
                                max_samples=None, n_estimators=200)
    rf.fit(X_train_resampled, y_train_resampled.values.ravel())

    # ----- GradientBoosting
    print("Fitting GradientBoosting")
    gb = GradientBoostingClassifier(random_state=13, n_estimators=600,
                                    max_depth=6, subsample=0.3, learning_rate=0.1)
    gb.fit(X_train_resampled, y_train_resampled.values.ravel())

    # ----- KNN
    print("Fitting KNN")
    knn = KNeighborsClassifier(n_neighbors=1, p=1, algorithm='ball_tree', weights='uniform')
    knn.fit(X_train_resampled, y_train_resampled.values.ravel())


    pipeline_rf = Pipeline(steps=[
        ('preprocessor', preprocessing_pipeline),
        ('model', rf)
    ])

    pipeline_knn = Pipeline(steps=[
        ('preprocessor', preprocessing_pipeline),
        ('model', knn)
    ])

    pipeline_gb = Pipeline(steps=[
        ('preprocessor', preprocessing_pipeline),
        ('model', gb)
    ])

    pipeline_dt = Pipeline(steps=[
        ('preprocessor', preprocessing_pipeline),
        ('model', dt)
    ])

    # Dump the pipelines
    PATH_PIPELINES = "/home/oreo/hmeq/app/assets/pipes"
    print(f"Dumping pipelines to {PATH_PIPELINES}")

    joblib.dump(pipeline_rf, os.path.join(PATH_PIPELINES, "full_pipeline_rf.joblib"))
    joblib.dump(pipeline_knn, os.path.join(PATH_PIPELINES, "full_pipeline_knn.joblib"))
    joblib.dump(pipeline_gb, os.path.join(PATH_PIPELINES, "full_pipeline_gb.joblib"))
    joblib.dump(pipeline_dt, os.path.join(PATH_PIPELINES, "full_pipeline_dt.joblib"))

    print("Pipelines dumped")

    PIPELINES = {
        "rf": pipeline_rf,
        "knn": pipeline_knn,
        "gb": pipeline_gb,
        "dt": pipeline_dt,
    }
