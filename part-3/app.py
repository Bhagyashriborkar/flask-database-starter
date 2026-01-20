from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Teacher(db.Model):
    """
    EXERCISE SOLUTION: Teacher model with One-to-Many relationship
    One Teacher -> Many Courses
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subject_specialty = db.Column(db.String(100))
    
    # Relationship: One Teacher has Many Courses
    courses = db.relationship('Course', backref='teacher', lazy=True)
    
    def __repr__(self):
        return f'<Teacher {self.name}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Foreign Key linking to Teacher
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    
    # Relationship: One Course has Many Students
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Foreign Key linking to Course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'


# =============================================================================
# BASIC ROUTES
# =============================================================================

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


@app.route('/teachers')
def teachers():
    all_teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=all_teachers)


# =============================================================================
# STUDENT ROUTES
# =============================================================================

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        new_student = Student(name=name, email=email, course_id=course_id)
        db.session.add(new_student)
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('add.html', courses=courses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit() 
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


# =============================================================================
# COURSE ROUTES
# =============================================================================

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        teacher_id = request.form.get('teacher_id')
        teacher_id = int(teacher_id) if teacher_id else None
        
        new_course = Course(
            name=name,
            description=description,
            teacher_id=teacher_id
        )

        db.session.add(new_course)
        db.session.commit()

        flash('Course added!', 'success')
        return redirect(url_for('courses'))
    
    teachers = Teacher.query.all()
    return render_template('add_course.html', teachers=teachers)


# =============================================================================
# TEACHER ROUTES
# =============================================================================

@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject_specialty = request.form.get('subject_specialty', '')

        new_teacher = Teacher(name=name, email=email, subject_specialty=subject_specialty)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))

    return render_template('add_teacher.html')


@app.route('/edit-teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    if request.method == 'POST':
        teacher.name = request.form['name']
        teacher.email = request.form['email']
        teacher.subject_specialty = request.form.get('subject_specialty', '')

        db.session.commit()
        flash('Teacher updated!', 'success')
        return redirect(url_for('teachers'))

    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/delete-teacher/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()

    flash('Teacher deleted!', 'danger')
    return redirect(url_for('teachers'))



# =============================================================================

@app.route('/query-demo')
def query_demo():
    """
    EXERCISE SOLUTION: Demonstrates filter(), order_by(), limit() and more!
    """
    
    results = {}

    # =========================================================================
    # 1. filter() - Filter records with conditions
    # =========================================================================
    
    # Example 1a: Students whose name contains 'a'
    results['filter_students'] = Student.query.filter(
        Student.name.like('%a%')
    ).all()
    
    # Example 1b: Filter by exact match
    results['filter_exact'] = Student.query.filter(
        Student.id == 1
    ).first()
    
    # Example 1c: Filter with multiple conditions (AND)
    results['filter_multiple'] = Student.query.filter(
        Student.name.like('%a%'),
        Student.id > 0
    ).all()

    # =========================================================================
    # 2. order_by() - Sort results
    # =========================================================================
    
    # Example 2a: Order by name (A → Z)
    results['ordered_students'] = Student.query.order_by(
        Student.name
    ).all()
    
    # Example 2b: Order by name descending (Z → A)
    results['ordered_desc'] = Student.query.order_by(
        Student.name.desc()
    ).all()
    
    # Example 2c: Order by ID descending (newest first)
    results['ordered_by_id'] = Student.query.order_by(
        Student.id.desc()
    ).all()

    # =========================================================================
    # 3. limit() - Limit number of results
    # =========================================================================
    
    # Example 3a: Get first 3 students
    results['limited_students'] = Student.query.limit(3).all()
    
    # Example 3b: Combine limit with order_by
    results['limited_ordered'] = Student.query.order_by(
        Student.name
    ).limit(2).all()

    # =========================================================================
    # BONUS: Advanced Query Methods
    # =========================================================================
    
    # Example 4: count() - Count total records
    results['total_students'] = Student.query.count()
    results['total_courses'] = Course.query.count()
    results['total_teachers'] = Teacher.query.count()
    
    # Example 5: first() - Get first record
    results['first_student'] = Student.query.first()
    
    # Example 6: filter_by() - Simpler filter for exact matches
    results['filter_by_course'] = Student.query.filter_by(
        course_id=1
    ).all() if Course.query.count() > 0 else []
    
    # Example 7: Join queries - Get students with their courses
    results['students_with_courses'] = db.session.query(
        Student, Course
    ).join(Course).all()
    
    # Example 8: Relationship queries - Teachers with courses
    results['teachers_with_courses'] = Teacher.query.all()

    return render_template('query_demo.html', results=results)


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """Create tables and add sample data"""
    print("Starting database initialization...")
    with app.app_context():
        db.create_all()
        print("✓ Tables created.")

        # Add sample teachers
        if Teacher.query.count() == 0:
            sample_teachers = [
                Teacher(name='Dr. Duryodhan Jathar', email='jathar@school.com', subject_specialty='Computer Science'),
                Teacher(name='Prof. Prachi Patekar', email='prachi@school.com', subject_specialty='Data Science'),
                Teacher(name='Ms. Shruti Bhate', email='shruti@school.com', subject_specialty='Web Development'),
            ]
            db.session.add_all(sample_teachers)
            db.session.commit()
            print('✓ Sample teachers added!')

        # Add sample courses
        if Course.query.count() == 0:
            teachers = Teacher.query.all()
            sample_courses = [
                Course(name='Python Basics', description='Learn Python programming fundamentals', teacher_id=teachers[0].id),
                Course(name='Web Development', description='HTML, CSS, JavaScript and Flask', teacher_id=teachers[2].id),
                Course(name='Data Science', description='Data analysis with Python', teacher_id=teachers[1].id),
                Course(name='Machine Learning', description='ML algorithms and applications', teacher_id=teachers[1].id),
            ]
            db.session.add_all(sample_courses)
            db.session.commit()
            print('✓ Sample courses added!')
        
        # Add sample students
        if Student.query.count() == 0:
            courses = Course.query.all()
            sample_students = [
                Student(name='Alice Johnson', email='alice@student.com', course_id=courses[0].id),
                Student(name='Bob Smith', email='bob@student.com', course_id=courses[1].id),
                Student(name='Charlie Brown', email='charlie@student.com', course_id=courses[0].id),
                Student(name='Diana Prince', email='diana@student.com', course_id=courses[2].id),
                Student(name='Ethan Hunt', email='ethan@student.com', course_id=courses[1].id),
            ]
            db.session.add_all(sample_students)
            db.session.commit()
            print('✓ Sample students added!')
        
        print("Database initialization complete!\n")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# EXERCISE SOLUTIONS SUMMARY:
# =============================================================================
#
#  EXERCISE 1: Teacher Model
# - Created Teacher class with id, name, email, subject_specialty
# - Added One-to-Many relationship: Teacher -> Courses
# - Used db.relationship() and db.ForeignKey()
#
# EXERCISE 2: Query Methods
# - filter(): Student.query.filter(Student.name.like('%a%')).all()
# - order_by(): Student.query.order_by(Student.name).all()
# - limit(): Student.query.limit(3).all()
#
# BONUS QUERIES INCLUDED:
# - filter_by(): Simpler exact match filtering
# - count(): Count total records
# - first(): Get first record
# - desc(): Descending order
# - Join queries: Combine multiple tables
# - Relationship access: teacher.courses, student.course
#
# =============================================================================