from datetime import date, datetime
from typing import List

import pytest

from movies_website.domain.model import Movie, Director, Genre, Actor, User, Review, make_review
from movies_website.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_movies = in_memory_repo.get_number_of_movie()

    # Check that the query returned 6 Movies.
    assert number_of_movies == 3


def test_repository_can_add_movie(in_memory_repo):
    movie = Movie(
        "cool stuff",
        2014,
        3
    )
    in_memory_repo.add_movie(movie)

    assert in_memory_repo.get_movie(3) is movie


def test_repository_can_retrieve_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)

    # Check that the Movie has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Movie is reviewed as expected.
    review_one = movie.reviews[0]
    review_two = movie.reviews[1]

    assert review_one.user.user_name == 'fmercury'
    assert review_two.user.user_name == "thorke"

    # Check that the Movie is tagged as expected.
    assert movie.genres[0].genre_name == 'Action'
    assert movie.genres[1].genre_name == 'Adventure'


def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(101)
    assert movie is None


def test_repository_can_retrieve_movies_by_year(in_memory_repo):
    movies = in_memory_repo.get_movie_by_year(2014)

    # Check that the query returned 1 Movies.
    assert len(movies) == 1


def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_year(in_memory_repo):
    movies = in_memory_repo.get_movie_by_year(2019)
    assert len(movies) == 0


def test_repository_can_retrieve_genres(in_memory_repo):
    genres: List[Genre] = in_memory_repo.get_genre()

    assert len(genres) == 6

    genre_one = [genre for genre in genres if genre.genre_name == 'Action'][0]
    length = 0
    for i in genre_one.movie_list:
        length += 1
    assert length == 1


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == 'Prometheus'


def test_repository_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    assert movie.title == 'Split'


def test_repository_can_get_movies_by_ids(in_memory_repo):
    movies = in_memory_repo.get_movie_by_id([1, 2])

    assert len(movies) == 2
    assert movies[0].title == 'Guardians of the Galaxy'
    assert movies[1].title == "Prometheus"


def test_repository_does_not_retrieve_movie_for_non_existent_id(in_memory_repo):
    movies = in_memory_repo.get_movie_by_id([1, 9])

    assert len(movies) == 1
    assert movies[0].title == 'Guardians of the Galaxy'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    movies = in_memory_repo.get_movie_by_id([0, 9])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_director('James Gunn')

    assert movie_ids == [1]


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_genre('United States')

    assert len(movie_ids) == 0


def test_repository_returns_year_of_previous_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year == 2012


def test_repository_returns_none_when_there_are_no_previous_movies(in_memory_repo):
    movie = in_memory_repo.get_movie(1)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year == 2012


def test_repository_returns_year_of_next_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year == 2016


def test_repository_returns_none_when_there_are_no_subsequent_movies(in_memory_repo):
    movie = in_memory_repo.get_movie(3)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year is None


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre('Motoring')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genre()


def test_repository_can_get_all_director(in_memory_repo):
    director = Director('Pig 2')
    in_memory_repo.add_director(director)

    assert director == in_memory_repo.get_director()[2]


def test_repository_can_add_a_review(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    review = make_review("Trump's onto it!", user, movie, 9, datetime.today())

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_review()


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    review = Review(None, movie, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_an_movie_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    review = Review(None, movie, "Trump's onto it!", datetime.today())

    user.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Movie doesn't refer to the Review.
        in_memory_repo.add_review(review)


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_review()) == 3



