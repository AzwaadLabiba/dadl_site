# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ============================================================================
# Authentication Model (Separate from data models!)
# ============================================================================
class AdminUser(db.Model, UserMixin):
    """Admin user for authentication - separate from Professor data"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Administrator')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'

# ============================================================================
# Data Models (No authentication mixed in!)
# ============================================================================
class Professor(db.Model):
    """Professor profile - pure data model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False, default='Professor')
    bio = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    office = db.Column(db.String(100), nullable=True)
    office_hours = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Social/Academic Links
    google_scholar = db.Column(db.String(200), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    orcid = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Professor {self.name}>'

class Student(db.Model):
    """Student information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    degree_type = db.Column(db.String(20), nullable=False)  # 'PhD', 'Masters'
    research_focus = db.Column(db.Text, nullable=True)
    school = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    
    # Current vs Previous
    is_current = db.Column(db.Boolean, default=True)
    
    # For previous students
    thesis_title = db.Column(db.String(500), nullable=True)
    current_work = db.Column(db.String(200), nullable=True)
    
    # Links
    linkedin = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    google_scholar = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.name}>'

# Association table for project members
project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class Project(db.Model):
    """Research project information"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    overview = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Ongoing')
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    
    image1 = db.Column(db.String(200), nullable=True)
    image2 = db.Column(db.String(200), nullable=True)
    image3 = db.Column(db.String(200), nullable=True)
    image4 = db.Column(db.String(200), nullable=True)
    
    # Relationships
    members = db.relationship('Student', secondary=project_members, backref='projects')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

class Publication(db.Model):
    """Publication information"""
    id = db.Column(db.Integer, primary_key=True)
    bibtex = db.Column(db.Text, nullable=False)  # Store the entire BibTeX entry
    
    # Parsed fields (auto-populated from BibTeX)
    title = db.Column(db.String(500), nullable=True)
    authors = db.Column(db.String(500), nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Additional fields
    url = db.Column(db.String(500), nullable=True)
    google_scholar_url = db.Column(db.String(500), nullable=True)
    citations = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def parse_bibtex(self):
        """Parse BibTeX and populate fields"""
        try:
            import bibtexparser
            bib_db = bibtexparser.loads(self.bibtex)
            if bib_db.entries:
                entry = bib_db.entries[0]
                self.title = entry.get('title', '').replace('{', '').replace('}', '')
                self.authors = entry.get('author', '')
                self.venue = entry.get('booktitle') or entry.get('journal', '')
                self.year = int(entry.get('year', 0)) if entry.get('year') else None
                self.url = entry.get('url', '')
        except Exception as e:
            print(f"Error parsing BibTeX: {e}")

    def __repr__(self):
        return f'<Publication {self.title}>'

class LabInfo(db.Model):
    """Lab general information"""
    id = db.Column(db.Integer, primary_key=True)
    lab_name = db.Column(db.String(200), default='DADL Lab')
    lab_full_name = db.Column(db.String(200), default='Data Analysis and Deep Learning Laboratory')
    # focus_statement = db.Column(db.Text, nullable=True)
    mission = db.Column(db.Text, nullable=True)
    research_areas = db.Column(db.Text, nullable=True)
    
    # Contact Info
    lab_email = db.Column(db.String(120), nullable=True)
    lab_address = db.Column(db.Text, nullable=True)
    lab_phone = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<LabInfo {self.lab_name}>'