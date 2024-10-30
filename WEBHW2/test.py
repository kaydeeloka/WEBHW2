from flask import Flask, render_template, request, redirect, url_for
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Subject, Grade  # Import models and db

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 실행 하기전
# Flask App Initialization
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_user:password@localhost/academic_records'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
# Restful API setup
api = Api(app, version='1.0', title='Academics API', description='A simple API for Users, Subjects, and Grades')

# --------- MODELS --------- #

# SQLAlchemy Model for User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(50), primary_key=True)  # Unique identifier
    role = db.Column(db.String(20), nullable=False)  # Role (student, professor, admin)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    admission_year = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# SQLAlchemy Model for Subject
class Subject(db.Model):
    __tablename__ = 'subjects'
    code = db.Column(db.String(10), primary_key=True)  # VARCHAR(10)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    professor_id = db.Column(db.String(10), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Subject {self.name}>'

# SQLAlchemy Model for Grade
class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # INT AUTO_INCREMENT
    student_id = db.Column(db.String(10), db.ForeignKey('user.id'))  # VARCHAR(10)
    subject_code = db.Column(db.String(10), db.ForeignKey('subject.code'))  # VARCHAR(10)
    semester = db.Column(db.String(6))  # VARCHAR(6)
    score = db.Column(db.Float)
    grade = db.Column(db.String(2))  # CHAR(2)

    def __repr__(self):
        return f'<Grade {self.grade} for Student {self.student_id}>'

# --------- NAMESPACES AND ROUTES --------- #

# RESTX Namespace for users
ns_users = api.namespace('users', description='User operations')
# Subject API namespace
ns_subjects = api.namespace('subjects', description='Subject operations')
# Grade API namespace
ns_grades = api.namespace('grades', description='Grade operations')


# --------- SERIALIZATION MODELS --------- #
# RESTX User Model for Serialization
user_model = ns_users.model('User', {
    'id': fields.String(required=True, description='The user unique identifier'),
    'role': fields.String(required=True, description='User role (student, professor, admin)'),
    'name': fields.String(required=True, description='The user name'),
    'department': fields.String(description='The user department'),
    'admission_year': fields.Integer(required=True, description='Admission year'),
    'password_hash': fields.String(required=True, description='Password hash')
})

# Create subject model for API serialization
subject_model = api.model('Subject', {
    'code': fields.String(required=True, description='The subject code'),
    'name': fields.String(required=True, description='The subject name'),
    'credits': fields.Integer(required=True, description='The number of credits'),
    'professor_id': fields.String(description='The ID of the professor')
})

# Create grade model for API serialization
grade_model = api.model('Grade', {
    'id': fields.Integer(readonly=True, description='The grade unique identifier'),
    'student_id': fields.String(required=True, description='The student ID'),
    'subject_code': fields.String(required=True, description='The subject code'),
    'semester': fields.String(description='The semester'),
    'score': fields.Float(description='The score received'),
    'grade': fields.String(description='The grade received')
})

