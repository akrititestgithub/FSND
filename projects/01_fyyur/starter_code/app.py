#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import os
import sys
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import date

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://abagaria@localhost:5432/fyyurapp'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
## TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genre = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    website = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    website = db.Column(db.String)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

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
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  data = []
  
  city_state_items = db.session.query(Venue.state,Venue.city).group_by(Venue.state,Venue.city).all()
  for item in city_state_items:
    temp1 = {}
    temp1['city'] = item[1]
    temp1['state'] = item[0]
    venues_data = []

    now= datetime.utcnow()
    venues = Venue.query.filter_by(state=item[0], city=item[1]).all()
    print("city = %s , state = %s, venues = %s"%(item[1],item[0],venues))
    for venue in venues:
      venue_data ={}
      no_of_up = db.session.query(Venue).join(Show, Show.venue_id == Venue.id).filter(Venue.id == venue.id).filter(Show.start_time>now).count()
      venue_data['id'] =venue.id 
      venue_data['name'] = venue.name
      venue_data['num_upcoming_shows'] = no_of_up
      venues_data.append(venue_data)
    temp1['venues'] = venues_data
    print(temp1)
    data.append(temp1)


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term =  "%{}%".format(request.form.get('search_term'))
  print(search_term)

  count =  Venue.query.filter(Venue.name.like(search_term)).count()
  venues = Venue.query.filter(Venue.name.like(search_term)).all()
  now= datetime.utcnow()
  venues_data = []
  temp1 = {}
  for venue in venues:
    venue_data ={}
    no_of_up = db.session.query(Venue).join(Show, Show.venue_id == Venue.id).filter(Venue.id == venue.id).filter(Show.start_time>now).count()
    venue_data['id'] =venue.id 
    venue_data['name'] = venue.name
    venue_data['num_upcoming_shows'] = no_of_up
    venues_data.append(venue_data)
  temp1['data'] = venues_data
  temp1['count'] = count
  
  print("temp1 = %s  " %(temp1))
  return render_template('pages/search_venues.html', results=temp1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data = {}
  venue1 = Venue.query.get(venue_id)
  data = vars(venue1)
  now= datetime.utcnow()
  no_of_up = db.session.query(Venue).join(Show, Show.venue_id == Venue.id).filter(Venue.id == venue1.id).filter(Show.start_time>now).count()
  upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Venue.id == venue1.id).filter(Show.start_time>now).all()
  no_of_past = db.session.query(Venue).join(Show, Show.venue_id == Venue.id).filter(Venue.id == venue1.id).filter(Show.start_time<now).count()
  past_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Venue.id == venue1.id).filter(Show.start_time<now).all()
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_entry = {}
    upcoming_shows_entry['artist_id']=show.artist_id
    artist = Artist.query.get(show.artist_id)
    upcoming_shows_entry['artist_name']=artist.name
    upcoming_shows_entry['artist_image_link']=artist.image_link
    upcoming_shows_entry['start_time'] = format_datetime(datetime.strftime(show.start_time, '%Y-%m-%d %H:%M:%S'),'full')
    upcoming_shows_list.append(upcoming_shows_entry)

  data['upcoming_shows'] = upcoming_shows_list
  data['past_shows_count'] = no_of_past
  data['upcoming_shows_count'] = no_of_up

  past_shows_list = []
  for show in past_shows:
    past_shows_entry = {}
    past_shows_entry['artist_id']=show.artist_id
    artist = Artist.query.get(show.artist_id)
    past_shows_entry['artist_name']=artist.name
    past_shows_entry['artist_image_link']=artist.image_link
    past_shows_entry['start_time'] = format_datetime(datetime.strftime(show.start_time, '%Y-%m-%d %H:%M:%S'),'full')
    past_shows_list.append(past_shows_entry)
  data['past_shows'] = past_shows_list
  print(data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  # body = {}
  try:
    name = request.form.get('name')
    genre = request.form.get('genre')
    city = request.form.get('city')
    state = request.form.get('state')
    website = request.form.get('website')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    venue =  Venue(name=name, genre=genre, city=city, state=state, website=website, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('Venue ' + request.form['name'] + ' coulnot be created!')
    abort(500)

  # on successful db insert, flash success
  
  # TODO: #DONE on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Todo.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #   data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  artists = Artist.query.all()
  data = []

  for art in artists:
    data_item = {}
    data_item['id'] = art.id
    data_item['name'] = art.name
    data.append(data_item)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  search_term =  "%{}%".format(request.form.get('search_term'))
  print(search_term)

  count =  Artist.query.filter(Artist.name.like(search_term)).count()
  artists = Artist.query.filter(Artist.name.like(search_term)).all()
  now= datetime.utcnow()
  artists_data = []
  response = {}
  for artist in artists:
    artist_data ={}
    no_of_up = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Artist.id == artist.id).filter(Show.start_time>now).count()
    artist_data['id'] =artist.id 
    artist_data['name'] = artist.name
    artist_data['num_upcoming_shows'] = no_of_up
    artists_data.append(artist_data)
  response['data'] = artists_data
  response['count'] = count
  
  print("response = %s  " %(response))
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }

  data = {}
  artist1 = Artist.query.get(artist_id)
  data = vars(artist1)
  now= datetime.utcnow()
  no_of_up = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Artist.id == artist1.id).filter(Show.start_time>now).count()
  upcoming_shows = db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist1.id).filter(Show.start_time>now).all()
  no_of_past = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Artist.id == artist1.id).filter(Show.start_time<now).count()
  past_shows = db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist1.id).filter(Show.start_time<now).all()
  upcoming_shows_list = []
  for show in upcoming_shows:
    upcoming_shows_entry = {}
    upcoming_shows_entry['venue_id']=show.venue_id
    venue = Venue.query.get(show.venue_id)
    upcoming_shows_entry['venue_name']=venue.name
    upcoming_shows_entry['venue_image_link']=venue.image_link
    upcoming_shows_entry['start_time'] = format_datetime(datetime.strftime(show.start_time, '%Y-%m-%d %H:%M:%S'),'full')
    upcoming_shows_list.append(upcoming_shows_entry)

  data['upcoming_shows'] = upcoming_shows_list
  data['past_shows_count'] = no_of_past
  data['upcoming_shows_count'] = no_of_up

  past_shows_list = []
  for show in past_shows:
    past_shows_entry = {}
    past_shows_entry['venue_id']=show.venue_id
    venue = Venue.query.get(show.venue_id)
    past_shows_entry['venue_name']=venue.name
    past_shows_entry['venue_image_link']=venue.image_link
    past_shows_entry['start_time'] = format_datetime(datetime.strftime(show.start_time, '%Y-%m-%d %H:%M:%S'),'full')
    past_shows_list.append(past_shows_entry)
  data['past_shows'] = past_shows_list
  print(data)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []

  shows_list = Show.query.all()
  for show in shows_list:
    show_det = {}
    artist_id = show.artist_id
    venue_id = show.venue_id
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    show_det['venue_id'] = venue_id
    show_det['venue_name'] = venue.name
    show_det['artist_id'] = artist_id
    show_det['artist_name'] = artist.name
    show_det['artist_image_link']=artist.image_link
    show_det['start_time'] = format_datetime(datetime.strftime(show.start_time, '%Y-%m-%d %H:%M:%S'),'full')
    data.append(show_det)
    

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
  error = False
  date_format = '%Y-%m-%d %H:%M:%S'
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = datetime.strptime(request.form['start_time'], date_format)
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    db.session.rollback()
  finally:
    db.session.close()
    if error: flash('An error occurred. Show could not be listed.')
    else: flash('Show was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7000))
    app.run(host='0.0.0.0', port=port)
