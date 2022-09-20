# * ----------------------------------------------------------------------------#
# * Imports
# *----------------------------------------------------------------------------#

import sys

from flask import (Blueprint, Flask, abort, flash, redirect, render_template,
                   request, url_for)

from database import db
from forms import *
from models import Artist, Show, Venue

route_blueprint = Blueprint("routes", __name__)


# *----------------------------------------------------------------------------#
# * Controllers.
# *----------------------------------------------------------------------------#


@route_blueprint.route("/")
def index():
    print("HELLO")
    return render_template("pages/home.html")


# * -------------------------------------------------------------------------- #
# *  Venues
# *  ----------------------------------------------------------------


@route_blueprint.route("/venues")
def venues():
    venues_list = Venue.query.distinct(Venue.city, Venue.state).all()
    data = [
        {
            "city": venue.city,
            "state": venue.state,
            "venues": [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(
                        [
                            show
                            for show in venue.shows
                            if show.start_time > datetime.now()
                        ]
                    ),
                }
                for venue in Venue.query.filter_by(city=venue.city).all()
            ],
        }
        for venue in venues_list
    ]

    return render_template("pages/venues.html", areas=data)


@route_blueprint.route("/venues/search", methods=["POST"])
def search_venues():
    # Implement search on artists with partial string search
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = [
        {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(
                Show.query.filter(Show.venue_id == venue.id)
                .filter(Show.start_time > datetime.now())
                .all()
            ),
        }
        for venue in venues
    ]
    response = {"count": len(venues), "data": data}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@route_blueprint.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id

    venues = Venue.query.filter(Venue.id == venue_id).first()

    # query for past shows and upcoming shows
    past_shows = (
        Show.query.filter(Show.venue_id == venue_id)
        .filter(Show.start_time < datetime.now())
        .all()
    )
    upcoming_shows = (
        Show.query.filter(Show.venue_id == venue_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )

    # create past shows and upcoming shows list
    past_shows_list = [
        {
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter(Artist.id == show.artist_id)
            .first()
            .name,
            "artist_image_link": Artist.query.filter(Artist.id == show.artist_id)
            .first()
            .image_link,
            "start_time": str(show.start_time),
        }
        for show in past_shows
    ]

    upcoming_shows_list = [
        {
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter(Artist.id == show.artist_id)
            .first()
            .name,
            "artist_image_link": Artist.query.filter(Artist.id == show.artist_id)
            .first()
            .image_link,
            "start_time": str(show.start_time),
        }
        for show in upcoming_shows
    ]

    data = {
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website_link": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template("pages/show_venue.html", venue=data)


# *  ----------------------------------------------------------------
# *  Create Venue
# *  ----------------------------------------------------------------


@route_blueprint.route("/venues/create", methods=["GET"])
def create_venue_form():
    # Renders the form to create a new venue
    form = VenueForm()

    return render_template("forms/new_venue.html", form=form)


@route_blueprint.route("/venues/create", methods=["POST"])
def create_venue_submission():  # sourcery skip: raise-specific-error
    # Insert form data as a new Venue record in the db, instead
    # Modify data to be the data object returned from db insertion
    error = False
    try:
        # validate form
        venue = Venue(
            name=request.form["name"],
            city=request.form["city"],
            state=request.form["state"],
            address=request.form["address"],
            phone=request.form["phone"],
            genres=request.form.getlist("genres"),
            facebook_link=request.form["facebook_link"],
            image_link=request.form["image_link"],
            website_link=request.form["website_link"],
            seeking_talent="seeking_talent" in request.form,
            seeking_description=request.form["seeking_description"],
        )
        db.session.add(venue)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
    else:
        flash("Venue " + request.form["name"] + " was successfully listed!")

    return render_template("pages/home.html")


@route_blueprint.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # Delete venue record from db
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Venue "
            + request.form["name"]
            + " could not be deleted."
        )
    else:
        flash("Venue " + request.form["name"] + " was successfully deleted!")

    return render_template("pages/home.html")


# *  ----------------------------------------------------------------
# *  ARTISTS
# *  ----------------------------------------------------------------


@route_blueprint.route("/artists")
def artists():
    # Get the artists from the database
    artists = Artist.query.all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    return render_template("pages/artists.html", artists=data)


@route_blueprint.route("/artists/search", methods=["POST"])
def search_artists():
    # Search on artist records with partial string search.
    search_term = request.form.get("search_term", "")
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = [
        {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(
                Show.query.filter(Show.artist_id == artist.id)
                .filter(Show.start_time > datetime.now())
                .all()
            ),
        }
        for artist in artists
    ]
    response = {"count": len(artists), "data": data}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@route_blueprint.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    past_shows = (
        Show.query.filter(Show.artist_id == artist_id)
        .filter(Show.start_time < datetime.now())
        .all()
    )
    upcoming_shows = (
        Show.query.filter(Show.artist_id == artist_id)
        .filter(Show.start_time > datetime.now())
        .all()
    )

    # filter venues by past shows
    past_shows_list = [
        {
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter(Venue.id == show.venue_id).first().name,
            "venue_image_link": Venue.query.filter(Venue.id == show.venue_id)
            .first()
            .image_link,
            "start_time": str(show.start_time),
        }
        for show in past_shows
    ]

    # filter venues by upcoming shows
    upcoming_shows_list = [
        {
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter(Venue.id == show.venue_id).first().name,
            "venue_image_link": Venue.query.filter(Venue.id == show.venue_id)
            .first()
            .image_link,
            "start_time": str(show.start_time),
        }
        for show in upcoming_shows
    ]

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template("pages/show_artist.html", artist=data)


# *  ----------------------------------------------------------------
# *  UPDATE VENUE AND ARTIST OBJECTS
# *  ----------------------------------------------------------------


@route_blueprint.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    # Render the form to edit an artist object
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@route_blueprint.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # Get artist record with ID <artist_id> from the db and update it with the new attributes
    error = False
    try:
        Artist.update(
            id=artist_id,
            name=request.form["name"],
            city=request.form["city"],
            state=request.form["state"],
            phone=request.form["phone"],
            genres=request.form.getlist("genres"),
            facebook_link=request.form["facebook_link"],
            image_link=request.form["image_link"],
            website_link=request.form["website_link"],
            seeking_venue="seeking_venue" in request.form,
            seeking_description=request.form["seeking_description"],
        )
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be edited."
        )
    else:
        flash("Artist " + request.form["name"] + " was successfully edited!")

    return redirect(url_for("show_artist", artist_id=artist_id))


