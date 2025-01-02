from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(99), nullable=False)
    email = db.Column(db.String(99), unique=True, nullable=False)
    role = db.Column(db.String(49), nullable=False)  # Employee, Innovation Manager, System Admin
    region = db.Column(db.String(49))
    password_hash = db.Column(db.String(127), nullable=False)  # Hash to store the password
    ideas = db.relationship('Idea', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# Idea Model
class Idea(db.Model):
    __tablename__ = 'ideas'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(199), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(49), default='pending')  # Submitted, Approved, Rejected
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    votes = db.relationship('Vote', backref='idea', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='idea', lazy='dynamic')
    resources = db.relationship('Resource', backref='idea', lazy='dynamic')

# Vote Model
class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    vote_type = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Feedback Model
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    content = db.Column(db.String(499), nullable=False)  # Feedback Rule
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Feedback Model
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    content = db.Column(db.String(499), nullable=False)  # Feedback Rule
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 
# Resource Model
class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    resource_type = db.Column(db.String(99), nullable=False)  # Budget, Staff, Tools
    allocated_amount = db.Column(db.Float, nullable=False)

# Incentive Model
class Incentive(db.Model):
    __tablename__ = 'incentives'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # Points-based incentive program
    reason = db.Column(db.String(200))  # Reason for the reward
    created_at = db.Column(db.DateTime, server_default=db.func.now())
