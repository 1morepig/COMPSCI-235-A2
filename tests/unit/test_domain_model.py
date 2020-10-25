from datetime import date

from movies_website.domain.model import User, Movie, Genre, make_review, make_genre_association, ModelException

import pytest
from datetime import date, datetime

@pytest.fixture()
def movie():
    movie = Movie("the movie", 2016)
    movie.description = "good movie"
    return movie


@pytest.fixture()
def user():
    return User('pig', '1234567890')


@pytest.fixture()
def genre():
    return Genre('Action')


def test_user_construction(user):
    assert user.user_name == 'pig'
    assert user.password == '1234567890'
    assert repr(user) == '<User pig 1234567890>'

    for review in user.reviews:
        # User should have an empty list of reviews after construction.
        assert False


def test_movie_construction(movie):
    assert movie.id is None
    assert movie.release_year == 2016
    assert movie.title == 'the movie'
    assert movie.description == 'good movie'
    assert len(movie.reviews) == 0
    assert len(movie.genres) == 0

    assert repr(
        movie) == '<Movie the movie, 2016>'


def test_movie_less_than_operator():
    movie_1 = Movie(
        "movie1", 2008
    )

    movie_2 = Movie(
        "movie2", 2009
    )

    assert movie_1 < movie_2


def test_genre_construction(genre):
    assert genre.genre_name == 'Action'

    for movie in genre.movie_list:
        assert False

    assert not genre.is_applied_to(Movie(None, 2016))


def test_make_review_establishes_relationships(movie, user):
    review_text = 'this movie is good'
    review = make_review(user=user, movie=movie, review_text=review_text, rating=7, timestamp=datetime.now())

    # Check that the User object knows about the Review.
    assert review in user.reviews

    # Check that the Review knows about the User.
    assert review.user is user

    # Check that Movie knows about the Review.
    assert review in movie.reviews

    # Check that the Review knows about the Movie.
    assert review.movie is movie


def test_make_genre_associations(movie, genre):
    make_genre_association(movie, genre)

    # check that the Genre knows about the Movie.
    assert genre.is_applied_to(movie)


def test_make_genre_associations_with_movie_already_tagged(movie, genre):
    make_genre_association(movie, genre)

    with pytest.raises(ModelException):
        make_genre_association(movie, genre)
