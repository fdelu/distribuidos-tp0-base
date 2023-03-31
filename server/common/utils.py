import csv
import datetime
import json


""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574

SPLIT_CHAR = ","
ATTRS_ORDER = ["agency", "first_name", "last_name", "document", "birthdate", "number"]

""" A lottery bet registry. """
class Bet:
    def __init__(self, *args):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        for i, attr in enumerate(ATTRS_ORDER):
            value: str = str(args[i])
            setattr(self, attr, value.replace(SPLIT_CHAR, ""))

        self.agency = int(self.agency)
        self.birthdate = datetime.date.fromisoformat(self.birthdate)
        self.number = int(self.number)

    def from_string(data: str):
        return Bet(*data.split(SPLIT_CHAR))

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

