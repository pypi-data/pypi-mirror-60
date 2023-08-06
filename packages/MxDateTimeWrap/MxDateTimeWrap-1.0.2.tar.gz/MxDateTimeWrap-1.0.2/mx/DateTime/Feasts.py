from .mx_datetime import DateTime

__all__ = [
    'EasterSunday', 'CarnivalMonday', 'MardiGras', 'AshWednesday',
    'PalmSunday', 'EasterFriday', 'EasterMonday', 'Ascension', 'Pentecost',
    'WhitMonday', 'TrinitySunday', 'CorpusChristi', 'Ostersonntag',
    'DimanchePaques', 'Rosenmontag', 'Aschermittwoch', 'MercrediCendres',
    'Palmsonntag', 'DimancheRameaux', 'GoodFriday', 'Karfreitag',
    'VendrediSaint', 'Ostermontag', 'LundiPaques', 'Himmelfahrt',
    'WhitSunday', 'Pfingstsonntag', 'DimanchePentecote', 'Pfingstmontag',
    'LundiPentecote', 'Fronleichnam', 'FeteDieu'
]

_eastereggs = {}


def EasterSunday(year):

    """EasterSunday(year)

    Return a DateTime instance pointing to Easter Sunday of the given
    year. Note: it must be given *with* century.

    Based on the algorithm presented in the Calendar FAQ by Claus
    Tondering (http://www.pip.dknet.dk/~pip10160/calendar.html), which
    in return is based on the algorithm of Oudin (1940) as quoted in
    "Explanatory Supplement to the Astronomical Almanac", P. Kenneth
    Seidelmann, editor."""

    if year in _eastereggs:
        return _eastereggs[year]
    G = year % 19
    C = year/100
    H = (C - C/4 - (8*C+13)/25 + 19*G + 15) % 30
    I = H - (H/28)*(1 - (H/28)*(29/(H + 1))*((21 - G)/11))
    J = (year + year/4 + I + 2 - C + C/4) % 7
    L = I - J
    month = 3 + (L + 40)/44
    day = L + 28 - 31*(month/4)
    _eastereggs[year] = d = DateTime(year, month, day)
    return d


# Some common feasts derived from Easter Sunday


def CarnivalMonday(year):

    return EasterSunday(year) - 48


def MardiGras(year):

    return EasterSunday(year) - 47


def AshWednesday(year):

    return EasterSunday(year) - 46


def PalmSunday(year):

    return EasterSunday(year) - 7


def EasterFriday(year):

    return EasterSunday(year) - 2


def EasterMonday(year):

    return EasterSunday(year) + 1


def Ascension(year):

    return EasterSunday(year) + 39


def Pentecost(year):

    return EasterSunday(year) + 49


def WhitMonday(year):

    return EasterSunday(year) + 50


def TrinitySunday(year):

    return EasterSunday(year) + 56


def CorpusChristi(year):

    return EasterSunday(year) + 60

Ostersonntag = EasterSunday
DimanchePaques = EasterSunday
Rosenmontag = CarnivalMonday
Aschermittwoch = AshWednesday
MercrediCendres = AshWednesday
Palmsonntag = PalmSunday
DimancheRameaux = PalmSunday
GoodFriday = EasterFriday
Karfreitag = EasterFriday
VendrediSaint = EasterFriday
Ostermontag = EasterMonday
LundiPaques = EasterMonday
Himmelfahrt = Ascension
WhitSunday = Pentecost
Pfingstsonntag = WhitSunday
DimanchePentecote = WhitSunday
Pfingstmontag = WhitMonday
LundiPentecote = WhitMonday
Fronleichnam = CorpusChristi
FeteDieu = CorpusChristi
