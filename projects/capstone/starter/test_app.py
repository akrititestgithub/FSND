import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actors, Movies


class CapstoneTest(unittest.TestCase):
    def setUp(self):
        self.token_assistant = os.environ['assistant_token']
        self.token_director = os.environ['director_token']
        self.token_producer = os.environ['producer_token']
        self.app = create_app()
        print("created app successfully",flush=True)
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = 'postgresql://abagaria@localhost:5432/capstone_test'

        setup_db(self.app, self.database_path)
        print("db setup successful.....",flush=True)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        #delete_db()
        pass

    def test_create_Actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "test_actor1",
                "age": 10,
                "salary": 3000,
                "email": "alka@alka.com"
                },
            headers={"Authorization": 'bearer '+self.token_director}
            )

        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_create_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "name": "test_movie1",
                "length": 10.5,
                "genre": "Action"
                },
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_get_Actors(self):
        res = self.client().get('/actors', headers={
            "Authorization": 'bearer '+self.token_assistant})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
            "Authorization": 'bearer '+self.token_assistant})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_add_and_delete_actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "test2",
                "age": 10,
                "salary": 3000,
                "email": "test@test.com"
                },
            headers={"Authorization": 'bearer '+self.token_director}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

        res = self.client().delete('/actors/2', headers={
            "Authorization": 'bearer '+self.token_producer})
        body = json.loads(res.data)
        ques = Actors.query.filter_by(id=2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(ques, None)

    def test_update_actors(self):
        res = self.client().patch(
            '/actors/1',
            json={
                "name": "alka",
                "age": "1",
                "salary": "3000",
                "email": "abc@alka.com"},
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)


    def test_Unauthorized_get_actors(self):
        res = self.client().get('/actors')
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)



    def test_404_wrong_endpoint_get_actors(self):
        res = self.client().get('/actorss', headers={
            "Authorization": 'bearer '+self.token_assistant})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)



    def test_404_wrong_endpoint_get_movies(self):
        res = self.client().get('/movi', headers={
            "Authorization": 'bearer '+self.token_assistant})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)



    def test_422_wrongId_delete_actor(self):
        res = self.client().delete('/actors/1000', headers={
            "Authorization": 'bearer '+self.token_producer})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    def test_401_unauthorized_delete_actor(self):
        res = self.client().delete('/actors/1', headers={
            "Authorization": 'bearer '+self.token_assistant})
        print(res.data)
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    def test_add_delete_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "name": "test_movie2",
                "length": 10.5,
                "genre": "Action"
                },
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

        res = self.client().delete('movies/2', headers={
            "Authorization": 'bearer '+self.token_producer})
        body = json.loads(res.data)
        ques = Movies.query.filter_by(id=2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(ques, None)

    def test_422_wrongId_delete_movies(self):
        res = self.client().delete('/movies/1000', headers={
            "Authorization": 'bearer '+self.token_producer})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    def test_unauthorized_delete_movies(self):
        res = self.client().delete('/movies/1', headers={
            "Authorization": 'bearer '+self.token_assistant})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)


    def test_401_unauthorized_create_actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "test3",
                "age": "15",
                "salary": "5000",
                "email": "kcdskl@jcds.com",
                },
            headers={"Authorization": 'bearer '+self.token_assistant}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    def test_401_unauthorized_create_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "name": "test1",
                "length": "16",
                "genre": "action",
                },
            headers={"Authorization": 'bearer '+self.token_assistant}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    def test_update_Movies(self):
        res = self.client().patch(
            '/movies/1',
            json={
                "name": "alks_mov",
                "length": "10",
                "genre": "Action"},
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_404_wrongID_update_movie(self):
        res = self.client().patch(
            '/movies/1000',
            json={
                "name": "john",
                "length": "10",
                "genre": "Action"},
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    def test_401_unauthorized_update_movie(self):
        res = self.client().patch(
            '/movies/100',
            json={
                "name": "test",
                "length": "10",
                "genre": "Action"},
            headers={"Authorization": 'bearer '+self.token_assistant}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)



    def test_404_wrongId_update_actor(self):
        res = self.client().patch(
            '/actors/1000',
            json={
                "name": "actor1",
                "age": "10",
                "salary": "3000",
                "email": "act1@act1.com"},
            headers={"Authorization": 'bearer '+self.token_producer}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)


if __name__ == "__main__":
    unittest.main()
