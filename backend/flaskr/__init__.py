import os
from flask import Flask, request, abort, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# paginations
PAGINATION_SIZE = 10


def pagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * PAGINATION_SIZE
    end = start + PAGINATION_SIZE

    items = [item.format() for item in selection]
    current_items = items[start:end]

    return current_items


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
	@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs --> DONE
	'''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
	@TODO: Use the after_request decorator to set Access-Control-Allow --> DONE
	'''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headrs',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTION')
        return response

    '''
	@TODO: --> DONE
	Create an endpoint to handle GET requests 
	for all available categories.
	'''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # categories
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        # view
        return jsonify({
            "success": True,
            "categories": formatted_categories,
            "total_categories": len(formatted_categories)
        })

    '''
	@TODO: --> DONE
	Create an endpoint to handle GET requests for questions, 
	including pagination (every 10 questions). 
	This endpoint should return a list of questions, 
	number of total questions, current category, categories. 

	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions. 
	'''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # selection query(questions), and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = pagination(request, selection)

        # categories
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        # view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': formatted_categories
        })

    '''
	@TODO: --> DONE
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # query
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
                # delete question
            question.delete()
            # view
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    '''
	@TODO: --> DONE
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.  
	@TODO: --> Done
	Create a POST endpoint to get questions based on a search term. 
	It should return any questions for whom the search term 
	is a substring of the question. 

	TEST: Search by any phrase. The questions list will update to include 
	only question that include that string within their question. 
	Try using the word "title" to start. 
	'''
    @app.route('/questions', methods=['POST'])
    def create_search_questions():
        # loading request body
        body = request.get_json()

        # if search
        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            # selection query the database using search term
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            # no results found
            if (len(selection) == 0):
                abort(404)

            # paginate
            paginated = pagination(request, selection)

            # view
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })

        # else create a question
        else:
            # loading data from body
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            # check if any field is None
            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                # create question
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                # insert question
                question.insert()
                # selection query(questions) by id
                selection = Question.query.order_by(Question.id).all()
                # paginate
                current_questions = pagination(request, selection)

                # view
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)

    '''
	@TODO: --> DONE
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        # query(category) by id
        category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if (category is None):
            abort(422)

        # selection query
        selection = Question.query.filter_by(category=category.id).all()

        # paginate
        paginated = pagination(request, selection)

        # view
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    '''
	@TODO: --> DONE
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not. 
	'''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # loading request body
        body = request.get_json()

        if body == None or 'quiz_category' not in body.keys():
            return abort(422)

        previous_questions = []
        if 'previous_questions' in body.keys():
            previous_questions = body['previous_questions']
            # query
        question = Question.query.filter(
            Question.category == body['quiz_category']['id'], Question.id.notin_(previous_questions)).first()
        # view
        return jsonify({
            "success": True,
            "question": question.format() if question != None else None
        })

    '''
	@TODO: --> DONE
	Create error handlers for all expected errors 
	including 404 and 422. 
	'''
    # error handler 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found.!"
        }), 404

    # error handler 422
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
