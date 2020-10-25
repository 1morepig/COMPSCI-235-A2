import csv
import os
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from movies_website.adapters.repository import AbstractRepository, RepositoryException
from movies_website.domain.model import Movie, Director, Genre, Actor, User, Review, make_genre_association, make_review, \
    make_actor_association, make_director_association


class MemoryRepository(AbstractRepository):
    # Movie ordered by year, not id. id is assumed unique.

    def __init__(self):
        self._movie = list()
        self._movie_index = dict()
        self._director = list()
        self._genre = list()
        self._actor = list()
        self._users = list()
        self._review = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.user_name == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movie, movie)
        self._movie_index[movie.id] = movie

    def get_movie(self, id: int) -> Movie:
        movie = None

        try:
            movie = self._movie_index[id]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_movie_by_year(self, target_year: int) -> List[Movie]:
        target_movie = Movie(
            release_year=target_year,
            title=None
        )
        matching_movie = list()

        try:
            index = self.movies_index(target_movie)
            for movie in self._movie[index:None]:
                if movie.release_year == target_year:
                    matching_movie.append(movie)
                else:
                    break
        except ValueError:
            # No movie for specified release year. Simply return an empty list.
            pass

        return matching_movie

    def get_number_of_movie(self):
        return len(self._movie)

    def get_first_movie(self) -> Movie:
        movie = None

        if len(self._movie) > 0:
            movie = self._movie[0]
        return movie

    def get_last_movie(self) -> Movie:
        movie = None

        if len(self._movie) > 0:
            movie = self._movie[-1]
        return movie

    def get_movie_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent movie ids in the repository.
        existing_ids = [id for id in id_list if id in self._movie_index]

        # Fetch the Movies.
        movies = [self._movie_index[id] for id in existing_ids]
        return movies

    def get_movie_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a genre with the name genre_name.
        genre = next((genre for genre in self._genre if genre.genre_name == genre_name), None)

        # Retrieve the ids of movies associated with the genre.
        if genre is not None:
            movie_ids = [movie.id for movie in genre.movie_list]
        else:
            # No Genre with name genre_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_actor(self, actor_name: str):
        actor = next((actor for actor in self._actor if actor.actor_full_name == actor_name), None)

        # Retrieve the ids of movies associated with the Actor.
        if actor is not None:
            movie_ids = [movie.id for movie in actor.movie_list]
        else:
            # No actor with name actor_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_director(self, director_name: str):
        director = next((director for director in self._director if director.director_full_name == director_name), None)

        # Retrieve the ids of movies associated with the Director.
        if director is not None:
            movie_ids = [movie.id for movie in director.movie_list]
        else:
            # No director with name director_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_year_of_previous_movie(self, movie: Movie):
        previous_year = None

        try:
            index = self.movies_index(movie)
            for stored_movie in reversed(self._movie[0:index]):
                if stored_movie.release_year < movie.release_year:
                    previous_year = stored_movie.release_year
                    break
        except ValueError:
            # No earlier movies, so return None.
            pass

        return previous_year

    def get_year_of_next_movie(self, movie: Movie):
        next_year = None

        try:
            index = self.movies_index(movie)
            for stored_movie in self._movie[index + 1:len(self._movie)]:
                if stored_movie.release_year > movie.release_year:
                    next_year = stored_movie.release_year
                    break
        except ValueError:
            # No subsequent movies, so return None.
            pass

        return next_year

    def add_genre(self, genre: Genre):
        insort_left(self._genre, genre)

    def get_genre(self) -> List[Genre]:
        return self._genre

    def add_director(self, director: Director):
        insort_left(self._director, director)

    def get_director(self) -> List[Director]:
        return self._director

    def add_actor(self, actor: Actor):
        insort_left(self._actor, actor)

    def get_actor(self) -> List[Actor]:
        return self._actor

    def add_review(self, review: Review):
        super().add_review(review)
        self._review.append(review)

    def get_review(self):
        return self._review

    # Helper method to return movie index.
    def movies_index(self, movie: Movie):
        index = bisect_left(self._movie, movie)
        if index != len(self._movie) and self._movie[index].release_year == movie.release_year:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        movie_file_reader = csv.DictReader(infile)
        for row in movie_file_reader:
            yield row


def load_movies_and_info(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row['Rank'])
        parsed_genres = data_row['Genre'].split(',')
        parsed_actors = data_row['Actors'].split(',')
        director = data_row['Director']
        # Add any new genre; associate the current movie with genre.
        for genre in parsed_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        # Add any new actor; associate the current movie with actor.
        for actor in parsed_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        # Add any new director; associate the current movie with director.
        if director not in directors.keys():
            directors[director] = list()
        directors[director].append(movie_key)

        # Create Movie object.
        movie = Movie(data_row['Title'], int(data_row['Year']), int(data_row['Rank']))
        movie.description = data_row['Description']
        movie.runtime_minutes = int(data_row['Runtime (Minutes)'])
        # Add the Movie to the repository.
        repo.add_movie(movie)

    # Create Genre objects, associate them with Movies and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_id in genres[genre_name]:
            movie = repo.get_movie(movie_id)
            make_genre_association(movie, genre)
        repo.add_genre(genre)
    # Create Actor objects, associate them with Movies and add them to the repository.
    for actor_name in actors.keys():
        actor = Actor(actor_name)
        for movie_id in actors[actor_name]:
            movie = repo.get_movie(movie_id)
            make_actor_association(movie, actor)
        repo.add_actor(actor)
    # Create Director objects, associate them with Movies and add them to the repository.
    for director_name in directors.keys():
        director = Director(director_name)
        for movie_id in directors[director_name]:
            movie = repo.get_movie(movie_id)
            make_director_association(movie, director)
        repo.add_director(director)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            user_name=data_row['username'],
            password=generate_password_hash(data_row['password'])
        )
        repo.add_user(user)
        users[data_row['id']] = user
    return users


def load_review(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'reviews.csv')):
        review = make_review(
            review_text=data_row['review-text'],
            user=users[data_row['author-id']],
            movie=repo.get_movie(int(data_row['movie-id'])),
            timestamp=datetime.fromisoformat(data_row['timestamp']),
            rating=int(data_row['rating'])
        )
        repo.add_review(review)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies and all other info relate to movie into the repository.
    load_movies_and_info(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load reviews into the repository.
    load_review(data_path, repo, users)
