import os
from sqlalchemy import Column, String, Integer, Float, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate
import sys;

# database_name = "capstone"
# database_path = "postgres://{}/{}".format(
#   'localhost:5432',
#   database_name)

db = SQLAlchemy()
class Movies(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    length = Column(Float)
    genre = Column(String)

    def __init__(self, length, genre, name):
        self.length = length
        self.genre = genre
        self.name = name

    def insert(self):
        print("entered db.models..",flush=True)
        try:
            #print("entered db.models1..",flush=True)
            db.session.add(self)
            db.session.commit()
        except:
            #print("entered db.models2..",flush=True)
            db.session.rollback()
            print(sys.exc_info())
        finally:
            #print("entered db.models3..",flush=True)
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'length': self.length,
          'genre': self.genre,
        }


class Actors(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String)
    salary = Column(Integer)

    def __init__(self, name, age, email, salary):
        print("init actor",flush=True)
        self.age = age
        self.email = email
        self.name = name
        self.salary = salary

    def insert(self):
        print("entered db.models..",flush=True)
        try:
            #print("entered db.models1..",flush=True)
            db.session.add(self)
            db.session.commit()
        except:
            #print("entered db.models2..",flush=True)
            db.session.rollback()
            print(sys.exc_info())
        finally:
            #print("entered db.models3..",flush=True)
            db.session.close()


    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()


    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()



    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'age': self.age,
          'email': self.email,
          'salary': self.salary,
        }


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    print(database_path,flush=True)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    #db.drop_all()
    db.create_all()
    migrate = Migrate(app, db)

# def delete_db():
#     db.drop_all()
#     db.session.remove()


