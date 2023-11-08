from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre = db.relationship("Genre")
    director = db.relationship("Director")

    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Integer()

    genre_id = fields.Integer()
    director_id = fields.Integer()


class DirectorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movies_query = Movie.query

        args = request.args

        director_id = args.get("director_id")
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        movies = movies_query.all()

        return movies_schema.dump(movies), 200

    def post(self):

        movie = movie_schema.load(request.json)
        db.session.add(Movie(**movie))
        db.session.commit()

        return None, 201


@movies_ns.route("/<int:uid>")
class MovieView(Resource):
    def get(self, uid):
        try:
            movie = Movie.query.get(uid)

            return movie_schema.dump(movie), 200

        except Exception as e:

            return "", 404

    def put(self, uid):
        try:
            db.session.query(Movie).filter(Movie.id == uid).update(request.json)
            db.session.commit()

            return "", 204
        except Exception as e:

            return "", 404

    def delete(self, uid):
        try:
            movie = Movie.query.get(uid)
            db.session.delete(movie)
            db.session.commit()

            return "", 204

        except Exception as e:

            return "", 404


@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()

        return directors_schema.dump(directors), 200


@directors_ns.route("/<int:director_id>")
class DirectorView(Resource):
    def get(self, director_id):
        try:
            director = Director.query.get(director_id)

            return director_schema.dump(director), 200

        except Exception as e:

            return "", 404


@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200


@genres_ns.route("/<int:genre_id>")
class GenreView(Resource):
    def get(self, genre_id):
        try:
            genre = Genre.query.get(genre_id)

            return genre_schema.dump(genre), 200

        except Exception as e:

            return "", 404


if __name__ == '__main__':
    app.run(debug=True)
