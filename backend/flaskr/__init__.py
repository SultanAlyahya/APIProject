import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={r"/*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        print(formatted_categories)

        return jsonify({'categories': formatted_categories})

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the
   screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        numberOfQ = (int(request.args.get('page', 1, type=int)))*10
        questions = Question.query.all()
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        if len(questions[numberOfQ-10:numberOfQ]) == 0:
            print(len(questions))
            return jsonify({'totalQuestions': 0}), 404

        formatted_questions = [question.format() for question in questions]
        print(formatted_questions[numberOfQ-10:numberOfQ])

        return jsonify({
            'questions': formatted_questions[numberOfQ-10:numberOfQ],
            'totalQuestions': len(formatted_questions),
            'categories': formatted_categories,
            'currentCategory': formatted_categories[0]
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question,
   the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        try:
            Question.query.get(id).delete()
            return jsonify({'question': 'deleted'}), 200
        except Exception:
            return jsonify({'question': 'not deleted'}), 500

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def create_question():

        try:
            if request.get_json()['difficulty'] > 5:
                return jsonify({'done': 'the difficulty is so high'}), 500
            else:
                Question(question=request.get_json()['question'],
                         answer=request.get_json()['answer'],
                         difficulty=request.get_json()['difficulty'],
                         category=request.get_json()['category']).insert()
                return jsonify({'done': 'yes'}), 201
        except Exception:
            return jsonify({'done': 'no'}), 500

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    @app.route('/searchForQuestions', methods=['POST'])
    def search():
        try:
            questions = Question.query.filter(Question.question.like(
                "%" + (request.get_json()['searchTerm'] + "%"))).all()
            if len(questions) == 0:
                return jsonify({'totalQuestions': 0}), 404
            else:
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({
                    'questions': formatted_questions,
                    'totalQuestions': len(formatted_questions),
                    'currentCategory': 'yes'
                })
        except Exception:
            print(sys.exc_info())
            return jsonify({'totalQuestions': 0}), 500

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<id>/questions', methods=['GET'])
    def questionsCategory(id):
        try:
            questions = Question.query.filter_by(category=id)
            formatted_questions = [question.format() for question in questions]
            category = Category.query.get(id)
            cate = category.format()
            print(cate)
            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': cate
            })
        except Exception:
            return jsonify({'error': 'server problem'}), 500

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def categoryQuestions():
        try:
            questions = Question.query.filter_by(
                category=str(request.get_json()['quiz_category']['id']))

            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0:
                return jsonify({'error': 'there is no questions'}), 404

            last = request.get_json()['previous_questions']

            for question in formatted_questions:
                if question['id'] not in last:
                    print(question)
                    return jsonify({'question': question}), 200
            return ('', 204)
        except Exception:
            return jsonify({'error': 'server problem'}), 500

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found_error(error):
        return 'api not found', 404

    @app.errorhandler(422)
    def server_error(error):
        return 'you reach Unprocessable api', 422

    return app
