import peewee as pv
from playhouse import sqlite_ext
from playhouse.shortcuts import model_to_dict, dict_to_model

from datetime import datetime, timedelta
import random
import json
from typing import Any

from .default import DEFAULT


database = sqlite_ext.SqliteDatabase(None)


class BaseModel(pv.Model):
    class Meta:
        database = database


class SrsField(pv.TextField):
    def db_value(self, value):
        if value:
            return json.dumps([v.total_seconds() for v in value])

    def python_value(self, value):
        if value:
            return [timedelta(seconds=v) for v in json.loads(value)]
        else:
            return DEFAULT['srs']


class Settings(BaseModel):
    srs = SrsField(default=DEFAULT['srs'])
    type_ = pv.TextField(default=DEFAULT['type_'])
    info = sqlite_ext.JSONField(default=DEFAULT['info'])

    def to_dict(self):
        return model_to_dict(self)


class Tag(BaseModel):
    name = pv.TextField(unique=True, collation='NOCASE')

    def __repr__(self):
        return f'<Tag: "{self.name}">'

    def __str__(self):
        return self.name


class Card(BaseModel):
    item = pv.TextField(unique=True)
    info = sqlite_ext.JSONField(null=True)
    srs_level = pv.IntegerField(null=True)
    next_review = pv.DateTimeField(null=True)
    tags = pv.ManyToManyField(Tag, backref='cards', on_delete='cascade')

    backup = None

    def __repr__(self):
        return self.item

    def _repr_markdown_(self):
        type_ = Settings.get().type_
        if type_ == 'markdown':
            return self.item

    def _repr_html_(self):
        type_ = Settings.get().type_
        if type_ == 'html':
            return self.item

    def mark(self, tag='marked'):
        Tag.get_or_create(name=tag)[0].notes.add(self)

    def unmark(self, tag='marked'):
        Tag.get_or_create(name=tag)[0].notes.remove(self)

    def right(self):
        if not self.backup:
            self.backup = model_to_dict(self)

        if not self.srs_level:
            self.srs_level = 0
        else:
            self.srs_level = self.srs_level + 1

        srs = Settings.get()['srs']
        try:
            self.next_review = datetime.now() + srs[self.srs_level]
        except IndexError:
            self.next_review = None

        self.save()

    correct = next_srs = right

    def wrong(self, next_review=timedelta(minutes=10)):
        if not self.backup:
            self.backup = model_to_dict(self)

        if self.srs_level and self.srs_level > 0:
            self.srs_level = self.srs_level - 1

        self.bury(next_review)

    incorrect = previous_srs = wrong

    def bury(self, next_review=timedelta(hours=4)):
        if not self.backup:
            self.backup = model_to_dict(self)

        if isinstance(next_review, timedelta):
            self.next_review = datetime.now() + next_review
        else:
            self.next_review = next_review
        self.save()

    def undo(self):
        if self.backup:
            dict_to_model(Card, self.backup).save()

    @classmethod
    def iter_quiz(cls, **kwargs):
        db_cards = list(cls.search(**kwargs))
        random.shuffle(db_cards)

        return iter(db_cards)

    @classmethod
    def iter_due(cls, **kwargs):
        return cls.iter_quiz(due=True, **kwargs)

    @classmethod
    def search(cls, tags=None, due=Any, offset=0, limit=None):
        query = cls.select()

        if due is True:
            query = query.where(Card.next_review < datetime.now())
        elif due is False:
            query = query.where(Card.next_review >= datetime.now())
        elif due is None:
            query = query.where(Card.next_review.is_null(True))
        elif isinstance(due, timedelta):
            query = query.where(Card.next_review < datetime.now() + due)
        elif isinstance(due, datetime):
            query = query.where(Card.next_review < due)

        if tags:
            for tag in tags:
                query = query.join(CardTag).join(Tag).where(Tag.name.contains(tag))

        query = query.order_by(cls.next_review.desc())

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query

    def to_dict(self):
        return model_to_dict(self, manytomany=True)

    @classmethod
    def add(cls, item, tags, **kwargs):
        with database.atomic():
            db_card = cls.create(item=item, info=kwargs)
            for tag in tags:
                Tag.get_or_create(name=tag)[0].cards.add(db_card)

            return db_card


CardTag = Card.tags.get_through_model()
