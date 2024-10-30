from flask import request
from flask_restx import Api, Resource, fields, Namespace
from models import db, User, Subject, Grade

# Restful API setup
api = Api(version='1.0', title='Academics API', description='A simple API for Users, Subjects, and Grades')

# --------- NAMESPACES AND ROUTES --------- #
# Initialize Namespaces
ns_users = Namespace('users', description='User operations')
ns_subjects = Namespace('subjects', description='Subject operations')
ns_grades = Namespace('grades', description='Grade operations')

# -------- SERIALIZATION MODELS -------- #
user_model = ns_users.model('User', {
    'id': fields.String(required=True, description='User unique identifier'),
    'role': fields.String(required=True, description='User role'),
    'name': fields.String(required=True, description='User name'),
    'department': fields.String(description='User department'),
    'admission_year': fields.Integer(required=True, description='Admission year'),
    'password_hash': fields.String(required=True, description='Password hash')
})

subject_model = ns_subjects.model('Subject', {
    'code': fields.String(required=True, description='Subject code'),
    'name': fields.String(required=True, description='Subject name'),
    'credits': fields.Integer(required=True, description='Number of credits'),
    'professor_id': fields.String(description='Professor ID')
})

grade_model = ns_grades.model('Grade', {
    'id': fields.Integer(readonly=True, description='Grade ID'),
    'student_id': fields.String(required=True, description='Student ID'),
    'subject_code': fields.String(required=True, description='Subject code'),
    'semester': fields.String(description='Semester'),
    'score': fields.Float(description='Score received'),
    'grade': fields.String(description='Grade received')
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