@route_blueprint.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    # Render the form to edit a venue with the given venue_id
    form = VenueForm()

    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@route_blueprint.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # Get venue record from database by id and update it with the new attributes
    error = False
    try:
        Venue.update(
            id=venue_id,
            name=request.form["name"],
            city=request.form["city"],
            state=request.form["state"],
            address=request.form["address"],
            phone=request.form["phone"],
            genres=request.form.getlist("genres"),
            facebook_link=request.form["facebook_link"],
            image_link=request.form["image_link"],
            website_link=request.form["website_link"],
            seeking_talent="seeking_talent" in request.form,
            seeking_description=request.form["seeking_description"],
        )
    except Exception:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be edited."
        )
    else:
        flash("Venue " + request.form["name"] + " was successfully edited!")

    return redirect(url_for("show_venue", venue_id=venue_id))


# *  ----------------------------------------------------------------
# *  Create Artist
# *  ----------------------------------------------------------------


@route_blueprint.route("/artists/create", methods=["GET"])
def create_artist_form():
    # Render the form to create a new artist
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@route_blueprint.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # Create a new artist object and add it to the database
   
    error = False
    try:
        artist = Artist(
            name=request.form["name"],
            city=request.form["city"],
            state=request.form["state"],
            phone=request.form["phone"],
            genres=request.form.getlist("genres"),
            facebook_link=request.form["facebook_link"],
            website_link=request.form["website_link"],
            image_link=request.form["image_link"],
            seeking_venue="seeking_venue" in request.form,
            seeking_description=request.form["seeking_description"],
        )

        db.session.add(artist)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
    if not error:
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
    return render_template("pages/home.html")


# * -----------------------------------------------------------------
# *  SHOWS
# *  ----------------------------------------------------------------


@route_blueprint.route("/shows")
def shows():
    # displays list of shows at /shows using Join to get venue and artist info
    shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(
        Artist, Show.artist_id == Artist.id
    )
    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time),
        }
        for show in shows
    ]

    return render_template("pages/shows.html", shows=data)


@route_blueprint.route("/shows/create")
def create_shows():
    # renders form
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@route_blueprint.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        show = Show(
            artist_id=request.form["artist_id"],
            venue_id=request.form["venue_id"],
            start_time=request.form["start_time"],
        )
        db.session.add(show)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("An error occurred. Show could not be listed.")
    if not error:
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    return render_template("pages/home.html")


# *  ----------------------------------------------------------------
# *  Error Handlers
# *  ----------------------------------------------------------------


@route_blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@route_blueprint.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500