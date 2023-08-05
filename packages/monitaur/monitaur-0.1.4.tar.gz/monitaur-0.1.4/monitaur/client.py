import json

import boto3
import dill
import requests
from alibi.explainers import AnchorTabular
from joblib import dump

from monitaur.exceptions import ClientAuthError, ClientValidationError
from monitaur.utils import explain_transaction

base_url = "https://api.monitaur.ai"


class Monitaur:
    def __init__(self, auth_key, base_url=base_url):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "monitaur-client-library",
                "Authorization": f"Token {auth_key}",
            }
        )
        self.base_url = base_url
        self.transaction_url = f"{self.base_url}/api/transactions/"
        self.models_url = f"{self.base_url}/api/models/"
        self.credentials_url = f"{self.base_url}/api/credentials/"

    def add_model(
        self,
        name: str,
        type: str,
        model_type: str,
        library: str,
        trained_model_hash: str,
        production_file_hash: str,
        feature_number: int,
        owner: str,
        developer: str,
        version: float = 0.1,
    ) -> int:
        """
        Adds metadata about the machine learning model to the system.

        Args:
            name: Unique name for what this model is predicting.
            type: Type of model (random forest, gradient boosting).
            model_type: This field can contain one of these values: tabular, image, nlp.
            library: Machine learning library (scikit-learn, xgboost) used.
            trained_model_hash: Trained model file hash. Must be a joblib.
            production_file_hash:
              Production file that uses the trained model for prediction.
              This should also have the logic that converts the prediction into something humanreadable.
              Example:
              ```
              def get_prediction(data_array):
                  diabetes_model = load("./_example/data.joblib")
                  data = array([data_array])
                  result = diabetes_model.predict(data)

                  prediction = "You do not have diabetes"
                  if result[0] == 1:
                      prediction = "You have diabetes"

                  return prediction
              ```
            feature_number: Number of inputs.
            owner: Name of the model owner.
            developer: Name of the data scientist.
            image: Is it an image model? Defaults to False.
            version: Monitaur model version. Defaults to 0.1.

        Returns:
            model_id: A new unique id for the monitaur model.
        """
        json = {
            "name": name,
            "type": type,
            "model_type": model_type,
            "library": library,
            "trained_model_hash": trained_model_hash,
            "production_file_hash": production_file_hash,
            "feature_number": feature_number,
            "owner": owner,
            "developer": developer,
            "version": version,
        }
        response = self._session.post(self.models_url, json=json)

        if response.status_code == requests.status_codes.codes.unauthorized:
            raise ClientAuthError("Invalid token", response.json())

        if response.status_code == requests.status_codes.codes.bad_request:
            raise ClientValidationError("Bad Request", response.json())

        return response.json().get("id")

    def get_credentials(self, model_id: int) -> dict:
        """
        Retrieves AWS credentials.

        Args:
            model_id: Unique id for the monitaur model received from the API.

        Returns:
            credentials:
                {
                    "aws_access_key": "123",
                    "aws_secret_key": "456",
                    "aws_region": "us-east-1",
                    "aws_bucket_name": "bucket name"
                }
        """
        response = self._session.get(f"{self.credentials_url}{model_id}/")

        if response.status_code == requests.status_codes.codes.unauthorized:
            raise ClientAuthError("Invalid token", response.json())

        if response.status_code == requests.status_codes.codes.bad_request:
            raise ClientValidationError("Bad Request", response.json())

        return response.json().get("credentials")

    def record_training(
        self,
        credentials: dict,
        model_id: int,
        trained_model,  # instantiated model
        training_data,  # NumPy array
        feature_names: list,
        re_train: bool = False,
    ):
        """
        Sends trained model and anchors data to S3.
        Currently works only for traditional, tabular machine learning models.

        Args:
            credentials: S3 credentials received from the API
                {
                    "aws_access_key": "123",
                    "aws_secret_key": "456",
                    "aws_region": "us-east-1",
                    "aws_bucket_name": "bucket name"
                }
            model_id: Unique id for the monitaur model received from the API.
            trained_model: Instantiated model (scikit-learn, xgboost).
            training_data: Training data (x training).
            feature_names: Model inputs.
            re_train: Model version will be increased by 0.1 when it is True.

        Returns:
            True
        """
        response = self._session.get(f"{self.models_url}{model_id}/")
        version = response.json()["version"]

        if re_train:
            version = self._increase_model_version(version)

        predict_fn = lambda x: trained_model.predict_proba(x)  # NOQA
        explainer = AnchorTabular(predict_fn, feature_names)
        explainer.fit(training_data)

        filename = f"{model_id}.joblib"
        filename_anchors = f"{model_id}.anchors"
        with open(filename, "wb") as f:
            dump(trained_model, f)
        with open(filename_anchors, "wb") as f:
            dill.dump(explainer, f)

        # connect to s3 and upload trained model and anchor files
        client = boto3.client(
            "s3",
            aws_access_key_id=credentials["aws_access_key"],
            aws_secret_access_key=credentials["aws_secret_key"],
            region_name=credentials["aws_region"],
        )
        with open(filename, "rb") as f:
            client.upload_fileobj(
                f, credentials["aws_bucket_name"], f"{model_id}/{version}/{filename}"
            )
        with open(filename_anchors, "rb") as f:
            client.upload_fileobj(
                f,
                credentials["aws_bucket_name"],
                f"{model_id}/{version}/{filename_anchors}",
            )

        print(f"Training recording: model id {model_id}, version {version}")
        return True

    def _increase_model_version(self, version):
        if isinstance(version, str):
            version = float(version)

        return version + 0.1

    def record_transaction(
        self,
        credentials: dict,
        model_id: int,
        trained_model_hash: str,
        production_file_hash: str,
        prediction: str,
        features: dict,
    ) -> dict:
        """
        Downloads trained model and respective explainers from s3.
        Calculates explanation for a given transaction.
        Sends transaction details to the server.

        Args:
            credentials: S3 credentials received from the API
                {
                    "aws_access_key": "123",
                    "aws_secret_key": "456",
                    "aws_region": "us-east-1",
                    "aws_bucket_name": "bucket name"
                }
            model_id: Unique id for the monitaur model received from the API.
            trained_model_hash: Trained model file hash. Must be a joblib.
            production_file_hash:
              Production file that uses the trained model for prediction.
              This should also have the logic that converts the prediction into something humanreadable.
              Example:
              ```
              def get_prediction(data_array):
                  diabetes_model = load("./_example/data.joblib")
                  data = array([data_array])
                  result = diabetes_model.predict(data)

                  prediction = "You do not have diabetes"
                  if result[0] == 1:
                      prediction = "You have diabetes"

                  return prediction
              ```
            prediction: Outcome from the production prediction file.
            features: key/value pairs of the feature names and values.

        Returns:
            Transaction details from the server
        """
        response = self._session.get(f"{self.models_url}{model_id}/")

        if response.status_code == requests.status_codes.codes.unauthorized:
            raise ClientAuthError("Invalid token", response.json())

        if response.status_code == requests.status_codes.codes.bad_request:
            raise ClientValidationError("Bad Request", response.json())

        version = response.json()["version"]

        interpretability = explain_transaction(
            model_id, version, features, credentials,
        )

        response = self._session.post(
            self.transaction_url,
            json={
                "model": model_id,
                "trained_model_hash": trained_model_hash,
                "production_file_hash": production_file_hash,
                "prediction": prediction,
                "features": features,
                "interpretability": json.dumps(interpretability),
            },
        )

        if response.status_code == requests.status_codes.codes.bad_request:
            raise ClientValidationError("Bad Request", response.json())

        return response.json()
