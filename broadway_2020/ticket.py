import pandas as pd

class Ticket:
    def __init__(
            self,
            weekday
    ):
        self.weekday = weekday
        self.slots_filled = 0
        self.artist_map = {}
        self.theatre_map = {}
        self.number = 0

    def all_artists(self):
        return set(self.artist_map.values())

    def all_theatres(self):
        return set(self.theatre_map.values())

    def export_ticket(self):
        df = pd.DataFrame(columns=['slot', 'theatre', 'artist'], data=[[1, None, None],
                          [2, None, None], [3, None, None], [4, None, None]])
        df['theatre'] = df['slot'].apply(lambda slot: self.theatre_map[slot])
        df['artist'] = df['slot'].apply(lambda slot: self.artist_map[slot])
        if df.isnull().sum().sum() > 0:
            raise Exception('The ticket has unassigned slots')

class Slot:
    def __init__(self, weekday, order):
        self.weekday = weekday
        self.order = order

