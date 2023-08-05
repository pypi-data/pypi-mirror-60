from joblib import load
from numpy import array


def get_prediction(data_array):
    diabetes_model = load("./_example/data.joblib")
    data = array([data_array])
    result = diabetes_model.predict(data)

    prediction = "You do not have diabetes"
    if result[0] == 1:
        prediction = "You have diabetes"

    return prediction
