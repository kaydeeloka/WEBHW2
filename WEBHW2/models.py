from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance (to be initialized later with the app)
db = SQLAlchemy()

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

    student = db.relationship('Student', backref='user', uselist=False)  # One-to-one with Student
    
    def __repr__(self):
        return f'<User {self.name}>'

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)  # Link to User table

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.user.name,
            "department": self.user.department,
            "admission_year": self.user.admission_year,
        }
        
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
