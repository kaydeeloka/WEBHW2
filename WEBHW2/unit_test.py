import unittest
import json
from app import app, db, User, Subject, Grade

class TestUserAPI(unittest.TestCase):
    TEST_USER_ID = 'test_user'
    TEST_PROFESSOR_ID = 'professor_user'
    TEST_PASSWORD = '1234'
    TEST_ROLE_STUDENT = 'Student'
    TEST_ROLE_PROFESSOR = 'Professor'
    
    def setUp(self):
        """Create a test client and set up the application."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
        self.client = self.app.test_client()
        self.app.testing = True
        
        # Create the database tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_all_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        response = self.app.post('/users', json={'name': 'Test User'})
        self.assertEqual(response.status_code, 201)
        
    def register_user(self, user_id, role, name, admission_year):
        """Helper method to register a user."""
        return self.client.post('/register', json={
            'id': user_id,
            'role': role,
            'name': name,
            'admission_year': admission_year
        })

    def login_user(self, user_id, password, role):
        """Helper method to log in a user."""
        return self.client.post('/login', data={
            'id': user_id,
            'password': password,
            'role': role
        })

    def test_login_user(self):
        """Test user login with fixed password."""
        self.register_user(self.TEST_USER_ID, self.TEST_ROLE_STUDENT, 'Test User', 2022)
        response = self.login_user(self.TEST_USER_ID, self.TEST_PASSWORD, self.TEST_ROLE_STUDENT)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_login_user_invalid_credentials(self):
        """Test login with invalid credentials."""
        self.register_user(self.TEST_USER_ID, self.TEST_ROLE_STUDENT, 'Test User', 2022)
        response = self.login_user(self.TEST_USER_ID, 'wrong_password', self.TEST_ROLE_STUDENT)
        self.assertEqual(response.status_code, 401)  # Adjust based on your API design
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_add_subject(self):
        """Test adding a new subject."""
        self.register_user(self.TEST_PROFESSOR_ID, self.TEST_ROLE_PROFESSOR, 'Professor User', 2020)

        response = self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': self.TEST_PROFESSOR_ID  # Associate with a professor
        })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'CS101')
        self.assertEqual(data['name'], 'Introduction to Computer Science')

    def test_student_dashboard(self):
        """Test access to the student dashboard."""
        self.register_user('test_student', self.TEST_ROLE_STUDENT, 'Student User', 2022)
        self.login_user('test_student', self.TEST_PASSWORD, self.TEST_ROLE_STUDENT)
        
        response = self.client.get('/student')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student User', response.data)  # Check if student name is in the response

    def test_admin_dashboard(self):
        """Test access to the admin dashboard."""
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        
    def test_create_subject(self):
        """Test creating a new subject."""
        response = self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'CS101')
        self.assertEqual(data['name'], 'Introduction to Computer Science')

    def test_read_subject(self):
        """Test reading a subject."""
        # Create a subject first
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        response = self.client.get('/subjects/CS101')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'CS101')
        self.assertEqual(data['name'], 'Introduction to Computer Science')

    def test_update_subject(self):
        """Test updating a subject."""
        # Create a subject first
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        response = self.client.put('/subjects/CS101', json={
            'name': 'Intro to CS',
            'credits': 4
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Intro to CS')
        self.assertEqual(data['credits'], 4)

    def test_delete_subject(self):
        """Test deleting a subject."""
        # Create a subject first
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        response = self.client.delete('/subjects/CS101')
        self.assertEqual(response.status_code, 204)  # No content
        response = self.client.get('/subjects/CS101')
        self.assertEqual(response.status_code, 404)  # Not found

    def test_create_grade(self):
        """Test creating a new grade."""
        # Create a user and subject first
        self.client.post('/register', json={
            'id': 'student_user',
            'role': 'Student',
            'name': 'Student User',
            'admission_year': 2022
        })
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        response = self.client.post('/grades', json={
            'student_id': 'student_user',
            'subject_code': 'CS101',
            'grade': 85
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['grade'], 85)

    def test_read_grade(self):
        """Test reading a grade."""
        # Create a user, subject, and grade first
        self.client.post('/register', json={
            'id': 'student_user',
            'role': 'Student',
            'name': 'Student User',
            'admission_year': 2022
        })
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        self.client.post('/grades', json={
            'student_id': 'student_user',
            'subject_code': 'CS101',
            'grade': 85
        })
        response = self.client.get('/grades/student_user/CS101')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['grade'], 85)

    def test_update_grade(self):
        """Test updating a grade."""
        # Create a user, subject, and grade first
        self.client.post('/register', json={
            'id': 'student_user',
            'role': 'Student',
            'name': 'Student User',
            'admission_year': 2022
        })
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        self.client.post('/grades', json={
            'student_id': 'student_user',
            'subject_code': 'CS101',
            'grade': 85
        })
        response = self.client.put('/grades/student_user/CS101', json={
            'grade': 90
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['grade'], 90)

    def test_delete_grade(self):
        """Test deleting a grade."""
        # Create a user, subject, and grade first
        self.client.post('/register', json={
            'id': 'student_user',
            'role': 'Student',
            'name': 'Student User',
            'admission_year': 2022
        })
        self.client.post('/subjects', json={
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'credits': 3,
            'professor_id': 'professor_user'
        })
        self.client.post('/grades', json={
            'student_id': 'student_user',
            'subject_code': 'CS101',
            'grade': 85
        })
        response = self.client.delete('/grades/student_user/CS101')
        self.assertEqual(response.status_code, 204)  # No content
        response = self.client.get('/grades/student_user/CS101')
        self.assertEqual(response.status_code, 404)  # Not found

if __name__ == '__main__':
    unittest.main()
