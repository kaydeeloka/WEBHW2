from flask import Flask, session, request, redirect, url_for, jsonify,render_template
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from models import db, User, Subject, Grade, Student  # Import models and db
from api_routes import  api # Import API routes
from werkzeug.security import generate_password_hash
import traceback,os  # To log detailed error information

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 실행 하기전
# Flask App Initialization
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_user:password@localhost/academic_records'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set the secret key for the app (this key is used for session management)
app.secret_key = os.urandom(24)  # Generates a secure random key
# Set the secret key for JWT (must be kept confidential)
app.config['JWT_SECRET_KEY'] = os.urandom(24) # Change this to a secure key
# Initialize JWTManager with the Flask app
jwt = JWTManager(app)

# Initialize the database with the Flask app
db.init_app(app)

# Register the API with the Flask app
api.init_app(app)

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
    return render_template('login.html')

# ---------REGISTER NEW USER --------- #
@app.route('/register', methods=['POST'])
def register():
    """Create a new user"""
    data = request.json  # This should contain the JSON data sent in the request
    
    if not data:
        return {'error': 'No data provided'}, 400  # Handle case where no data is sent

    # Validate required fields
    required_fields = ['id', 'role', 'name', 'admission_year']
    for field in required_fields:
        if field not in data or data[field] is None:
            return {'error': f'Missing required field: {field}'}, 400

    # Check for valid role
    if data['role'] not in ['Student', 'Professor', 'Admin']:
        return {'error': 'Invalid role specified'}, 400

    # Create the password hash (fixed for demonstration purposes)
    password_hash = generate_password_hash('1234')  # Fixed password for all new users

    # Create the new user object
    new_user = User(
        id=data['id'],
        role=data['role'],
        name=data['name'],
        department=data.get('department', ''),
        admission_year=data['admission_year'],
        password_hash=password_hash
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Convert the user object to a dictionary
        user_data = {
            'id': new_user.id,
            'role': new_user.role,
            'name': new_user.name,
            'department': new_user.department,
            'admission_year': new_user.admission_year,
            # Do not include password_hash for security reasons
        }
        
        return {
            'message': 'User registered successfully!',
            'user': user_data  # Return the dictionary representation of the user
        }, 201
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

# ---------LOGIN USER --------- #
# Fixed password for all users
FIXED_PASSWORD = '1234'

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form
        user_id = data.get('id')  # This should be the ID
        password = data.get('password')
        role = data.get('role')

        if not user_id or not password or not role:
            return jsonify({'error': 'All fields are required.'}), 400

        user = User.query.filter_by(id=user_id).first()  # Fetch user by ID

        # Check if the user exists
        if not user:
            return jsonify({'error': 'User not found.'}), 404

        # Verify the fixed password for all users
        if password != FIXED_PASSWORD:
            return jsonify({'error': 'Invalid password.'}), 401

        # Verify the user role
        if user.role.lower() != role.lower():
            return jsonify({'error': f'Invalid role. You are not {role}.'}), 403

        # If all checks pass, create JWT tokens
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        refresh_token = create_refresh_token(identity={'id': user.id, 'role': user.role})

        # Store user ID in session based on role
        session['user_id'] = user.id  # Store user ID in session

        # Return the tokens and user info
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'role': user.role,
            'user_id': user.id  # Return user ID for frontend access
        }), 200

    except Exception as e:
        print("ERROR: An exception occurred during login.")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during login.', 'message': str(e)}), 500

# Routes for subject CRUD operations
@app.route('/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if request.method == 'GET':
        subjects = Subject.query.all()
        return jsonify([{
            'id': s.id,
            'code': s.code,
            'name': s.name,
            'credits': s.credits,
            'professor_id': s.professor_id
        } for s in subjects])

    if request.method == 'POST':
        data = request.json
        new_subject = Subject(
            code=data['code'],
            name=data['name'],
            credits=data['credits'],
            professor_id=data['professor_id']
        )
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'message': 'Subject added successfully!'}), 201

