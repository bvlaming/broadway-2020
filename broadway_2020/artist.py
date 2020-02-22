class Artist:
    def __init__(self, name, weekday, tier):
        self.name = name
        self.weekday = weekday
        self.tier = tier
        self.booked = {}
        self.theatre = None