import csv
import logging

from artist import Artist
from theatre import Theatre

artist_path = 'data/artists.csv'
theatre_path = 'data/theatres.csv'
fixed_addresses_path = 'data/fixed_addresses.csv'
WEEKDAY = 'Friday'

LOGGER = logging.getLogger(__name__)


def _load_artists(path):
    artists = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['artist', 'tier'])
        for row in reader:
            artists.append(Artist(name=row['artist'].strip(),
                                  weekday=WEEKDAY,
                                  tier=row['tier'].strip()))
    return artists


def _load_theatres(path):
    theatres = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['address', 'capacity'])
        for row in reader:
            theatres.append(Theatre(
                address=row['address'].strip(),
                capacity=int(row['capacity']),
                weekday=WEEKDAY))
    return theatres


def _load_fixed_addresses(path):
    fixed_addresses = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['artist', 'address'])
        for row in reader:
            fixed_addresses.append((row['artist'].strip(), row['address'].strip()))
    LOGGER.info('We hebben %s artiesten die een specifiek adres hebben geclaimd')
    return fixed_addresses


def _assign_artists_to_theatres(artists, theatres, fixed_addresses):
    # We should first assign the artists who have a fixed theatre. After that, assign
    # the remaining artists/and theatres: first, fill the biggest theatres with A
    # artists, then with B artists, then with C artists.
    fixed_address = []
    for artist_name, address in fixed_addresses:
        try:
            artist = [a for a in artists if a.name == artist_name][0]
            theatre = [t for t in theatres if t.address == address][0]
            artist.theatre = theatre
            theatre.artist = artist
            fixed_address.append((artist, theatre))
        except IndexError:
            LOGGER.info('Er staat een onbekend adres of een onbekende artiest tussen'
                        'de fixed_addresses; het gaat om artiest %s of adres %s',
                        artist_name,
                        address)

    remaining_artists = [a for a in artists if a.theatre is None]
    remaining_artists.sort(key=lambda a: a.tier)
    remaining_theatres = [t for t in theatres if t.artist is None]
    remaining_theatres.sort(key=lambda t: -t.capacity)
    LOGGER.info("We moeten nog %s artiesten toewijzen aan %s theaters",
                len(remaining_artists),
                len(remaining_theatres))

    for a, t in zip(remaining_artists, remaining_theatres):
        a.theatre = t
        t.artist = a

    return artists, theatres


def load_and_assign_artists_theatres():
    artists = _load_artists(artist_path)
    theatres = _load_theatres(theatre_path)
    fixed_addresses = _load_fixed_addresses(fixed_addresses_path)

    if len(artists) != len(theatres):
        LOGGER.warning('Het aantal artiesten klopt niet met het aantal theaters! We '
                       'hebben %s artiesten en %s theaters.',
                       len(artists),
                       len(theatres))
    LOGGER.info('Er zijn per slot %s voorstellingen', len(theatres))
    total_capacity = sum(theatre.capacity for theatre in theatres)
    LOGGER.info('Totale capaciteit (=aantal tickets) per slot: %s', total_capacity)

    artists, theatres = _assign_artists_to_theatres(artists, theatres, fixed_addresses)

    LOGGER.info('Per slot hebben we %s tier-A artiesten, %s tier-B artiesten, en '
                '%s tier-C artiesten',
                len([a for a in artists if a.tier=='A']),
                len([a for a in artists if a.tier=='B']),
                len([a for a in artists if a.tier=='C']))
    LOGGER.info('Per slot hebben we %s tier-A stoelen, %s tier-B stoelen, en '
                 '%s tier-C stoelen te verdelen',
                 sum([t.capacity for t in theatres if t.artist.tier=='A']),
                 sum([t.capacity for t in theatres if t.artist.tier=='B']),
                 sum([t.capacity for t in theatres if t.artist.tier=='C'])
                 )

    return artists, theatres, total_capacity