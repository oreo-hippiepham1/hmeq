from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import uvicorn

from app.schemas import LoanApplicationRequest, AgentAdviceRequest
from app.pipeline_utils import log_tf_feature_names, translate_lime_explanation
from app.limestone import lime_explain_instance
from app.agent.lime_agent import create_graph, LimeGraphMessage

import os
import json
import joblib
from contextlib import asynccontextmanager


def log_tf_feature_names(transformer, feature_names):
    return [f"{feature}_log" for feature in feature_names]


# 1 --- BASIC SETUP
lime_graph_app = None  # Initialize lime_graph_app globally
PIPELINES = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when app starts, for initializing heavy resources
    # Initialize the LIME Agent Graph
    global lime_graph_app
    global PIPELINES
    print("INFO:     Compiling LIME Agent Graph...")  # Optional: for logging
    lime_graph_app = create_graph()
    print("INFO:     LIME Agent Graph compiled.")  # Optional: for logging
    # Load pipelines
    PATH_PIPELINES = "/home/oreo/hmeq/app/assets/pipes"
    PIPELINES = {
        "rf": joblib.load(os.path.join(PATH_PIPELINES, "full_pipeline_rf.joblib")),
        "knn": joblib.load(os.path.join(PATH_PIPELINES, "full_pipeline_knn.joblib")),
        "gb": joblib.load(os.path.join(PATH_PIPELINES, "full_pipeline_gb.joblib")),
        "dt": joblib.load(os.path.join(PATH_PIPELINES, "full_pipeline_dt.joblib")),
        # "svm": joblib.load(os.path.join(PATH_PIPELINES, "full_pipeline_svm.joblib")),
    }

    yield  # divider

    # Run when app shuts down, for releasing resources
    print("INFO:     Closing LIME Agent Graph...")  # Optional: for logging


# Main App
app = FastAPI(lifespan=lifespan)

# CORS Config
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Get feature names
PATH_ASSETS = "/home/oreo/hmeq/app/assets"
feature_names = json.load(
    open(os.path.join(PATH_ASSETS, "feature_original_names.json"), "r")
)


# Load X_test_processed for LIME explanations
PATH_DATA_PROCESSED = "/home/oreo/hmeq/app/assets/data/processed"
X_test_processed = pd.read_csv(os.path.join(PATH_DATA_PROCESSED, "X_test.csv"))


# 2 --- API


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/predict/{pipeline_name}")
async def predict(request: LoanApplicationRequest, pipeline_name: str):
    """
    Invoke the ML model(s) to predict the probability of default for a loan application using the specified pipeline.

    Args:
        request: LoanApplicationRequest
            The loan application data to predict on.
        pipeline_name: str
            The name of the pipeline to use for prediction (e.g., "rf", "knn", "gb", "dt").
    Returns:
        A dictionary containing the probability of default.
    """
    # Convert input to DataFrame (as pipeline expects)
    if pipeline_name not in PIPELINES:
        return {"error": f"Pipeline {pipeline_name} not found."}

    pipeline = PIPELINES[pipeline_name]
    data_unpacked: Dict[str, Any] = request.model_dump(exclude_unset=True)
    input_df = pd.DataFrame(data=[data_unpacked], columns=feature_names)

    # Predict probability (get probability of class 1 == Default)
    proba = pipeline.predict_proba(input_df)[0, 1]
    print(f"INFO:     Probability of default: {pipeline.predict_proba(input_df)}")
    return {"probability_of_default": proba}


# 3 --- LIME EXPLANATION ENDPOINT ---
# Explain an instance from X_test
@app.get("/explain/{pipeline_name}/{instance_index}")
async def explain_instance(pipeline_name: str, instance_index: int):
    """
    Explain a specific instance from the test set using LIME.

    Args:
        pipeline_name: str
            The name of the pipeline to use for explanation (e.g., "rf", "knn", "gb", "dt").
        instance_index: int
            The index of the instance in the test set to explain.
    Returns:
        A dictionary containing the LIME explanation for the specified instance.
        If the pipeline or instance index is invalid, an error message is returned.
    """
    if pipeline_name not in PIPELINES:
        return {"error": f"Pipeline {pipeline_name} not found."}

    pipeline = PIPELINES[pipeline_name]

    if instance_index < 0 or instance_index >= len(X_test_processed):
        return {
            "error": f"Instance index {instance_index} is out of bounds for X_test_processed (length {len(X_test_processed)})."
        }

    instance_to_explain = X_test_processed.iloc[[instance_index]].values[0]

    try:
        lime_explanation_raw = lime_explain_instance(
            pipeline=pipeline,
            instance=instance_to_explain,
        )
        translated_explanation = translate_lime_explanation(
            lime_explanation_raw.as_list(), pipeline
        )
        return {
            "pipeline_name": pipeline_name,
            "instance_index": instance_index,
            "lime_explanation": translated_explanation,
        }

    except Exception as e:
        return {"error": f"Error generating LIME explanation: {str(e)}"}


