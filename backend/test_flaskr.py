import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}@{}/{}".format('af', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for testing
        self.new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': '1'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO --> DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    ### pagination ###
    # paginated questions test
    def test_get_paginated_questions(self):
        # get response
        res = self.client().get('/questions')
        # load data
        data = json.loads(res.data)

        # status message and data retured correctly 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # valid page 404 test
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/question?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.!')
    
    ### get ###
     # get catogeries test
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    # get questions test
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    ### delete ###
    # delete question test
    def test_delete_question(self):
       question = Question.query.order_by(Question.id.desc()).first()
       question_id = question.id

       res = self.client().delete('/questions/{}'.format(question_id))
       data = json.loads(res.data)

       question = Question.query.get(question_id)

       self.assertEqual(res.status_code, 200)
       self.assertEqual(data['success'], True)
       self.assertEqual(data['deleted'], question_id)
       self.assertIsNone(question)
    
    # delete question 422 test
    def test_422_delete_question(self):
        question_id = 500
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    ### create questions ###
    # craete question test
    def test_create_question(self):
        # create new question
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        # check if question has been created
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    # craete question 422 test
    def test_422_create_question(self):
        # create new question without data
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    ### search ###
    # search question test
    def test_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'what is'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # search question 404 test
    def test_404_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'abcdefg'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.!')

    ### questions by category ###
    # questions by category test
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # questions by category 422 test
    def test_422_get_questions_by_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    ### quiz ###
    # play quiz tset
    def test_play_quiz(self):
        category = Category.query.first()
        res = self.client().post(
            '/quizzes', json={"quiz_category": category.format()})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # play quiz 422 test
    def test_422_play_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()