@app.route('/subjects/<int:id>', methods=['PUT', 'DELETE'])
def modify_subject(id):
    subject = Subject.query.get_or_404(id)

    if request.method == 'PUT':
        data = request.json
        subject.code = data['code']
        subject.name = data['name']
        subject.credits = data['credits']
        subject.professor_id = data['professor_id']
        db.session.commit()
        return jsonify({'message': 'Subject updated successfully!'})

    if request.method == 'DELETE':
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully!'})

@app.route('/subject/<int:id>', methods=['GET'])
def get_subject(id):
    subject = Subject.query.get_or_404(id)
    return jsonify({
        'id': subject.id,
        'code': subject.code,
        'name': subject.name,
        'professor_id': subject.professor_id,
        'credits': subject.credits
    })

@app.route('/student')
def student_dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    grades = Grade.query.filter_by(student_id=user_id).all()  # Fetch grades for the logged-in student

    return render_template('student.html',user=user, grades=grades)

# Fetch all students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': s.id, 'name': s.name, 'department': s.department, 
        'admission_year': s.admission_year
    } for s in students])

# Add a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    student = Student(
        name=data['name'], department=data['department'], 
        admission_year=data['admission_year']
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully'})

# Delete a student by ID
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'})
    return jsonify({'error': 'Student not found'}), 404

# Routes for managing grades
@app.route('/grades', methods=['GET', 'POST'])
def manage_grades():
    if request.method == 'GET':
        grades = Grade.query.all()
        return jsonify([{
            'id': g.id,
            'student_id': g.student_id,
            'subject_code': g.subject_code,
            'semester': g.semester,
            'grade': g.grade,
            'score': g.score
        } for g in grades])
    elif request.method == 'POST':
        data = request.json
        new_grade = Grade(
            student_id=data['student_id'],
            subject_code=data['subject_code'],
            semester=data['semester'],
            grade=data['grade'],
            score=data['score']
        )
        db.session.add(new_grade)
        db.session.commit()
        return jsonify({'message': 'Grade added successfully'})

@app.route('/grades/filtered', methods=['GET'])
def get_filtered_grades():
    professor_id = request.args.get('professor_id')  # Get professor_id from query params
    # Step 1: Fetch all subjects taught by this professor
    subjects = Subject.query.filter_by(professor_id=professor_id).all()
    subject_codes = [subject.code for subject in subjects]
    # Step 2: Filter grades by the subject codes
    grades = Grade.query.filter(Grade.subject_code.in_(subject_codes)).all()
    # Step 3: Return the filtered grades
    return jsonify([{
        'id': g.id,
        'student_id': g.student_id,
        'subject_code': g.subject_code,
        'semester': g.semester,
        'grade': g.grade,
        'score': g.score
    } for g in grades])

# Add a new grade
@app.route('/grades', methods=['POST'])
def add_grade():
    data = request.json
    grade = Grade(
        student_id=data['student_id'],
        subject_code=data['subject_code'],
        semester=data['semester'],
        grade=data['grade'],
        score=data['score']
    )
    db.session.add(grade)
    db.session.commit()
    return jsonify({'message': 'Grade added successfully'})

# Delete a grade by ID
@app.route('/grades/<int:id>', methods=['DELETE'])
def delete_grade(id):
    grade = Grade.query.get(id)
    if grade:
        db.session.delete(grade)
        db.session.commit()
        return jsonify({'message': 'Grade deleted successfully'})
    return jsonify({'error': 'Grade not found'}), 404

@app.route('/professor')
def professor_dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('index'))
    
    # Fetch user (professor) details
    user = User.query.get(user_id)
    
  # Fetch all subjects taught by the logged-in professor
    subjects = Subject.query.filter_by(professor_id=user_id).all()

    # Extract subject codes from the subjects
    subject_codes = [subject.code for subject in subjects]

    # Query grades for those subject codes
    grades = Grade.query.filter(Grade.subject_code.in_(subject_codes)).all()

    return render_template('professor.html', user=user, subjects=subjects, grades=grades)

@app.route('/admin')
def admin_dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('index'))
    
    # Fetch user (admin) details
    user = User.query.get(user_id)
    
    # Fetch all subjects
    subjects = Subject.query.all()
    
    # Fetch all grades
    grades = Grade.query.all()
    
    return render_template('admin.html', user=user, subjects=subjects, grades=grades)


# Run the App
if __name__ == '__main__':
    app.run(debug=True)