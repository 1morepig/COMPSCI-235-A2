from typing import List, Iterable
from datetime import date, datetime
from movies_website.adapters.repository import AbstractRepository
from movies_website.domain.model import make_review, Movie, Review, Genre, Actor, Director


class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class InvalidRatingException(Exception):
    pass


def add_review(movie_id: int, review_text: str, username: str, repo: AbstractRepository, rating: int = 5):
    # Check that the movie exists.
    movie = repo.get_movie(movie_id)
    if movie is None:
        raise NonExistentArticleException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    if type(rating) is not int or not (1 <= rating <= 10):
        raise InvalidRatingException
    # Create comment.
    review = make_review(review_text, user, movie, rating, datetime.now())

    # Update the repository.
    repo.add_review(review)


def get_movie(movie_id: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentArticleException

    return movie_to_dict(movie)


def get_first_movie(repo: AbstractRepository):
    movie = repo.get_first_movie()

    return movie_to_dict(movie)


def get_last_movie(repo: AbstractRepository):
    movie = repo.get_last_movie()
    return movie_to_dict(movie)


def get_movies_by_year(year, repo: AbstractRepository):
    # Returns movies for the target year (empty if no matches), the year of the previous movie (might be null),
    # the year of the next movie (might be null)

    movies = repo.get_movie_by_year(target_year=year)

    movies_dto = list()
    prev_year = next_year = None

    if len(movies) > 0:
        prev_year = repo.get_year_of_previous_movie(movies[0])
        next_year = repo.get_year_of_next_movie(movies[0])

        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies)

    return movies_dto, prev_year, next_year


def get_movies_ids_for_genre(genre_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_genre(genre_name)

    return movie_ids


def get_movies_ids_for_actor(actor_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_actor(actor_name)

    return movie_ids


def get_movies_ids_for_director(director_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_director(director_name)

    return movie_ids


def get_movies_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movie_by_id(id_list)

    # Convert Movies to dictionary form.
    movies_as_dict = movies_to_dict(movies)

    return movies_as_dict


def get_reviews_for_movie(movie_id, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentArticleException

    return reviews_to_dict(movie.reviews)


def get_all_actors(search:str, repo: AbstractRepository):
    actors = repo.get_actor()

    searched_actors = list()
    if search is not None:
        for actor in actors:
            if search in actor.actor_full_name:
                searched_actors.append(actor)
        return actors_to_dict(searched_actors)
    else:
        return actors_to_dict(actors)


def get_all_genres(search:str, repo: AbstractRepository):
    genres = repo.get_genre()
    searched_genres = list()
    if search is not None:
        for genre in genres:
            if search in genre.genre_name:
                searched_genres.append(genre)
        return genres_to_dict(searched_genres)
    else:
        return genres_to_dict(genres)


def get_all_director(search:str, repo: AbstractRepository):
    directors = repo.get_director()
    searched_directors = list()
    if search is not None:
        for director in directors:
            if search in director.director_full_name:
                searched_directors.append(director)
        return directors_to_dict(searched_directors)
    else:
        return directors_to_dict(directors)
# ============================================
# Functions to convert model entities to dicts
# ============================================


def movie_to_dict(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'year': movie.release_year,
        'title': movie.title,
        'description': movie.description,
        'director': director_to_dict(movie.director),
        'actors': actors_to_dict(movie.actors),
        'reviews': reviews_to_dict(movie.reviews),
        'genres': genres_to_dict(movie.genres),
        'runtime_minutes': movie.runtime_minutes
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def review_to_dict(review: Review):
    review_dict = {
        'username': review.user.user_name,
        'movie_id': review.movie.id,
        'review_text': review.review_text,
        'timestamp': review.timestamp,
        'rating': review.rating
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.genre_name,
        'genre_linked_movie': [movie.id for movie in genre.movie_list]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


def actor_to_dict(actor: Actor):
    actor_dict = {
        'name': actor.actor_full_name,
        'actor_linked_movie': [movie.id for movie in actor.movie_list]
    }
    return actor_dict


def actors_to_dict(actors: Iterable[Actor]):
    return [actor_to_dict(actor) for actor in actors]


def director_to_dict(director: Director):
    director_dict = {
        'name': director.director_full_name,
        'director_linked_movie': [movie.id for movie in director.movie_list]
    }
    return director_dict


def directors_to_dict(directors: Iterable[Director]):
    return [director_to_dict(director) for director in directors]


# ============================================
# Functions to convert dicts to model entities
# ============================================


def dict_to_article(dict):
    movie = Movie(dict.title, dict.year, dict.id)
    # Note there's no comments or tags.
    return movie
