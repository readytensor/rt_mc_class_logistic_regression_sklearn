import os
import warnings
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import NotFittedError

warnings.filterwarnings("ignore")


PREDICTOR_FILE_NAME = "predictor.joblib"


class Classifier:
    """A wrapper class for the Logistic Regression classifier.

    This class provides a consistent interface that can be used with other
    classifier models.
    """

    model_name = "Logistic Regression Classifier"

    def __init__(
        self,
        penalty: Optional[str] = "elasticnet",
        C: Optional[float] = 0.5,
        l1_ratio: Optional[float] = 0.5,
        **kwargs,
    ):
        """Construct a new Logistic Regression classifier.

        Args:
            penalty (int, optional): The norm of the penalty - one of l1, l2,
                elasticnet, or none.
                Options: ["l1", "l2", "elasticnet", "none"]
                Defaults to "elasticnet".
            C (int, optional): Inverse of regularization strength; must be a
                positive float. Like in support vector machines, smaller values
                specify stronger regularization.
                Defaults to 0.5.
            l1_ratio (int, optional): The Elastic-Net mixing parameter, with
                0 <= l1_ratio <= 1.
                Only used if penalty='elasticnet'.
                Defaults to 0.5.
        """
        self.penalty = penalty
        self.C = float(C)
        self.l1_ratio = float(l1_ratio)
        self.model = self.build_model()
        self._is_trained = False

    def build_model(self) -> LogisticRegression:
        """Build a new classifier."""
        model = LogisticRegression(
            penalty = self.penalty,
            C = self.C,
            l1_ratio=self.l1_ratio,
            solver='saga',
        )
        return model

    def fit(self, train_inputs: pd.DataFrame, train_targets: pd.Series) -> None:
        """Fit the classifier to the training data.

        Args:
            train_inputs (pandas.DataFrame): The features of the training data.
            train_targets (pandas.Series): The labels of the training data.
        """
        self.model.fit(train_inputs, train_targets)
        self._is_trained = True

    def predict(self, inputs: pd.DataFrame) -> np.ndarray:
        """Predict class labels for the given data.

        Args:
            inputs (pandas.DataFrame): The input data.
        Returns:
            numpy.ndarray: The predicted class labels.
        """
        return self.model.predict(inputs)

    def predict_proba(self, inputs: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities for the given data.

        Args:
            inputs (pandas.DataFrame): The input data.
        Returns:
            numpy.ndarray: The predicted class probabilities.
        """
        return self.model.predict_proba(inputs)

    def evaluate(self, test_inputs: pd.DataFrame, test_targets: pd.Series) -> float:
        """Evaluate the classifier and return the accuracy.

        Args:
            test_inputs (pandas.DataFrame): The features of the test data.
            test_targets (pandas.Series): The labels of the test data.
        Returns:
            float: The accuracy of the classifier.
        """
        if self.model is not None:
            return self.model.score(test_inputs, test_targets)
        raise NotFittedError("Model is not fitted yet.")

    def save(self, model_dir_path: str) -> None:
        """Save the classifier to disk.

        Args:
            model_dir_path (str): Dir path to which to save the model.
        """
        if not self._is_trained:
            raise NotFittedError("Model is not fitted yet.")
        joblib.dump(self, os.path.join(model_dir_path, PREDICTOR_FILE_NAME))

    @classmethod
    def load(cls, model_dir_path: str) -> "Classifier":
        """Load the classifier from disk.

        Args:
            model_dir_path (str): Dir path to the saved model.
        Returns:
            Classifier: A new instance of the loaded classifier.
        """
        model = joblib.load(os.path.join(model_dir_path, PREDICTOR_FILE_NAME))
        return model

    def __str__(self):
        return (
            f"Model name: {self.model_name} ("
            f"C: {self.C}, "
            f"l1_ratio: {self.l1_ratio}, "
            f"penalty: {self.penalty})"
        )


def train_predictor_model(
    train_inputs: pd.DataFrame, train_targets: pd.Series, hyperparameters: dict
) -> Classifier:
    """
    Instantiate and train the predictor model.

    Args:
        train_X (pd.DataFrame): The training data inputs.
        train_y (pd.Series): The training data labels.
        hyperparameters (dict): Hyperparameters for the classifier.

    Returns:
        'Classifier': The classifier model
    """
    classifier = Classifier(**hyperparameters)
    classifier.fit(train_inputs=train_inputs, train_targets=train_targets)
    return classifier


def predict_with_model(
    classifier: Classifier, data: pd.DataFrame, return_probs=False
) -> np.ndarray:
    """
    Predict class probabilities for the given data.

    Args:
        classifier (Classifier): The classifier model.
        data (pd.DataFrame): The input data.
        return_probs (bool): Whether to return class probabilities or labels.
            Defaults to True.

    Returns:
        np.ndarray: The predicted classes or class probabilities.
    """
    if return_probs:
        return classifier.predict_proba(data)
    return classifier.predict(data)


def save_predictor_model(model: Classifier, predictor_dir_path: str) -> None:
    """
    Save the classifier model to disk.

    Args:
        model (Classifier): The classifier model to save.
        predictor_dir_path (str): Dir path to which to save the model.
    """
    if not os.path.exists(predictor_dir_path):
        os.makedirs(predictor_dir_path)
    model.save(predictor_dir_path)


def load_predictor_model(predictor_dir_path: str) -> Classifier:
    """
    Load the classifier model from disk.

    Args:
        predictor_dir_path (str): Dir path where model is saved.

    Returns:
        Classifier: A new instance of the loaded classifier model.
    """
    return Classifier.load(predictor_dir_path)


def evaluate_predictor_model(
    model: Classifier, x_test: pd.DataFrame, y_test: pd.Series
) -> float:
    """
    Evaluate the classifier model and return the accuracy.

    Args:
        model (Classifier): The classifier model.
        x_test (pd.DataFrame): The features of the test data.
        y_test (pd.Series): The labels of the test data.

    Returns:
        float: The accuracy of the classifier model.
    """
    return model.evaluate(x_test, y_test)
