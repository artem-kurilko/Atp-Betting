# ATP Betting bot

## Strategy

We make prediction using features in generated atp_data.csv file using XGBoost. 
Model trained on all atp matches from 2000-2020 year from [website](http://tennis-data.co.uk/data.php).
Accuracy of this program is 76.614%.

**Data for prediction:**
- [elo ranking](http://tennisabstract.com/reports/atp_elo_ratings.html)
- [total amount of wins](https://www.atptour.com/en/content/ajax/player-match-record-page?matchRecordType=tour&playerId=")
- [ranks and coeffs of nearest matches](https://www.tennisexplorer.com)

## How to run 

###Set up libraries

Enter in command line:

> pip install -r requirements.txt

Then in automation.py in method **get_total_amount_of_wins(name: str)** specify path to chromedriver:
    
    driver = webdriver.Chrome('/path/to/chromedriver')

###Run program

Enter in command line:

> python main.py

## Statistics
	Amount of raw test values 30222
	Amount of test values 19811
	Amount of matched games 15178
	Average coefficient 1.6607478587429625
	Accuracy: 76.61400232194235 %