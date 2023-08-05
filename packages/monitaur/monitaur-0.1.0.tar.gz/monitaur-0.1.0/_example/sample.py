from joblib import dump
from numpy import loadtxt

from monitaur import Monitaur
from monitaur.exceptions import ClientAuthError, ClientValidationError
from monitaur.utils import hash_file
from prediction import get_prediction
from xgboost_diabetes import train_model


# create instance of Monitaur client library
# monitaur = Monitaur(
#     auth_key="d4c72601c68d57e7aae8e8e9f11c3c44ddb92462",
#     base_url="https://api.monitaur.ai",
# )
monitaur = Monitaur(
    auth_key="f20d58f7e4289246bd1594449357ec9776b90a10",
    base_url="http://localhost:8008",
)

# train model
dataset = loadtxt("./_example/data.csv", delimiter=",")
seed = 7
test_size = 0.1
model_data = train_model(dataset, seed, test_size)
trained_model = model_data["trained_model"]
training_data = model_data["training_data"]
dump(trained_model, open(f"./_example/data.joblib", "wb"))

# add model to api
model_data = {
    "name": "Diabetes Classifier",
    "type": "Gradient Boosting",
    "model_type": "tabular",
    "library": "xgboost",
    "trained_model_hash": hash_file("./_example/data.joblib"),
    "production_file_hash": hash_file("./_example/prediction.py"),
    "feature_number": 8,
    "owner": "Anthony Habayeb",
    "developer": "Andrew Clark",
}
try:
    # model_id = monitaur.add_model(**model_data)
    model_id = 1
except ClientAuthError as e:
    print(e)
except ClientValidationError as e:
    print(e)
except Exception as e:
    print(e)

# get aws credentials
try:
    credentials = monitaur.get_credentials(model_id)
    # credentials = {
    #     "aws_access_key": "AKIAT25ZXQVMGE5IWQDA",
    #     "aws_secret_key": "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",
    #     "aws_region": "us-east-1",
    #     "aws_bucket_name": "monitaur-demo",
    # }
except ClientAuthError as e:
    print(e)
except ClientValidationError as e:
    print(e)
except Exception as e:
    print(e)

# record training
record_training_data = {
    "credentials": credentials,
    "model_id": model_id,
    "trained_model": trained_model,
    "training_data": training_data,
    "feature_names": [
        "Pregnancies",
        "Glucose",
        "BloodPressure",
        "SkinThickness",
        "Insulin",
        "BMI",
        "DiabetesPedigreeF",
        "Age",
    ],
    # "re_train": True
}
try:
    monitaur.record_training(**record_training_data)
    # pass
except ClientAuthError as e:
    print(e)
except ClientValidationError as e:
    print(e)
except Exception as e:
    print(e)

# record transaction
prediction = get_prediction([2, 84, 68, 27, 0, 26.7, 0.341, 32])
transaction_data = {
    "credentials": credentials,
    "model_id": model_id,
    "trained_model_hash": hash_file("./_example/data.joblib"),
    "production_file_hash": hash_file("./_example/prediction.py"),
    "prediction": prediction,
    "features": {
        "Pregnancies": 2,
        "Glucose": 84,
        "BloodPressure": 68,
        "SkinThickness": 27,
        "Insulin": 0,
        "BMI": 26.7,
        "DiabetesPedigreeF": 0.341,
        "Age": 32,
    },
}
try:
    response = monitaur.record_transaction(**transaction_data)
    print(response)
    # pass
except ClientAuthError as e:
    print(e)
except ClientValidationError as e:
    print(e)
except Exception as e:
    print(e)
