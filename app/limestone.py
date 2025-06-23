import lime
import lime.lime_tabular

import os
import joblib
import json
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline


PATH_DATA_PROCESSED = "/home/oreo/hmeq/app/assets/data/processed"
X_train_processed = pd.read_csv(os.path.join(PATH_DATA_PROCESSED, "X_train.csv"))

PATH_ASSETS = "/home/oreo/hmeq/app/assets"
feature_processed_names = json.load(
    open(os.path.join(PATH_ASSETS, "feature_preprocessed_names.json"), "r")
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

    explainer_lime = lime.lime_tabular.LimeTabularExplainer(
        training_data=X_train_processed.values,
        feature_names=feature_processed_names,
        class_names=["Paid", "Default"],
        mode="classification",
        categorical_features=[10, 11, 12, 13, 14, 15, 16],
    )

    # Get the explanation
    lime_explanation_instance = explainer_lime.explain_instance(
        data_row=instance,
        predict_fn=_predict_fn_lime,
        num_features=10,
        labels=(1,),
        num_samples=400,
    )
    return lime_explanation_instance
