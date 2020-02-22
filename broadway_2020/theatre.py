NUM_LOC_MAP = {"west": -1, "central": 0, "east": 1}


class InsufficientCapacity(Exception):
    pass


class Theatre:
    def __init__(self, address, capacity, weekday):
        self.address = address
        self.capacity = capacity
        self.capacity_map = {1: capacity, 2: capacity, 3: capacity, 4: capacity}
        self.weekday = weekday
        self.seats_filled = {1: 0, 2: 0, 3: 0, 4: 0}
        self.location = "central"
        # 'west', 'central', 'east'. Don't go from west to east (or v.v.) directly
        self.artist = None

    def fill_seats(self, amount, slot):
        """
        Try to book `amount` seats for a given slot.

        Params:
            amount (int): number of seats to book.

        Returns:
            bool: True if successful, False if not enough capacity.
        """
        if amount <= self.capacity_map[slot] - self.seats_filled[slot]:
            self.seats_filled[slot] += amount
            return True
        else:
            raise InsufficientCapacity

    def set_remote_location(self, loc):
        """
        Define location of theatre.

        Params:
            loc (str): location.
        """
        self.location = loc

    def num_location(self):
        return NUM_LOC_MAP[self.location]

    def seats_left_map(self):
        seats_map = {}
        for slot in [1, 2, 3, 4]:
            seats_map[slot] = self.capacity - self.seats_filled[slot]
        return seats_map