# ---------USER ROUTES --------- #
# Routes with CRUD Operations
@ns_users.route('/')
class UserList(Resource):
    @ns_users.doc('list_users')
    @ns_users.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        users = User.query.all()
        return users  # Flask-RestX will handle the serialization with the user_model

    @ns_users.expect(user_model)
    @ns_users.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = request.json
        new_user = User(
            id=data['id'],
            role=data['role'],
            name=data['name'],
            department=data.get('department', ''),
            admission_year=data['admission_year'],
            password_hash=data['password_hash']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201

@ns_users.route('/<string:id>')
@ns_users.response(404, 'User not found')
class UserResource(Resource):
    @ns_users.marshal_with(user_model)
    def get(self, id):
        """Get a user by ID"""
        user = User.query.get_or_404(id)
        return user

    @ns_users.expect(user_model)
    @ns_users.marshal_with(user_model)
    def put(self, id):
        """Update a user by ID"""
        user = User.query.get_or_404(id)
        data = request.json

        user.role = data['role']
        user.name = data['name']
        user.department = data.get('department', user.department)
        user.admission_year = data['admission_year']
        user.password_hash = data['password_hash']

        db.session.commit()
        return user

    @ns_users.response(204, 'User deleted')
    def delete(self, id):
        """Delete a user by ID"""
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

# ---------SUBJECTS ROUTES --------- #
@ns_subjects.route('/')
class SubjectList(Resource):
    @ns_subjects.doc('list_subjects')
    @ns_subjects.marshal_list_with(subject_model)
    def get(self):
        '''List all subjects'''
        return Subject.query.all()

    @ns_subjects.doc('create_subject')
    @ns_subjects.expect(subject_model)
    @ns_subjects.marshal_with(subject_model, code=201)
    def post(self):
        '''Create a new subject'''
        data = request.json
        new_subject = Subject(**data)
        db.session.add(new_subject)
        db.session.commit()
        return new_subject, 201

@ns_subjects.route('/<string:code>')
@ns_subjects.response(404, 'Subject not found')
@ns_subjects.param('code', 'The subject code')
class SubjectResource(Resource):
    @ns_subjects.doc('get_subject')
    @ns_subjects.marshal_with(subject_model)
    def get(self, code):
        '''Fetch a subject given its code'''
        subject = Subject.query.get_or_404(code)
        return subject

    @ns_subjects.doc('delete_subject')
    @ns_subjects.response(204, 'Subject deleted')
    def delete(self, code):
        '''Delete a subject given its code'''
        subject = Subject.query.get_or_404(code)
        db.session.delete(subject)
        db.session.commit()
        return '', 204

    @ns_subjects.expect(subject_model)
    @ns_subjects.marshal_with(subject_model)
    def put(self, code):
        '''Update a subject given its code'''
        subject = Subject.query.get_or_404(code)
        data = request.json
        for key, value in data.items():
            setattr(subject, key, value)
        db.session.commit()
        return subject

# ---------GRADE ROUTES --------- #
@ns_grades.route('/')
class GradeList(Resource):
    @ns_grades.doc('list_grades')
    @ns_grades.marshal_list_with(grade_model)
    def get(self):
        '''List all grades'''
        return Grade.query.all()

    @ns_grades.doc('create_grade')
    @ns_grades.expect(grade_model)
    @ns_grades.marshal_with(grade_model, code=201)
    def post(self):
        '''Create a new grade'''
        data = request.json
        new_grade = Grade(**data)
        db.session.add(new_grade)
        db.session.commit()
        return new_grade, 201

@ns_grades.route('/<int:id>')
@ns_grades.response(404, 'Grade not found')
@ns_grades.param('id', 'The grade identifier')
class GradeResource(Resource):
    @ns_grades.doc('get_grade')
    @ns_grades.marshal_with(grade_model)
    def get(self, id):
        '''Fetch a grade given its identifier'''
        grade = Grade.query.get_or_404(id)
        return grade

    @ns_grades.doc('delete_grade')
    @ns_grades.response(204, 'Grade deleted')
    def delete(self, id):
        '''Delete a grade given its identifier'''
        grade = Grade.query.get_or_404(id)
        db.session.delete(grade)
        db.session.commit()
        return '', 204

    @ns_grades.expect(grade_model)
    @ns_grades.marshal_with(grade_model)
    def put(self, id):
        '''Update a grade given its identifier'''
        grade = Grade.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            setattr(grade, key, value)
        db.session.commit()
        return grade


# Register namespace with the API
api.add_namespace(ns_users)
api.add_namespace(ns_subjects)
api.add_namespace(ns_grades)

# Initialize the Database
with app.app_context():
    db.create_all()  # Create database tables if they don't exist
        
#error handling
@app.errorhandler(Exception)
def handle_exception(e):
    return {"error": str(e)}, 500

# Web Frontend Route
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    # Redirect based on role
    if role == 'Student':
        return redirect(url_for('student_dashboard'))  # Redirect to student page
    elif role == 'Professor':
        return redirect(url_for('professor_dashboard'))  # Redirect to professor page
    elif role == 'Admin':
        return redirect(url_for('admin_dashboard'))  # Redirect to admin page
    else:
        return redirect(url_for('login'))  # Back to login if something went wrong
    
@app.route('/student')
def student_dashboard():
    return render_template('student.html')

@app.route('/professor')
def professor_dashboard():
    return render_template('professor.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

# Run the App
if __name__ == '__main__':
    app.run(debug=True)