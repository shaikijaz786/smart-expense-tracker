from flask import Flask, render_template, request, redirect
import sqlite3
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'shaik' and password == 'ijaz':
            return redirect('/home')

        return "Invalid Login"

    return render_template('login.html')


# HOME PAGE
@app.route('/home')
def home():
    return render_template('index.html')


# ADD EXPENSE
@app.route('/add', methods=['POST'])
def add():
    amount = request.form['amount']
    date = request.form['date']
    category = request.form['category']

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, date, category) VALUES (?, ?, ?)",
        (amount, date, category)
    )

    conn.commit()
    conn.close()

    return redirect('/report')


# REPORT PAGE
@app.route('/report')
def report():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT amount, date, category FROM expenses")
    expenses = cursor.fetchall()

    conn.close()

    total = 0
    category_totals = {}

    for expense in expenses:

        amount = float(expense[0])
        category = expense[2]

        total += amount

        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    if len(amounts) > 0:
        plt.figure(figsize=(5, 5))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%')
        plt.title("Expense Distribution")
        plt.savefig("static/charts/expense_chart.png")
        plt.close()

    return render_template(
        'report.html',
        expenses=expenses,
        total=total
    )


# CLEAR DATA
@app.route('/clear')
def clear():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()

    return redirect('/home')

@app.route('/search', methods=['POST'])
def search():

    category = request.form['category']

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount, date, category FROM expenses WHERE category=?",
        (category,)
    )

    expenses = cursor.fetchall()

    conn.close()

    total = sum(float(row[0]) for row in expenses)

    return render_template(
        'report.html',
        expenses=expenses,
        total=total
    )



@app.route('/monthly')
def monthly():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT substr(date,1,7) AS month,
                   SUM(amount)
            FROM expenses
            GROUP BY month
            ORDER BY month
        """)

        data = cursor.fetchall()

    except Exception as e:
        conn.close()
        return str(e)

    conn.close()

    return render_template(
        'monthly.html',
        data=data
    )

if __name__ == '__main__':
    app.run(debug=True)