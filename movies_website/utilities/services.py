from typing import Iterable
import random

from movies_website.adapters.repository import AbstractRepository
from movies_website.domain.model import Movie


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genre()
    genre_names = [genre.genre_name for genre in genres]

    return genre_names


def get_actor_names(repo: AbstractRepository):
    actors = repo.get_actor()
    actor_names = [actor.actor_full_name for actor in actors]

    return actor_names


def get_director_names(repo: AbstractRepository):
    directors = repo.get_director()
    director_names = [director.director_full_name for director in directors]

    return director_names


def get_random_movies(quantity, repo: AbstractRepository):
    movie_count = repo.get_number_of_movie()

    if quantity >= movie_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of articles.
        quantity = movie_count - 1

    # Pick distinct and random articles.
    random_ids = random.sample(range(1, movie_count), quantity)
    movies = repo.get_movie_by_id(random_ids)

    return movies_to_dict(movies)


# ============================================
# Functions to convert dicts to model entities
# ============================================

def movie_to_dict(movie: Movie):
    movie_dict = {
        'year': movie.release_year,
        'title': movie.title,
        'description': movie.description,
        'director': movie.director,
        'actors': movie.actors,
        'genres': movie.genres,
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]
