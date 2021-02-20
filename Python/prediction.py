"""
This file is used to improve program's overall accuracy
"""
import logging as log
import pandas as pd
from datetime import datetime

# logging config
log.basicConfig(filename='E:/startups/AtpPredictionBot/logs.txt', level=log.INFO)
cur_time = str(datetime.now())[0:16]


def predict_match(model, series, description: str):
    """
    Match prediction method.

    @param model: XGboost model
    @type model: XGboost classifier
    @param series: dictionary of match parameters
    @type series: Dict[str, Any]
    @param description match desc (ex. date player - player)
    @type description string
    """

    index = 1
    vector = pd.DataFrame(series, index=[index])
    feat_names = model.get_booster().feature_names
    res = model.predict_proba(vector[feat_names].iloc[[-1]])
    y_pred = res[0]

    if y_pred[0] >= 0.6:
        output = ' Time: ' + cur_time + ' Match date: ' + description + " Prediction: loser. Conf: " + str(y_pred[0])
        print(output)
        log.info(output)
    elif y_pred[1] >= 0.6:
        output = ' Time: ' + cur_time + ' Match date: ' + description + " Prediction: winner. Conf: " + str(y_pred[1])
        print(output)
        log.info(output)


def test_confidence_prediction(model, X_test: pd.DataFrame, y_test: pd.Series):
    """
    Test predictions only on outcome where our prediction confidence is >= 6.0

    @param model: XGboost model
    @type model: XGboost classifier
    @param X_test : test x data to predict
    @type X_test: DataFrame
    @param y_test: test y data
    @type y_test: Series
    @rtype: string
    @returns: string of regularized prediction accuracy in percentages
    """

    y_test_values = []
    y_test_pred = []

    for index, row in X_test.iterrows():
        l_coef = row["Lcoef"]
        w_coef = row['Wcoef']

        series = {
            'Wcoef': w_coef,
            'Lcoef': l_coef,
            'Wrank': row['Wrank'],
            'Lrank': row['Lrank'],
            'Wwins': row['Wwins'],
            'Lwins': row['Lwins'],
            'Welo': row['Welo'],
            'Lelo': row['Lelo']
        }

        # predict each test match
        vector = pd.DataFrame(series, index=[index])
        feat_names = model.get_booster().feature_names
        res = model.predict_proba(vector[feat_names].iloc[[-1]])
        # res[0][0] - loser
        # res[0][1] - winner
        y_pred = res[0]

        # if xgboost predicted player with probability >= 0.6
        # then add actual and predicted outcome to our test dataset
        if y_pred[0] >= 0.6:
            y_test_values.append(y_test[index])
            y_test_pred.append(0)
        elif y_pred[1] >= 0.6:
            y_test_values.append(y_test[index])
            y_test_pred.append(1)

    amount_of_matched_games = 0

    for value in range(0, len(y_test_values)):
        if y_test_values[value] == y_test_pred[value]:
            amount_of_matched_games += 1

    accuracy = amount_of_matched_games * 100 / len(y_test_values)
    return str(accuracy) + ' %'
