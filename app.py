from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return f"Received: Name = {name}, Email = {email} (Saved to database!)"
    return "Method not allowed"

@app.route('/users')    
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    search_query = request.args.get('search', '')
    if search_query:
        users = User.query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('users.html', users=users)

@app.route('/edit/<int:id>')
def edit(id):
    user = User.query.get_or_404(id)
    return render_template('edit.html', user=user)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    user = User.query.get_or_404(id)
    user.name = request.form['name']
    user.email = request.form['email']
    db.session.commit()
    return redirect(url_for('users'))

@app.route('/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

@app.route('/summary')
def summary():
    total_users = User.query.count()
    last_user = User.query.order_by(User.id.desc()).first()
    days_active = 1  # Simple estimate
    avg_entries_per_day = total_users / days_active if days_active else 0
    return render_template('summary.html', total_users=total_users, avg_entries_per_day=round(avg_entries_per_day, 2), last_user=last_user)


from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Farz karein yeh aapka data hai jo database se aa raha hai
students = [
    {'id': 1, 'name': 'Ali Khan', 'major': 'Computer Science', 'gpa': 3.8},
    {'id': 2, 'name': 'Fatima Ahmed', 'major': 'Software Engineering', 'gpa': 3.9},
    {'id': 3, 'name': 'Zainab Butt', 'major': 'Data Science', 'gpa': 3.5},
    {'id': 4, 'name': 'Bilal Rana', 'major': 'Computer Science', 'gpa': 3.2},
]
next_id = 5

# Main page jo table dikhayega
@app.route('/')
def index():
    return render_template('table.html', students=students)

# Naya student add karne wala function
@app.route('/add', methods=['POST'])
def add_student():
    global next_id
    # Yeh HTML form se data hasil karega
    name = request.form['name']
    major = request.form['major']
    gpa = float(request.form['gpa'])

    # Naya student bana kar list mein add karega
    new_student = {'id': next_id, 'name': name, 'major': major, 'gpa': gpa}
    students.append(new_student)
    next_id += 1
    
    # Wapis main page par bhej dega
    return redirect(url_for('index'))

# Student delete karne wala function
@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    # YAHAN PAR WO STUDENT ID AAYEGI JIS PAR USER NE CLICK KIYA HOGA
    # For example, agar user ne ID 2 wale student ke 'Delete' link par click kiya,
    # to yahan student_id mein '2' aa jayega.
    
    global students
    
    # Yeh line ek nayi list banayegi jis mein woh student nahi hoga jiski ID match hui
    students = [s for s in students if s['id'] != student_id]
    
    # Wapis main page par bhej dega
    return redirect(url_for('index'))


@app.route('/export')
def export():
    users = User.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Email'])
    for user in users:
        cw.writerow([user.id, user.name, user.email])
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers['Content-Disposition'] = 'attachment; filename=users_export.csv'
    return output

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)