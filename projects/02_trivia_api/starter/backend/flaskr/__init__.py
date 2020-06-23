import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db,setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def get_category_list():
  categories = {}
  for category in Category.query.all():
      categories[category.id] = category.type
  return categories

def create_app(test_config=None):
  global app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resource={r'/api/*': {'origins': '*'}})


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                               'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                               'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
        categories = Category.query.all()

        if categories is None:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {
                category.id: category.type for category in categories
            },
            'total_categories': len(Category.query.all())
        })

    except Exception as error:
        raise error

    finally:
        db.session.close()


  '''
  @TODO: 
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
    questions_list = Question.query.all()
    paginated_questions = paginate_questions(request, questions_list)
    if len(paginated_questions) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(questions_list),
        'categories': get_category_list()
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 


  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
        question = Question.query.filter(Question.id ==
                                         question_id).one_or_none()

        if question is None:
            abort(422)

        question.delete()

        return jsonify({
            'success': True,
            'deleted': question_id,
            'total_questions': len(Question.query.all())
        })

    except Exception as error:
        raise error

    finally:
        db.session.close()

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
  def add_or_search_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = body.get('category', None)
      search = body.get('searchTerm', None)

      try:
          if search is not None:
              selection = Question.query.order_by(Question.id).filter(
                  Question.question.ilike(f'%{search}%'))
              current_questions = paginate_questions(request, selection)

              return jsonify({
                  'success': True,
                  'search_term': body['searchTerm'],
                  'questions': current_questions,
                  'total_matching_questions': len(selection.all()),
                  'total_questions': len(Question.query.all())
              }), 200

          else:
              if len(new_question) == 0 or len(new_answer) == 0:
                  abort(400)
              question = Question(question=new_question,
                                  answer=new_answer,
                                  difficulty=new_difficulty,
                                  category=new_category)
              question.insert()

              current_questions = paginate_questions(request, Question.query.
                                                     order_by(Question.id).
                                                     all())

              return jsonify({
                  'success': True,
                  'created_id': question.id,
                  'new_question': question.format(),
                  'questions': current_questions,
                  'total_questions': len(Question.query.all())
              }), 201

      except Exception as error:
          raise error

      finally:
          db.session.close()
  

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      category = Category.query.get(category_id)
      if not category:
          abort(404)
      questions = Question.query.filter(
      Question.category == str(category_id)).all()

      if not questions:
          abort(404)

      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(Question.query.all()),
        'total_in_category': len(questions),
        'current_category': category.format()
      })

    except Exception as error:
      raise error

    finally:
      db.session.close()


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
  def play_game():
    try:
      req = request.get_json()

      valid_categories = [0, 1, 2, 3, 4, 5, 6]
      if 'quiz_category' not in req or 'previous_questions' not in req:
          abort(400)


      questions = [question.format() for question in
                   Question.query.filter(Question.id.notin_(
                       req.get('previous_questions'))).all()]

      if req.get('quiz_category')['id'] != 0:
          questions = [question.format() for question in
                       Question.query.filter_by(category=req.get(
                           'quiz_category')['id']).filter(
                           Question.id.notin_(req.get(
                               'previous_questions'))).all()]

      if questions:
          next_question = random.choice(questions)
      else:
          next_question = None

      return jsonify({
          'success': True,
          'question': next_question
      })

    except Exception as error:
      raise error

    finally:
      db.session.close()

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": error.description
      }), 422

  @app.errorhandler(404)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": error.description
      }), 404


  return app 

if __name__ == "__main__":
  create_app()
  

    