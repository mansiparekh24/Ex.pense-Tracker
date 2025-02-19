from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for flash messages

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    expenses = Expense.query.all()
    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0  # Sum of all expenses
    return render_template('index.html', expenses=expenses, total_expense=total_expense)

@app.route('/chart')
def chart():
    expense_data = db.session.query(Expense.category, db.func.sum(Expense.amount).label('total_amount'))\
        .group_by(Expense.category).all()

    expense_data = [{'category': data.category, 'amount': data.total_amount} for data in expense_data]

    return render_template('chart.html', expense_data=expense_data)



@app.route('/add', methods=['POST'])
def add_expense():
    description = request.form.get('description', '').strip()
    amount = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()

    if not description or not amount or not category:
        flash("All fields are required!", "danger")
        return redirect(url_for('index'))

    try:
        amount = float(amount)
        new_expense = Expense(description=description, amount=amount, category=category)
        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added successfully!", "success")
    except ValueError:
        flash("Invalid amount!", "danger")

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully!", "warning")
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        db.session.commit()
        flash("Expense updated successfully!", "info")
        return redirect(url_for('index'))

    return render_template('edit.html', expense=expense)

if __name__ == '__main__':
    app.run(debug=True)
