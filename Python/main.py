"""
Atp prediction bot
"""

from sklearn.model_selection import train_test_split
from datetime import datetime
import logging as log
import pandas as pd
import xgboost

from Python import prediction
from Python import automation

__author__ = "Artemii Kurilko"

__version__ = "1.0.0"
__maintainer__ = "Artemii Kurilko"
__email__ = "kurilko365@gmail.com"
__status__ = "Development"

# logging config
log.basicConfig(filename='E:/startups/AtpPredictionBot/logs.txt', level=log.INFO)
cur_time = str(datetime.now())[0:16]

# Access our dataset
dataset_path = "E:/startups/AtpPredictionBot/Generated Data/atp_data_train.xlsx"
dataset = pd.read_excel(dataset_path, engine='openpyxl')

# XGBoost settings parameters
# Set x and y parameters. Y is a sequence of 1 and 0 (winner and loser) repeated on a dataset length / 2
X = dataset[["Wcoef", "Lcoef", "Wrank", "Lrank", "Wwins", "Lwins", "Welo", "Lelo"]]
Y = dataset["IsWinner"]

# Split train and test dataset
seed = 7
test_size = 0.33
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

# Create and train xgboost model
model = xgboost.XGBClassifier(learning_rate=0.017,
                              max_depth=5,
                              min_child_weight=1,
                              gamma=0)

# model.fit(X_train, y_train)

# Train model
model.fit(X, Y)

# Get upcoming matches
matches = automation.get_matches()
log.info('\n')
tournament_name = ''

# Predict each match and log the result
for match in matches:
    match_values = match.split(',')

    date = match_values[0].strip()
    winner = match_values[1].strip()
    loser = match_values[2].strip()
    wcoef = float(match_values[5].strip())
    lcoef = float(match_values[6].strip())
    tournament = match_values[11].strip()

    if tournament != tournament_name:
        tournament_name = tournament
        log.info(' Time: ' + cur_time + ' Tournament: ' + tournament.upper())
    else:
        tournament = None

    descr = date + " " + winner + " " + loser + " " + str(wcoef) + " " + str(lcoef) + " "

    try:
        series = {
            'Wcoef': wcoef,
            'Lcoef': lcoef,
            'Wrank': int(match_values[3].strip()),
            'Lrank': int(match_values[4].strip()),
            'Wwins': int(match_values[9].strip()),
            'Lwins': int(match_values[10].strip()),
            'Welo': float(match_values[7]),
            'Lelo': float(match_values[8])
        }
        prediction.predict_match(model, series, descr)
    except IndexError:
        pass

# Evaluate overall prediction accuracy
# accuracy = accuracy_score(y_test, predictions)
# print("Accuracy: %.2f%%" % (accuracy * 100.0))
