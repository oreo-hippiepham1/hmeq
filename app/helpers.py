import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

import os


def log_tf_feature_names(transformer, feature_names):
    return [f"{feature}_log" for feature in feature_names]


# --- Translating LIME explanation to human readable format ---
cat_features = ["REASON", "JOB"]
num_features_log_iter = ["LOAN", "VALUE", "MORTDUE", "YOJ", "CLAGE", "DEBTINC"]
num_features_mode = ["DELINQ", "DEROG", "NINQ", "CLNO"]


def _translate_numerical_condition(condition_str, col_transformer):
    """Helper to translate numerical conditions, now handling simple and range conditions."""
    try:
        # --- 1. Parse ---
        # Try simple condition first: feature op value (e.g., X <= 0.5)
        match_simple = re.match(
            r"([a-zA-Z0-9_]+)\s*([<>=!]+)\s*(-?\d+\.?\d*)", condition_str
        )
        # Try range condition: value < feature <= value (e.g., 0.1 < X <= 0.5)
        match_range = re.match(
            r"(-?\d+\.?\d*)\s*<[=]?\s*([a-zA-Z0-9_]+)\s*<[=]?\s*(-?\d+\.?\d*)",
            condition_str,
        )

        processed_feature_name = None
        operator = None
        threshold_transformed_single = None
        lower_bound_transformed = None
        upper_bound_transformed = None
        is_range = False

        if match_range:
            lower_bound_transformed = float(match_range.group(1))
            processed_feature_name = match_range.group(2)
            upper_bound_transformed = float(match_range.group(3))
            is_range = True

            op_lower_search = re.search(
                re.escape(str(lower_bound_transformed))
                + r"\s*(<[=]?)\s*"
                + re.escape(processed_feature_name),
                condition_str,
            )
            op_upper_search = re.search(
                re.escape(processed_feature_name)
                + r"\s*(<[=]?)\s*"
                + re.escape(str(upper_bound_transformed)),
                condition_str,
            )
            op_lower = op_lower_search.group(1) if op_lower_search else "<"
            op_upper = op_upper_search.group(1) if op_upper_search else "<="

        elif match_simple:
            processed_feature_name = match_simple.group(1)
            operator = match_simple.group(2)
            threshold_transformed_single = float(match_simple.group(3))
        else:
            return condition_str, False  # Cannot parse

        # --- 2. Identify & Get Components ---
        original_feature_name = None
        transformer_pipeline = None
        transformer_key = None
        feature_list_for_transformer = []
        uses_log = False

        if processed_feature_name.startswith("num_log_iter__"):
            transformer_key = "num_log_iter"
            original_feature_name = processed_feature_name.split("__")[1].replace(
                "_log", ""
            )
            feature_list_for_transformer = num_features_log_iter
            if "_log" in processed_feature_name:
                uses_log = True
        elif processed_feature_name.startswith("num_mode__"):
            transformer_key = "num_mode"
            original_feature_name = processed_feature_name.split("__")[1]
            feature_list_for_transformer = num_features_mode
            uses_log = False
        else:
            return condition_str, False

        transformer_pipeline = col_transformer.named_transformers_[transformer_key]
        scaler_instance = transformer_pipeline.named_steps["scaler"]
        feature_idx_in_scaler = feature_list_for_transformer.index(
            original_feature_name
        )
        n_scaler_features = scaler_instance.n_features_in_

        # --- Function to inverse transform a single value ---
        def inverse_transform_value(transformed_val):
            dummy_row = np.zeros((1, n_scaler_features))
            dummy_row[0, feature_idx_in_scaler] = transformed_val
            scaled_inverted_row = scaler_instance.inverse_transform(dummy_row)
            value_scaled_inverted = scaled_inverted_row[0, feature_idx_in_scaler]
            if uses_log:
                if value_scaled_inverted < 0 and np.isclose(value_scaled_inverted, 0):
                    return 0
                return np.expm1(value_scaled_inverted)
            return value_scaled_inverted

        # --- 3 & 4. Inverse Transform ---
        if is_range:
            original_lower_bound = inverse_transform_value(lower_bound_transformed)
            original_upper_bound = inverse_transform_value(upper_bound_transformed)
        else:
            original_threshold_single = inverse_transform_value(
                threshold_transformed_single
            )

        # --- 5. Format ---
        def format_threshold(value, feature_name):
            if feature_name == "DEBTINC":
                return f"{value:.2f}"
            return f"{value:.2f}"

        if is_range:
            formatted_lower = format_threshold(
                original_lower_bound, original_feature_name
            )
            formatted_upper = format_threshold(
                original_upper_bound, original_feature_name
            )
            translated_condition = f"{formatted_lower} {op_lower} {original_feature_name} {op_upper} {formatted_upper}"
        else:
            formatted_single = format_threshold(
                original_threshold_single, original_feature_name
            )
            translated_condition = (
                f"{original_feature_name} {operator} {formatted_single}"
            )

        return translated_condition, True

    except Exception as e:
        # print(f"Error translating numerical condition '{condition_str}': {e}")
        return condition_str, False