# Explain user-input instance
@app.post("/explain_custom_instance/{pipeline_name}")
async def explain_custom_instance(pipeline_name: str, request: LoanApplicationRequest):
    """
    Explain a custom instance using LIME. This is what is used for the actual app.

    Args:
        pipeline_name: str
            The name of the pipeline to use for explanation (e.g., "rf", "knn", "gb", "dt").
        request: LoanApplicationRequest
            The custom loan application data to explain.
    Returns:
        A dictionary containing the LIME explanation for the custom instance.
        If the pipeline is invalid or an error occurs, an error message is returned.
    """
    if pipeline_name not in PIPELINES:
        return {"error": f"Pipeline {pipeline_name} not found."}

    pipeline = PIPELINES[pipeline_name]

    # Convert input to DataFrame (as pipeline expects)
    data_unpacked: Dict[str, Any] = request.model_dump(exclude_unset=True)
    input_df = pd.DataFrame(data=[data_unpacked], columns=feature_names)

    try:
        # Preprocess the input instance using the pipeline's preprocessor
        if "preprocessor" not in pipeline.named_steps:
            return {"error": "Preprocessor step not found in the pipeline."}

        preprocessor = pipeline.named_steps["preprocessor"]
        processed_instance_df = preprocessor.transform(input_df)

        # Ensure the processed_instance is a 1D numpy array as expected by lime_explain_instance
        if isinstance(processed_instance_df, pd.DataFrame):
            instance_to_explain_np = processed_instance_df.values[0]
        elif isinstance(processed_instance_df, np.ndarray):
            # If it's already a numpy array, ensure it's 1D (e.g., if transform returns a 2D array with 1 row)
            instance_to_explain_np = processed_instance_df.flatten()
            if processed_instance_df.ndim > 1 and processed_instance_df.shape[0] == 1:
                instance_to_explain_np = processed_instance_df[0]
            else:  # Fallback or raise error if shape is unexpected
                instance_to_explain_np = processed_instance_df
        else:
            return {
                "error": "Processed instance is not in the expected format (DataFrame or ndarray)."
            }

        lime_explanation_raw = lime_explain_instance(
            pipeline=pipeline,  # Pass the full pipeline
            instance=instance_to_explain_np,
        )
        translated_explanation = translate_lime_explanation(
            lime_explanation_raw.as_list(),
            pipeline,  # Pass the full pipeline for translation context
        )
        return {
            "pipeline_name": pipeline_name,
            "input_data": data_unpacked,
            "lime_explanation": translated_explanation,
        }
    except AttributeError as e:
        # Catching cases where .values might be called on non-DataFrame, or named_steps issues
        return {
            "error": f"Error during preprocessing or LIME data preparation: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Error generating LIME explanation for custom instance: {str(e)}"
        }


# 4 --- AGENT ADVICE ENDPOINT ---
@app.post("/agent/advice")
async def get_agent_advice(request: AgentAdviceRequest):
    """
    Generate financial advice based on LIME and SHAP explanations using the LIME Agent Graph.
    Args:
        request: AgentAdviceRequest
            The request containing LIME explanations and default probability. Follows the schema defined in app/schemas.py.
    Returns:
        A dictionary containing the agent's interpretation and financial advice.
    """
    if lime_graph_app is None:
        # This should ideally not happen if startup event worked
        return {"error": "Agent graph not initialized. Please try again shortly."}

    try:
        graph_input = LimeGraphMessage(
            default_probability=request.default_probability,
            lime_explanations=request.lime_explanations,
            # agent_response_lime and agent_response_advice are outputs from the graph
        )

        # Invoke the LIME agent graph
        agent_result = await lime_graph_app.ainvoke(graph_input)

        return {
            "agent_interpretation": agent_result.get("agent_response_lime"),
            "financial_advice": agent_result.get("agent_response_advice"),
        }
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during agent advice generation: {str(e)}")
        return {"error": f"Error generating agent advice: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
