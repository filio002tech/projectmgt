from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'secure_collaboration_key_2026' # Protects state cookies

def get_db_connection():
    conn = sqlite3.connect('collaboration.db')
    conn.row_factory = sqlite3.Row # Allows dictionary-like row querying
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            # Populate secure session tokens
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['username'] = user['username']
            flash('Welcome back to your workspace!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid system credentials. Please check your username/password.', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Unauthorized boundary entry blocked. Please login.', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    # Pull current project lists
    projects = conn.execute('SELECT * FROM projects').fetchall()
    # Pull explicit matrix breakdown of all team contributions linked with project tags
    contributions = conn.execute('''
        SELECT c.*, p.title as project_title 
        FROM contributions c 
        JOIN projects p ON c.project_id = p.id
        ORDER BY c.id DESC
    ''').fetchall()
    conn.close()
    
    return render_template('dashboard.html', projects=projects, contributions=contributions)

@app.route('/create_project', methods=['POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.form['title'].strip()
    duration = request.form['duration'].strip()
    required_role = request.form['required_role'].strip()
    created_by = session['name']
    
    if title and duration:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO projects (title, duration, required_role, created_by)
            VALUES (?, ?, ?, ?)
        ''', (title, duration, required_role, created_by))
        conn.commit()
        conn.close()
        flash('Project Framework deployed to systemic cloud nodes successfully!', 'success')
    else:
        flash('Failed to deploy project. Complete all fields.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/submit_contribution', methods=['POST'])
def submit_contribution():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    project_id = request.form['project_id']
    task_title = request.form['task_title'].strip()
    code_submission = request.form['code_submission'].strip()
    
    if project_id and task_title:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO contributions (project_id, staff_name, staff_role, task_title, code_submission)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, session['name'], session['role'], task_title, code_submission))
        conn.commit()
        conn.close()
        flash('Contribution successfully integrated and audited inside the matrix logs!', 'success')
    else:
        flash('Submission failed. Provide all necessary parameters.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Session securely terminated.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)