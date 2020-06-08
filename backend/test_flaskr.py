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
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:14231423az@localhost:5432/api"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['questions']), 10)
        self.assertLessEqual(data['totalQuestions'], 30)
        self.assertGreater(data['totalQuestions'], 20)

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=55')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['totalQuestions'], 0)

    def test_delete_question(self):
        res = self.client().delete('/questions/55')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], 'deleted')
    
    def test_500_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['question'], 'not deleted')

    def test_create_question(self):
        res = self.client().post('/questions', json={'question':'test', 'answer':'test', 'difficulty':3, 'category':1}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['done'], 'yes')

    def test_500_create_question(self):
        res = self.client().post('/questions', json={'question':'test', 'answer':'test', 'difficulty':6, 'category':1}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertTrue(data['done'])

    def test_search(self):
        res = self.client().post('/searchForQuestions', json={'searchTerm':'title'}) 
        data = json.loads(res.data)
        print(data['questions'][0])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 1)
       
    def test_404_search(self):
        res = self.client().post('/searchForQuestions', json={'searchTerm':'qwertyu'}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['totalQuestions'], 0)

    def test_questionsCategory(self):
        res = self.client().get('/categories/1/questions') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertGreater(data['totalQuestions'], 0)

    def test_500_questionsCategory(self):
        res = self.client().get('/categories/5/questions') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['error'], 'server problem')
    
    def test_categoryQuestions(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category':{'id':1}}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['answer'], 'adsfg')
        self.assertNotEqual(data['question']['answer'], 'aaaa')

    def test_500_categoryQuestions(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category':{'id':3}}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 'there is no questions')


    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()