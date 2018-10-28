from .db import database, Settings, CardTag, Card, Tag


def init(filename, **kwargs):
    database.init(filename, **kwargs)
    database.create_tables([Settings, Card, Tag, CardTag])
    Settings.get_or_create()
