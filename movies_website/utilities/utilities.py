from flask import Blueprint, request, render_template, redirect, url_for, session

import movies_website.adapters.repository as repo
import movies_website.utilities.services as services


# Configure Blueprint.
utilities_blueprint = Blueprint(
    'utilities_bp', __name__)


def get_genres_and_urls(search=None):
    genre_names = services.get_genre_names(repo.repo_instance)
    genre_urls = dict()
    if search is None:
        for genre_name in genre_names:
            genre_urls[genre_name] = url_for('movies_bp.movies_by_genre', genre=genre_name)
    else:
        for genre_name in genre_names:
            if search in genre_name:
                genre_urls[genre_name] = url_for('movies_bp.movies_by_genre', genre=genre_name)
    return genre_urls


def get_actors_and_urls(search=None):
    actor_names = services.get_actor_names(repo.repo_instance)
    actor_urls = dict()
    if search is None:
        for actor_name in actor_names:
            actor_urls[actor_name] = url_for('movies_bp.movies_by_actor', actor=actor_name)
    else:
        for actor_name in actor_names:
            if search in actor_name:
                actor_urls[actor_name] = url_for('movies_bp.movies_by_actor', actor=actor_name)
    return actor_urls


def get_directors_and_urls(search=None):
    director_names = services.get_director_names(repo.repo_instance)
    director_urls = dict()
    if search is None:
        for director_name in director_names:
            director_urls[director_name] = url_for('movies_bp.movies_by_director', director=director_name)
    else:
        for director_name in director_names:
            if search in director_name:
                director_urls[director_name] = url_for('movies_bp.movies_by_director', director=director_name)
    return director_urls


def get_selected_movies(quantity=3):
    movies = services.get_random_movies(quantity, repo.repo_instance)

    for movie in movies:
        movie['hyperlink'] = url_for('movies_bp.movies_by_release_year', year=movie['year'])
    return movies
