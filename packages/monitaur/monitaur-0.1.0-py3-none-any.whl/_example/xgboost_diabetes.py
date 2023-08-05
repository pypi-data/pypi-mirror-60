from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


def train_model(dataset, seed, test_size):

    X = dataset[:, 0:8]
    Y = dataset[:, 8]

    x_train, x_test, y_train, y_test = train_test_split(
        X, Y, test_size=test_size, random_state=seed
    )
    model = XGBClassifier()
    model.fit(x_train, y_train)

    return {"trained_model": model, "training_data": x_train}
