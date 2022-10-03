from flask import Blueprint, request, jsonify
from app.db import get_movie, get_movies, get_movies_by_country, \
    get_movies_faceted, add_comment, update_comment, delete_comment

from flask_cors import CORS
from app.api.utils import expect
from datetime import datetime


auth = Blueprint(
    'movies_api_v1', 'movies_api_v1', url_prefix='/api/v1/movies')

CORS(auth)


@auth.route('/', methods=['GET'])
def api_get_movies():
    MOVIES_PER_PAGE = 20

    (movies, total_num_entries) = get_movies(
        None, page=0, movies_per_page=MOVIES_PER_PAGE)

    response = {
        "movies": movies,
        "page": 0,
        "filters": {},
        "entries_per_page": MOVIES_PER_PAGE,
        "total_results": total_num_entries,
    }

    return jsonify(response)


@auth.route('/search', methods=['GET'])
def api_search_movies():
    DEFAULT_MOVIES_PER_PAGE = 20

    # first determine the page of the movies to collect
    try:
        page = int(request.args.get('page', 0))
    except (TypeError, ValueError) as e:
        print('Got bad value:\t', e)
        page = 0

    # determine the filters
    filters = {}
    return_filters = {}
    cast = request.args.getlist('cast')
    genre = request.args.getlist('genre')
    if cast:
        filters["cast"] = cast
        return_filters["cast"] = cast
    if genre:
        filters["genres"] = genre
        return_filters["genre"] = genre
    search = request.args.get('text')
    if search:
        filters["text"] = search
        return_filters["search"] = search

    # finally use the database and get what is necessary
    (movies, total_num_entries) = get_movies(
        filters, page, DEFAULT_MOVIES_PER_PAGE)

    response = {
        "movies": movies,
        "page": page,
        "filters": return_filters,
        "entries_per_page": DEFAULT_MOVIES_PER_PAGE,
        "total_results": total_num_entries
    }

    return jsonify(response), 200


@auth.route('/id/<id>', methods=['GET'])
def api_get_movie_by_id(id):
    movie = get_movie(id)
    if movie is None:
        return jsonify({
            "error": "Not found"
        }), 400
    elif movie == {}:
        return jsonify({
            "error": "uncaught general exception"
        }), 400
    else:
        updated_type = str(type(movie.get('lastupdated')))
        return jsonify(
            {
                "movie": movie,
                "updated_type": updated_type
            }
        ), 200


@auth.route('/countries', methods=['GET'])
def api_get_movies_by_country():
    try:
        countries = request.args.getlist('countries')
        results = get_movies_by_country(countries)
        response_object = {
            "titles": results
        }
        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            "error": str(e)
        }
        return jsonify(response_object), 400


@auth.route('/facet-search', methods=['GET'])
def api_search_movies_faceted():
    MOVIES_PER_PAGE = 20

    # first determine the page of the movies to collect
    try:
        page = int(request.args.get('page', 0))
    except (TypeError, ValueError) as e:
        print('Got bad value for page, defaulting to 0:\t', e)
        page = 0

    # determine the filters
    filters = {}
    return_filters = {}
    cast = request.args.getlist('cast')
    if cast:
        filters["cast"] = cast
        return_filters["cast"] = cast
    if not filters:
        return api_search_movies()

    # finally use the database and get what is necessary
    try:
        (movies, total_num_entries) = get_movies_faceted(
            filters, page, MOVIES_PER_PAGE)

        response = {
            "movies": movies.get('movies'),
            "facets":  {
                "runtime": movies.get('runtime'),
                "rating": movies.get('rating')
            },
            "page": page,
            "filters": return_filters,
            "entries_per_page": MOVIES_PER_PAGE,
            "total_results": total_num_entries,
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth.route('/comment', methods=["POST"])
#@jwt_required
def api_post_comment():
    """
    Posts a comment about a specific movie. Validates the user is logged in by
    ensuring a valid JWT is provided
    """
    #claims = get_jwt_claims()
    #user = User.from_claims(claims)
    post_data = request.get_json()
    try:
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        comment = expect(post_data.get('comment'), str, 'comment')
        add_comment(movie_id, user, comment, datetime.now())
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({"comments": updated_comments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth.route('/comment', methods=["PUT"])
#@jwt_required
def api_update_comment():
    """
    Updates a user comment. Validates the user is logged in by ensuring a
    valid JWT is provided
    """
#    claims = get_jwt_claims()
    user_email = "jane.doe@example.com"
    post_data = request.get_json()
    try:
        comment_id = expect(post_data.get('comment_id'), str, 'comment_id')
        updated_comment = expect(post_data.get(
            'updated_comment'), str, 'updated_comment')
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        edit_result = update_comment(
            comment_id, user_email, updated_comment, datetime.now()
        )
        if edit_result.modified_count == 0:
            raise ValueError("no document updated")
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({"comments": updated_comments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth.route('/comment', methods=["DELETE"])
#@jwt_required
def api_delete_comment():
    """
    Delete a comment. Requires a valid JWT
    """
#    claims = get_jwt_claims()
    user_email = "jane.doe@example.com"
    post_data = request.get_json()
    try:
        comment_id = expect(post_data.get('comment_id'), str, 'comment_id')
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        delete_comment(comment_id, user_email)
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({'comments': updated_comments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400