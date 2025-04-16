from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # For timezone handling

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Needed for flash messages

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

def format_datetime(value):
    """Format a datetime object to a string in local timezone"""
    if value is None:
        return ""
    local_tz = pytz.timezone('Asia/Kolkata')  # Change to your preferred timezone
    local_dt = value.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime('%Y-%m-%d %H:%M')

# Add the filter to Jinja2 environment
app.jinja_env.filters['datetime'] = format_datetime

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        
        if not title or not desc:
            flash('Both title and description are required!', 'danger')
        else:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            flash('Todo added successfully!', 'success')
        return redirect('/')
    
    all_todo = Todo.query.order_by(Todo.date_created.desc()).all()
    return render_template('index.html', allTodo=all_todo)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.get_or_404(sno)
    
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        
        if not title or not desc:
            flash('Both title and description are required!', 'danger')
        else:
            todo.title = title
            todo.desc = desc
            db.session.commit()
            flash('Todo updated successfully!', 'success')
        return redirect('/')
    
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect('/')

@app.route('/toggle/<int:sno>')
def toggle_complete(sno):
    todo = Todo.query.get_or_404(sno)
    todo.completed = not todo.completed
    db.session.commit()
    flash('Todo status updated!', 'info')
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
#  pip install gunicorn
# pip freeze >  requirements.txta
#from app import app, db
# with app.app_context():
#     db.create_all()