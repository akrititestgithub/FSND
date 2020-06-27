import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import requires_auth, AuthError
from models import Actors, Movies

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    print("--------created app------------")
    CORS(app)
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,PATCH')
        return response

    @app.route('/')
    def welcome():
        msg = 'Welcome to the Casting Agency'
        return jsonify(msg)

    @app.route('/actors', methods=['GET'])
    @requires_auth(permission='get:actors')
    def get_Actors(payload):
        actors = Actors.query.all()
        act_format = [act.format() for act in actors]
        result = {
            "success": True,
            "Actors": act_format
        }
        return jsonify(result)

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:actors')
    def delete_Actors(payload, id):

        try:
            act = Actors.query.filter_by(id=id).one_or_none()
            act.delete()
            return jsonify({
                'success': True
            })
        except Exception:
            print("exception raised !!!")
            abort(422)

    @app.route('/actors', methods=['POST'])
    @requires_auth(permission='post:actors')
    def insert_Actors(payload):
        body = request.get_json()
        try:
            actor = Actors(name=body['name'],age=body['age'],email=body['email'],salary=body['salary'])
            #print(actor,flush=True)
            actor.insert()
            return jsonify({
                'success': True
            })
        except Exception:
            abort(404)

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth(permission='patch:actors')
    def update_Actors(payload, id):

        actor = Actors.query.filter(Actors.id == id).one_or_none()
        if actor is None:
            abort(404)
        body = request.get_json()
        if 'name' in body:
            actor.name = body['name']
        if 'age' in body:
            actor.age = body['age']
        if 'email' in body:
            actor.email = body['email']
        if 'salary' in body:
            actor.salary = body['salary']
        actor.update()
        return jsonify({
            'success': True,
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth(permission='get:movies')
    def get_Movies(payload):

        movies = Movies.query.all()
        mov_format = [mov.format() for mov in movies]
        result = {
            "success": True,
            "Movies": mov_format
        }
        return jsonify(result)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:movies')
    def delete_Movies(payload, id):

        try:
            mov = Movies.query.filter_by(id=id).one_or_none()
            mov.delete()
            return jsonify({
                'success': True
            })
        except Exception:
            abort(422)

    @app.route('/movies', methods=['POST'])
    @requires_auth(permission='post:movies')
    def insert_Movies(payload):

        body = request.get_json()
        try:
            movie = Movies(
                name=body['name'],
                length=body['length'],
                genre=body['genre'])

            movie.insert()
            return jsonify({
                'success': True
            })
        except Exception:
            abort(404)

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth(permission='patch:movies')
    def update_Movies(payload, id):
        movie = Movies.query.filter(Movies.id == id).one_or_none()
        if movie is None:
            abort(404)
        body = request.get_json()
        if 'name' in body:
            movie.name = body['name']
        if 'length' in body:
            movie.age = body['length']
        if 'genre' in body:
            movie.email = body['genre']
        movie.update()
        return jsonify({
            'success': True,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
            return jsonify({
            'success': False,
            'error': 422,
            'message': error.description
        }), 422

    @app.errorhandler(400)
    def Bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "Bad request"
        }), 400

    @app.errorhandler(500)
    def InternelError(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def unauthorized(error):
        print(error.status_code)
        print(error.error)
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)