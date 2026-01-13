from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

DATABASE = 'students.db'


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# =============================================================================
# CREATE - Add new student
# =============================================================================

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()

        # Check if email already exists
        existing_email = conn.execute(
            'SELECT id FROM students WHERE email = ?',
            (email,)
        ).fetchone()

        if existing_email:
            conn.close()
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_student'))

        conn.execute(
            'INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
            (name, email, course)
        )
        conn.commit()
        conn.close()

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    # GET request only
    return render_template('add.html')


    #    



# =============================================================================
# READ - Display all students + SEARCH
# =============================================================================

@app.route('/')
def index():
    search = request.args.get('search')

    conn = get_db_connection()
    if search:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? ORDER BY id DESC",
            (f"%{search}%",)
        ).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template('index.html', students=students)



# =============================================================================
# UPDATE - Edit student
# =============================================================================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn.execute(
            'UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?',
            (name, email, course, id)
        )
        conn.commit()
        conn.close()

        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()
    return render_template('edit.html', student=student)


# =============================================================================
# DELETE - Remove student
# =============================================================================

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM students WHERE id = ?',
        (id,)
    )
    conn.commit()
    conn.close()

    flash('Student deleted successfully!', 'danger')
    return redirect(url_for('index'))


# =============================================================================
# RUN APP
# =============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
