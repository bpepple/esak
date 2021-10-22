"""
Creator module.

This module provides the following classes:

- Creator
- CreatorSchema
"""
from marshmallow import INCLUDE, Schema, fields, post_load, pre_load

from esak import events_summary, exceptions, series


class Creator:
    """
    The Creator object contains information for creators.

    :param `**kwargs`: The keyword arguments is used for setting creator data from Marvel.
    """

    def __init__(self, **kwargs):
        """Intialize a new Creator."""
        if "response" not in kwargs:
            kwargs["response"] = None

        for k, v in kwargs.items():
            setattr(self, k, v)


class CreatorsSchema(Schema):
    """Schema for the Creator API."""

    id = fields.Int()
    firstName = fields.Str(attribute="first_name")
    middleName = fields.Str(attribute="middle_name")
    lastName = fields.Str(attribute="last_name")
    suffix = fields.Str()
    fullName = fields.Str(attribute="full_name")
    modified = fields.DateTime()
    resourceURI = fields.Str(attribute="resource_uri")
    # urls
    thumbnail = fields.Url()
    series = fields.Nested(series.SeriesSchema, many=True)
    # stories
    events = fields.Nested(events_summary.EventSummarySchema, many=True)

    class Meta:
        """Any unknown fields will be included."""

        unknown = INCLUDE

    @pre_load
    def process_input(self, data, **kwargs):
        if data.get("code", 200) != 200:
            raise exceptions.ApiError(data.get("status"))

        if "status" in data:
            data["data"]["results"][0]["response"] = data
            data = data["data"]["results"][0]

        if "thumbnail" in data:
            data["thumbnail"] = f"{data['thumbnail']['path']}.{data['thumbnail']['extension']}"

        if "events" in data:
            data["events"] = data["events"]["items"]

        if "series" in data:
            data["series"] = data["series"]["items"]

        data["id"] = data["resourceURI"].split("/")[-1]
        return data

    @post_load
    def make(self, data, **kwargs):
        """
        Make the Creator object.

        :param data: Data from Marvel response.

        :returns: :class:`Creator` object
        :rtype: Creator
        """
        return Creator(**data)
