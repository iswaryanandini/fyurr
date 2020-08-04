#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date
from sqlalchemy import func
from array import array

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
now= datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', cascade = "all,delete", backref='venue',lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    past_shows = db.Column(db.String(120))
    upcoming_shows = db.Column(db.String(120))
    past_shows_count = db.Column(db.Integer)
    upcoming_shos_count = db.Column(db.Integer)
    shows = db.relationship('Show', cascade = "all,delete", backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key = True)
    venue_name = db.Column(db.String)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key = True)
    artist_name = db.Column(db.String)
    artist_image_link = db.Column(db.String(120))
    start_time = db.Column(db.DateTime)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, locale='en_US')#(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def get_venue(self, city, state):
  return self.query.filter_by(self.city==city, self.state==state).all()

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    all_places = Venue.query.distinct(Venue.city, Venue.state).all()
    # print(all_places)
    for place in all_places:
        local = {
            'city': place.city,
            'state': place.state
        }
        data.append(local)
    venues = Venue.query.all()
    # shows = Show.query.all()
    # upcomingShows = []
    # print(data)
    for each in data:
        each['places'] = []
        for venue in venues:
            now= datetime.utcnow()
            shows = db.session.query(Show.venue_id).filter(Show.venue_id == venue.id, Show.start_time>now).count()
            if venue.city == each["city"] and venue.state == each["state"]:
                v = {
                    'id': venue.id,
                    'name': venue.name,
                    'upcoming_shows':shows
                }
                each["places"].append(v)
               
  
                  
    return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def venue():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  # print(search_term)
  ven_name = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data =[]

  for ven in ven_name:
    now= datetime.utcnow()
    shows = db.session.query(Show.venue_id).filter(Show.venue_id == ven.id, Show.start_time>now).count()
    data.append({
      "id": ven.id,
      "name": ven.name,
      "upcoming_shows": shows
    })

  response={
    "count": len(ven_name),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

def fun_past_shows(venue_id):
    past_show_artist = db.session.query(Show.artist_id,Show.artist_name,Show.artist_image_link,Show.start_time).filter(Show.venue_id == venue_id,Show.start_time<now ).all()
    pastShows = []
    for past_show in past_show_artist:
      shows = {
          'artist_id': past_show.artist_id,
          'artist_name': past_show.artist_name,
          'artist_image_link': past_show.artist_image_link,
          'start_time': str(past_show.start_time)
      }
      pastShows.append(shows)
    
    return pastShows

def fun_upcoming_shows(venue_id):
    upcoming_show_artist = db.session.query(Show.artist_id,Show.artist_name,Show.artist_image_link,Show.start_time).filter(Show.venue_id == venue_id,Show.start_time>now ).all()
    upcomingShows = []
    for upcoming_show in upcoming_show_artist:
      shows = {                  
          'artist_id': upcoming_show.artist_id,
          'artist_name': upcoming_show.artist_name,
          'artist_image_link': upcoming_show.artist_image_link,
          'start_time': str(upcoming_show.start_time)
      }
      upcomingShows.append(shows)

        
        
    return upcomingShows

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  id = Venue.query.get(venue_id)
  venues = Venue.query.filter(Venue.id == venue_id).all()
  shows = Show.query.filter(Show.venue_id == venue_id).all()
  past_shows =[]
  upcoming_shows =[]
  
  for each in venues:
    venueData = {      
      "id": each.id,
      "name": each.name,
      "genres": each.genres,
      "address": each.address,
      "city": each.city,
      "state": each.state,
      "phone": each.phone,
      "website": each.website,
      "facebook_link": each.facebook_link,
      "seeking_talent": each.seeking_talent,
      "seeking_description": each.seeking_description,
      "image_link": each.image_link,}

  if shows:
    for each in shows:
      past_shows = fun_past_shows(venue_id)
      upcoming_shows = fun_upcoming_shows(venue_id)

      showData={
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
  else:
    showData={
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
      }


  wholeData = {**venueData, **showData}
  
  
  # data = list(filter(lambda d: d['id'] == venue_id, venues_det))[1]
  return render_template('pages/show_venue.html', venue=wholeData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # newid = Venue.query.all()  
  # currid = newid + 1
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  vid = db.session.query(func.max(Venue.id)).scalar()
  vidmax = vid + 1
  data = request.form 
  name = data['name']
  city = data['city']
  state = data['state']
  address = data['address']
  phone = data['phone']
  genres = request.form.getlist('genres')
  fb_link = data['facebook_link']
  image_link = data['image_link']
  website = data['website']
  seeking_talent = data['seeking_talent']
  seeking_description = data['seeking_description']
  if seeking_talent == 'y':
    seek = True
  else:
    seek = False
  try:
    db.session.add(Venue(
            id=vidmax,
            city=city,
            state=state,
            name=name,
            address=address,
            phone=phone,
            facebook_link=fb_link,
            genres=genres,
            seeking_talent=seek,
            website=website,
            image_link=image_link,
            seeking_description=seeking_description
        ))
  except expression:
        error = true
        print(sys.exc_info())
  finally:
        if not error:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash('An error occurred. Venue ' +
                  name + ' could not be listed.')
            db.session.rollback()
  return render_template('pages/home.html')
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + request.form['id'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue {venue_id} could not be deleted.')
  if not error: 
    flash('Venue {venue_id} was successfully deleted.')
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artistslist = Artist.query.all()
  for artist in artistslist:
    list={
      'id':artist.id,
      'name':artist.name
    }
    data.append(list)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artistData = []
  search_term=request.form.get('search_term', '')
  artistsearch = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  for eachartist in artistsearch:
    now = datetime.utcnow()
    showArtist = db.session.query(Show.artist_id).filter(Show.artist_id == eachartist.id).filter(Show.start_time > now).count()
    artistData.append({
      "id": eachartist.id,
      "name": eachartist.name,
      "num_upcoming_shows": showArtist
    })

  response={
    "count": len(artistsearch),
    "data": artistData
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  now = datetime.utcnow()
  pastShows = []
  upcomingShows = []
  id = Artist.query.get(artist_id)  
  artistList = Artist.query.filter(Artist.id == artist_id).all()
  showArtist = db.session.query(Venue.id,Venue.name,Venue.image_link,Show.start_time).join(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id).all()
  for eachshow in showArtist:
    if eachshow.start_time <now:
      pastShows.append({
        "venue_id": eachshow.id,
        "venue_name": eachshow.name,
        "venue_image_link": eachshow.image_link,
        "start_time":eachshow.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    elif eachshow.start_time >now:
      upcomingShows.append({
        "venue_id": eachshow.id,
        "venue_name": eachshow.name,
        "venue_image_link": eachshow.image_link,
        "start_time": eachshow.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  for eachartist in artistList:
    artistdata = {
      "id": eachartist.id,
      "name": eachartist.name,
      "genres": eachartist.genres,
      "city": eachartist.city,
      "state": eachartist.state,
      "phone": eachartist.phone,
      "website": eachartist.website,
      "facebook_link": eachartist.facebook_link,
      "seeking_venue": eachartist.seeking_venue,
      "seeking_description": eachartist.seeking_description,
      "image_link": eachartist.image_link,
      "past_shows": pastShows,
      "upcoming_shows": upcomingShows,
      "past_shows_count": len(pastShows),
      "upcoming_shows_count": len(upcomingShows),
    }
      
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artistdata)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  artist.name = form.data['name']
  artist.phone = form.data['phone']
  artist.city = form.data['city']
  artist.state = form.data['state']
  artist.genres = form.data['genres']
  artist.facebook_link = form.data['facebook_link']
  artist.image_link = form.data['image_link']
  artist.website = form.data['website']
  artist.seeking_venue = form.data['seeking_venue']
  artist.seeking_description = form.data['seeking_description']
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  venue.name = form.data['name']
  venue.phone = form.data['phone']
  venue.city = form.data['city']
  venue.state = form.data['state']
  venue.address = form.data['address']
  venue.genres = form.data['genres']
  venue.facebook_link = form.data['facebook_link']
  venue.image_link = form.data['image_link']
  venue.website = form.data['website']
  venue.seeking_talent = form.data['seeking_talent']
  venue.seeking_description = form.data['seeking_description']
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  data = request.form
  newartists = Artist(                   
                    name = data['name'],
                    city = data['city'],
                    state = data['state'],
                    phone = data['phone'],
                    genres = request.form.getlist('genres'),
                    facebook_link = data['facebook_link'],
                    image_link = data['image_link'],
                    website = data['website'],
                    seeking_venue = data['seeking_venue'],
                    seeking_description = data['seeking_description'],
  )
  try:
    db.session.add(newartists)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  shows = Show.query.all()
  for eachshow in shows:
    showlist={
      "venue_id": eachshow.venue_id,
      "venue_name": eachshow.venue_name,
      "artist_id": eachshow.artist_id,
      "artist_name": eachshow.artist_name,
      "artist_image_link": eachshow.artist_image_link,
      "start_time": eachshow.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    data.append(showlist)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  data = request.form
  newShows = Show(                   
                    venue_id = data['venue_id'],
                    venue_name = db.session.query(Venue.name).filter(Venue.id == data['venue_id']),
                    artist_id = data['artist_id'],
                    artist_name = db.session.query(Artist.name).filter(Artist.id == data['artist_id']),
                    start_time = data['start_time'],
                    artist_image_link = db.session.query(Artist.image_link).filter(Artist.id == data['artist_id'])
  )
  try:
    db.session.add(newShows)
    db.session.commit()
    flash('Show ' + request.form['venue_id'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Artist ' + data.venue_id + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
