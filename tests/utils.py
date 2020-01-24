import datetime


def today():
    return datetime.date.today()


def yesterday():
    return today() - datetime.timedelta(days=1)


def tomorrow():
    return today() + datetime.timedelta(days=1)
