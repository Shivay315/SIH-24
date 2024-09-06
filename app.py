from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    bus = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Attendance {self.student_name} on {self.date}>'

# Create the database tables
with app.app_context():
    db.create_all()

# Sample drivers (if used)
drivers = {
    "Shivay": "879",
    "Prince": "165a"
}

@app.route('/')
def index():
    records = Attendance.query.all()
    return render_template('index.html', drivers=drivers, record=records)  # Keeps the index.html route

@app.route('/schedule')
def schedule():
    records = Attendance.query.all()
    return render_template('schedule.html', records=records)  # New route for schedule.html

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_record = Attendance(
            student_name=request.form['student_name'],
            bus=request.form['bus'],
            date=request.form['date'],
            status=request.form['status']
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('schedule'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    record = Attendance.query.get_or_404(id)
    if request.method == 'POST':
        record.student_name = request.form['student_name']
        record.bus = request.form['bus']
        record.date = request.form['date']
        record.status = request.form['status']
        db.session.commit()
        return redirect(url_for('schedule'))
    return render_template('edit.html', record=record)

@app.route('/delete/<int:id>')
def delete(id):
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('schedule'))

if __name__ == '__main__':
    app.run(debug=True)
