import re
from datetime import datetime

from flask_wtf import Form
from wtforms import (
    BooleanField,
    DateTimeField,
    SelectField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import URL, DataRequired

from enums import Genres, States


def validate_phone(phone):
    # regex for phone number validation
    phone_regex = re.compile(r"^\(?([0-9]{3})\)?[-.●]?([0-9]{3})[-.●]?([0-9]{4})$")

    return phone_regex.match(phone)


class ShowForm(Form):
    artist_id = StringField("artist_id")
    venue_id = StringField("venue_id")
    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.now()
    )


class VenueForm(Form):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state", validators=[DataRequired()], choices=States.choices(), coerce=str
    )
    address = StringField("address", validators=[DataRequired()])
    phone = StringField("phone")
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres", validators=[DataRequired()], choices=Genres.choices(), coerce=str
    )
    facebook_link = StringField("facebook_link", validators=[URL()])
    website_link = StringField("website_link")

    seeking_talent = BooleanField("seeking_talent")

    seeking_description = StringField("seeking_description")



class ArtistForm(Form):
    
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state", validators=[DataRequired()], choices=States.choices(), coerce=str
    )
    phone = StringField(
        # implement phone validation logic for state
        "phone",
        validators=[DataRequired()],
    )
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres", validators=[DataRequired()], choices=Genres.choices(), coerce=str
    )
    facebook_link = StringField(
        # implement enum restriction
        "facebook_link",
        validators=[URL()],
    )

    website_link = StringField("website_link")

    seeking_venue = BooleanField("seeking_venue")

    seeking_description = StringField("seeking_description")

   