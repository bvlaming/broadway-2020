import logging
import sys
from enum import Enum
import pandas as pd
import numpy as np
from artist import Artist
from theatre import Theatre
from ticket import Ticket

from data_loader import load_and_assign_artists_theatres

import csv

LOGGER = logging.getLogger(__name__)

MAX_SAME_TICKETS = 8
WEEKDAY = "Friday"
PERMUTATION_TYPE = {
    1: ["B", "C", None, "A"],
    2: ["C", None, "A", "B"],
    3: [None, "A", "B", "C"],
    4: ["A", "B", "C", None],
}

PERMUTATION_MAP = {1: 2, 2: 3, 3: 4, 4: 1}


class Tier(Enum):
    A = "a"
    B = "b"
    C = "c"


def locations_valid(theatreA, theatreB):
    # Alleen -1 als we van west naar oost of v.v. gaan, anders zitten we goed
    return theatreA.num_location() * theatreB.num_location() != -1


def find_theatre_and_amount(theatres, slot, permutation_type, previous_theatres):
    """
    For a given slot (1-4), and permutation, find the best theatre and number of tickets
    we could book.

    :param theatres (List[Theatre]):
    :param slot (int): number from 1-4
    :param permutation (int): key of dict, of ['A', 'B','C', None]
    :return:
    """
    permutation = PERMUTATION_TYPE[permutation_type]
    if previous_theatres:
        theatres = [t for t in theatres if
                    (locations_valid(t, previous_theatres[-1])
                     and t not in previous_theatres)]

    tier = permutation[slot - 1]
    if tier is None:
        possible_theatres = theatres
    else:
        possible_theatres = [t for t in theatres if t.artist.tier == tier
                             and t not in previous_theatres]
    possible_theatres.sort(key=lambda t: -t.seats_left_map()[slot])

    theatre = possible_theatres[0]
    amount = min(theatre.seats_left_map()[slot], MAX_SAME_TICKETS)
    return theatre, amount


def assign_set_of_tickets(theatres, ticket_acc, tickets_to_do, permutation_type):
    """
    Greedy assignment algorithm. Try to fill the most empty theatre first.

    first

    :param artists:
    :param theatres:
    :return:
    """
    previous_theatres = []
    amounts = []
    suggested_theatres = {}
    for slot in [1, 2, 3, 4]:
        theatre, amount = find_theatre_and_amount(
            theatres, slot, permutation_type, previous_theatres
        )
        previous_theatres.append(theatre)
        amounts.append(amount)
        suggested_theatres[slot] = theatre

    LOGGER.info('amounts %s', amounts)
    LOGGER.info('theatres %s', [t.address for t in suggested_theatres.values()])
    # LOGGER.info('capacities %s', [t.seats_left_map for t in suggested_theatres.values()])
    amount_to_book = min(amounts)
    amount_to_book = min(amount_to_book, tickets_to_do)
    if amount_to_book == 0:
        LOGGER.info("Everything is booked at some slot")
        # todo: we should probably first relax the tier constraints to fill the
        #  remaining tickets; then, export the tickets in some way.
        return

    ticket = Ticket(WEEKDAY)

    for slot in [1, 2, 3, 4]:
        ticket.number = amount_to_book
        theatre = suggested_theatres[slot]
        theatre.seats_filled[slot] += amount_to_book
        ticket.theatre_map[slot] = theatre
        ticket.artist_map[slot] = ticket.theatre_map[slot].artist

    next_permutation_type = PERMUTATION_MAP[permutation_type]
    ticket_acc.append(ticket)

    # take 8 tickets for the A theatre with most capacity left. Assign to slot 1.
    # take 8 tickets for the largest B theatre with most capacity left. Assign to slot 2.
    # take 8 tickets for the largest C theatre with most capacity left. Assign to slot 3
    # take 8 tickets for the largest (any) theatre with capacity left. Assign to slot 4
    # do this in a permutational way; i.e. start with [A, B, C, any], then [B, C, any, A],
    # then [C, any, A, B] and finally [any, A, B, C]
    return (
        ticket,
        ticket_acc,
        tickets_to_do - amount_to_book,
        next_permutation_type,
    )


def assign_all_tickets(theatres, total_tickets):
    permutation_type = 1
    tickets = []
    tickets_to_do = total_tickets
    while tickets_to_do > 0:
        print(tickets_to_do)
        new_ticket, tickets, tickets_to_do, permutation_type = assign_set_of_tickets(
            theatres, tickets, tickets_to_do, permutation_type
        )

    return tickets


def main():
    artists, theatres, total_tickets = load_and_assign_artists_theatres()
    print(total_tickets)
    t, a = find_theatre_and_amount(theatres, 1, 1, [])
    print(t.address)
    print(a)
    tickets = assign_all_tickets(theatres, total_tickets)
    print(len(tickets))
    print(sum([t.number for t in tickets]))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(name)-4s:%(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