def _translate_categorical_condition(condition_str, col_transformer):
    try:
        # Pattern 1: feature=value or feature==value
        match_equality = re.match(
            r"([a-zA-Z0-9_]+)\s*([=]{1,2})\s*(-?\d+\.?\d*)", condition_str
        )

        # Pattern 2: feature > value, feature >= value, feature < value, feature <= value
        match_inequality = re.match(
            r"([a-zA-Z0-9_]+)\s*([<>]=?)\s*(-?\d+\.?\d*)", condition_str
        )

        # Pattern 3: value1 <[=] feature <[=] value2 (the range for OHE features like 0 < X <= 1)
        match_range = re.match(
            r"(-?\d+\.?\d*)\s*<[=]?\s*([a_zA-Z0-9_]+)\s*<[=]?\s*(-?\d+\.?\d*)",
            condition_str,
        )

        processed_feature_name = None
        is_condition_true = False  # Represents "feature IS category_value"
        is_condition_false = False  # Represents "feature IS NOT category_value"

        if match_equality:
            processed_feature_name = match_equality.group(1)
            # op = match_equality.group(2) # '=' or '=='
            val = float(match_equality.group(3))
            if not processed_feature_name.startswith("cat__"):
                return condition_str, False  # Not a cat feature
            if np.isclose(val, 1.0):
                is_condition_true = True
            elif np.isclose(val, 0.0):
                is_condition_false = True
            else:  # Equality to something other than 0 or 1 for OHE
                return condition_str, False

        elif match_inequality:  # Handles >, >=, <, <=
            processed_feature_name = match_inequality.group(1)
            op = match_inequality.group(2)
            val = float(match_inequality.group(3))
            if not processed_feature_name.startswith("cat__"):
                return condition_str, False

            if (op == ">" and val < 0.5) or (
                op == ">=" and val <= 0.0
            ):  # e.g., X > 0.0 or X >= 0.0 means X must be 1
                is_condition_true = True
            elif (op == "<" and val > 0.5) or (
                op == "<=" and val < 0.5
            ):  # e.g., X < 1.0 or X <= 0.0 means X must be 0
                is_condition_false = True
            # else: might be an ambiguous inequality like X > 0.6 for a 0/1 feature.

        elif match_range:
            lower_bound = float(match_range.group(1))
            processed_feature_name_range = match_range.group(2)
            upper_bound = float(match_range.group(3))
            if not processed_feature_name_range.startswith("cat__"):
                return condition_str, False
            processed_feature_name = processed_feature_name_range  # Assign it

            # This specifically handles "0.00 < X <= 1.00" or similar meaning X=1
            if (
                (np.isclose(lower_bound, 0.0) or lower_bound < 0.5)
                and (np.isclose(upper_bound, 1.0) or upper_bound > 0.5)
                and (lower_bound < upper_bound)
            ):  # Range effectively means the feature is 1
                is_condition_true = True

        if not processed_feature_name:  # No pattern matched or not a cat feature
            return condition_str, False

        # Final check if a definitive state was determined
        if not is_condition_true and not is_condition_false:
            # This means a pattern matched, but the logic above didn't set true/false
            # e.g., an ambiguous inequality like "cat_X > 0.6"
            return condition_str, False

        parts = processed_feature_name.split("__")
        if len(parts) != 2:
            return condition_str, False  # Should be cat__FEATURE_VALUE
        original_cat_feature, category_value = parts[1].split("_", 1)

        condition_meaning = ""
        if is_condition_true:
            condition_meaning = f"{original_cat_feature} is {category_value}"
        elif is_condition_false:
            condition_meaning = f"{original_cat_feature} is not {category_value}"
        else:  # Should not be reached if logic above is sound
            return condition_str, False

        return condition_meaning, True

    except Exception as e:
        # print(f"DEBUG CAT EXCEPTION on '{condition_str}': {e}")
        return condition_str, False


def translate_lime_explanation(raw_exp, fitted_pipeline):
    """
    Translates a raw LIME explanation list (tuples) into a more interpretable format
    using the fitted preprocessing pipeline.
    """
    translated_explanation = []
    try:
        outer_preprocessor_pipeline = fitted_pipeline.named_steps["preprocessor"]
        col_transformer = outer_preprocessor_pipeline.named_steps["preprocessor"]
        if not isinstance(col_transformer, ColumnTransformer):
            raise TypeError(
                "Expected ColumnTransformer not found at the expected location."
            )
    except (KeyError, TypeError, AttributeError) as e:
        raise ValueError(f"Could not find the ColumnTransformer. Error: {e}")

    for condition_str, weight in raw_exp:
        translated_condition, success_num = _translate_numerical_condition(
            condition_str, col_transformer
        )
        if success_num:
            translated_explanation.append((translated_condition, weight))
            continue
        translated_condition, success_cat = _translate_categorical_condition(
            condition_str, col_transformer
        )
        if success_cat:
            translated_explanation.append((translated_condition, weight))
            continue
        print(f"Warning: Could not translate condition: {condition_str}")
        translated_explanation.append((condition_str, weight))
    return translated_explanation


# SAMPLE USAGE:
# raw_explanation = explanation_lime.as_list()

# translated_output = translate_lime_explanation(raw_explanation, loaded_rf_pipeline)

# print("Translated LIME Explanation:")
# for condition, weight in translated_output:
#     print(f"  ('{condition}', {weight:.4f})") # Format weight for display
