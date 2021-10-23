"""
Series module.

This module provides the following classes:

- Series
- SeriesSchema
"""
import itertools

from marshmallow import INCLUDE, Schema, fields, post_load, pre_load
from marshmallow.exceptions import ValidationError

from esak import (
    character_summary,
    comic_summary,
    creator_summary,
    events_summary,
    exceptions,
    series_summary,
    story_summary,
)


class Series:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class SeriesSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    resourceURI = fields.Str(attribute="resource_uri")
    # urls
    startYear = fields.Int(attribute="start_year", allow_none=True)
    endYear = fields.Int(attribute="end_year", allow_none=True)
    rating = fields.Str(allow_none=True)
    modified = fields.DateTime()
    thumbnail = fields.URL(allow_none=True)
    comics = fields.Nested(comic_summary.ComicSummarySchema, many=True)
    stories = fields.Nested(story_summary.StorySummarySchema, many=True)
    events = fields.Nested(events_summary.EventSummarySchema, many=True)
    characters = fields.Nested(character_summary.CharacterSummarySchema, many=True)
    creators = fields.Nested(creator_summary.CreatorSummarySchema, many=True)
    next = fields.Nested(series_summary.SeriesSummarySchema, allow_none=True)
    previous = fields.Nested(series_summary.SeriesSummarySchema, allow_none=True)

    class Meta:
        unknown = INCLUDE

    @pre_load
    def process_input(self, data, **kwargs):
        if data.get("code", 200) != 200:
            raise exceptions.ApiError(data.get("status"))

        if "status" in data:
            data = data["data"]["results"][0]

        # derive ID
        data["id"] = data["resourceURI"].split("/")[-1]

        if "thumbnail" in data and data["thumbnail"] is not None:
            data["thumbnail"] = f"{data['thumbnail']['path']}.{data['thumbnail']['extension']}"
        else:
            data["thumbnail"] = None

        if "comics" in data:
            data["comics"] = data["comics"]["items"]

        if "stories" in data:
            data["stories"] = data["stories"]["items"]

        if "events" in data:
            data["events"] = data["events"]["items"]

        if "characters" in data:
            data["characters"] = data["characters"]["items"]

        if "creators" in data:
            data["creators"] = data["creators"]["items"]

        return data

    @post_load
    def make(self, data, **kwargs):
        return Series(**data)


class SeriesList:
    def __init__(self, response):
        self.series = []
        self.response = response

        for series_dict in response["data"]["results"]:
            try:
                result = SeriesSchema().load(series_dict)
            except ValidationError as error:
                raise exceptions.ApiError(error)

            self.series.append(result)

    def __iter__(self):
        return iter(self.series)

    def __len__(self):
        return len(self.series)

    def __getitem__(self, index):
        try:
            return next(itertools.islice(self.series, index, index + 1))
        except TypeError:
            return list(itertools.islice(self.series, index.start, index.stop, index.step))
