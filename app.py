# app.py - Updated with file upload support
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_admin import Admin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from flask_migrate import Migrate

# Import models
from models import (
    db, AdminUser, Professor, Student, Project, 
    Publication, LabInfo
)

# Import enhanced admin views with file upload support
from admin_views import (
    MyAdminIndexView, ProfessorModelView, StudentModelView,
    ProjectModelView, PublicationModelView, LabInfoModelView
)

# ============================================================================
# 1. App Configuration
# ============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dadl_lab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directories if they don't exist
for folder in ['static/uploads/professor', 'static/uploads/students', 'static/uploads/projects']:
    os.makedirs(folder, exist_ok=True)
    # Create .gitkeep files to preserve empty directories
    gitkeep_path = os.path.join(folder, '.gitkeep')
    if not os.path.exists(gitkeep_path):
        open(gitkeep_path, 'a').close()

# Initialize database with app
db.init_app(app)
migrate = Migrate(app, db)

# ============================================================================
# 2. Flask-Login Setup
# ============================================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# ============================================================================
# 3. Setup Admin Panel with Enhanced Views
# ============================================================================
admin = Admin(
    app, 
    name='DADL Lab Admin', 
    template_mode='bootstrap4', 
    index_view=MyAdminIndexView()
)

# Add all model views with file upload support
admin.add_view(ProfessorModelView(Professor, db.session, name='Professor Profile'))
admin.add_view(StudentModelView(Student, db.session, name='Students'))
admin.add_view(ProjectModelView(Project, db.session, name='Projects'))
admin.add_view(PublicationModelView(Publication, db.session, name='Publications'))
admin.add_view(LabInfoModelView(LabInfo, db.session, name='Lab Information'))

# ============================================================================
# 4. Routes
# ============================================================================
@app.route('/')
def home():
    """Main website homepage"""
    lab_info = LabInfo.query.first()
    professor = Professor.query.first()
    
    # Students
    current_phd = Student.query.filter_by(is_current=True, degree_type='PhD').all()
    current_masters = Student.query.filter_by(is_current=True, degree_type='Masters').all()
    former_phd = Student.query.filter_by(is_current=False, degree_type='PhD').all()
    former_masters = Student.query.filter_by(is_current=False, degree_type='Masters').all()
    
    # Projects
    ongoing_projects = Project.query.filter_by(status='Ongoing').all()
    completed_projects = Project.query.filter_by(status='Completed').all()
    
    # Publications
    featured_publications = Publication.query.filter_by(is_featured=True).order_by(Publication.year.desc()).limit(5).all()
    
    return render_template('single_page.html',
                         lab_info=lab_info,
                         professor=professor,
                         current_phd=current_phd,
                         current_masters=current_masters,
                         former_phd=former_phd,
                         former_masters=former_masters,
                         ongoing_projects=ongoing_projects,
                         completed_projects=completed_projects,
                         featured_publications=featured_publications)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('admin_login.html')
        
        admin_user = AdminUser.query.filter_by(username=username).first()
        
        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            flash(f'Welcome back, {admin_user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
@login_required
def admin_logout():
    """Admin logout"""
    user_name = current_user.name
    logout_user()
    flash(f'Goodbye, {user_name}! You have been logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin-status')
def admin_status():
    """Check admin login status"""
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.name} (ID: {current_user.id})"
    else:
        return "Not logged in"

@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    additional_images = [img for img in [project.image2, project.image3, project.image4] if img]
    return render_template('project_detail.html', project=project, additional_images=additional_images)



# ============================================================================
# 5. Context Processor
# ============================================================================
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# ============================================================================
# 6. Database Initialization
# ============================================================================
def create_default_data():
    """Create default data if database is empty"""
    
    # Create default admin user
    if not AdminUser.query.first():
        admin = AdminUser(
            username='admin',
            name='Lab Administrator'
        )
        admin.set_password('changeme123')
        db.session.add(admin)
        print("Created default admin user - username: admin, password: changeme123")
    
    # Create default professor
    if not Professor.query.first():
        default_prof = Professor(
            name='Dr. John Smith',
            title='Professor and Lab Director',
            bio='Principal Investigator of the Data Analysis and Deep Learning Laboratory.',
            education='Ph.D. in Computer Science from MIT (2008)',
            experience='Professor at University (2015-present)',
            email='jsmith@university.edu',
            office='Room 301, Computer Science Building',
            office_hours='Mon/Wed 2-4 PM',
            google_scholar='https://scholar.google.com/citations?user=XXXXXXX',
            linkedin='https://linkedin.com/in/drjohnsmith',
            website='https://www.example-university.edu/~jsmith'
        )
        db.session.add(default_prof)
        print("Created default professor profile")
    
    # Create default lab info
    if not LabInfo.query.first():
        lab_info = LabInfo(
            lab_name='DADL Lab',
            lab_full_name='Data Analysis and Deep Learning Laboratory',
            focus_statement='Developing innovative ML algorithms and data analysis techniques.',
            mission='Advancing AI through research and training next-generation data scientists.',
            research_areas='Deep Learning, Computer Vision, NLP, Reinforcement Learning',
            lab_email='dadl-lab@university.edu',
            lab_address='Computer Science Department, Room 301',
            lab_phone='+1 (555) 123-4567'
        )
        db.session.add(lab_info)
        print("Created default lab information")
    
    # Create sample student (optional)
    if not Student.query.first():
        sample_student = Student(
            name='Jane Doe',
            degree_type='PhD',
            research_focus='Deep Learning for Computer Vision',
            school='University Name',
            start_date='Fall 2023',
            is_current=True,
            email='jane.doe@university.edu'
        )
        db.session.add(sample_student)
        print("Created sample student")
    
    # Create sample project (optional)
    if not Project.query.first():
        sample_project = Project(
            title='Deep Learning for Medical Image Analysis',
            topic='Computer Vision',
            overview='Developing novel deep learning algorithms for automated medical diagnosis.',
            status='Ongoing',
            start_date='Jan 2024'
        )
        db.session.add(sample_project)
        print("Created sample project")
    
    db.session.commit()
    print("Default data creation complete!")

# ============================================================================
# 7. Main Entry Point
# ============================================================================
if __name__ == '__main__':
    with app.app_context():
        # For first run only - remove the database deletion after initial setup
        db_path = 'dadl_lab.db'
        if os.path.exists(db_path):
            response = input("Database exists. Delete and recreate? (y/n): ")
            if response.lower() == 'y':
                os.remove(db_path)
                print("Old database removed.")
        
        # Create tables
        db.create_all()
        create_default_data()
    
    print("\n" + "="*60)
    print("DADL Lab Website Starting...")
    print("="*60)
    print("Main website: http://localhost:5000/")
    print("Admin panel: http://localhost:5000/admin/")
    print("Admin login: http://localhost:5000/admin-login")
    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: changeme123")
    print("\nFile uploads are enabled for:")
    print("  - Professor photos")
    print("  - Student photos")
    print("  - Project images")
    print("="*60 + "\n")
    
    app.run(debug=True)