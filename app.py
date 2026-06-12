from flask import Flask, render_template, request, redirect, session
import sqlite3
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "expense_secret"   # ✅ REQUIRED for session (IMPORTANT)

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'shaik' and password == 'ijaz':
            session['user'] = username   # ✅ SESSION ADDED
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')


# ---------------- DASHBOARD (NEW FIX) ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT amount, date, category FROM expenses")
    expenses = cursor.fetchall()

    conn.close()

    total = sum(float(row[0]) for row in expenses) if expenses else 0

    return render_template('dashboard.html', expenses=expenses, total=total)


# ---------------- ADD EXPENSE ----------------
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

    return redirect('/dashboard')


# ---------------- REPORT ----------------
@app.route('/report')
def report():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT amount, date, category FROM expenses")
    expenses = cursor.fetchall()

    conn.close()

    total = sum(float(exp[0]) for exp in expenses)

    category_totals = {}

    for exp in expenses:
        amount = float(exp[0])
        category = exp[2]

        category_totals[category] = category_totals.get(category, 0) + amount

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    if amounts:
        plt.figure(figsize=(5, 5))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%')
        plt.title("Expense Distribution")
        plt.savefig("static/charts/expense_chart.png")
        plt.close()

    return render_template('report.html', expenses=expenses, total=total)


# ---------------- CLEAR ----------------
@app.route('/clear')
def clear():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- SEARCH ----------------
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

    return render_template('report.html', expenses=expenses, total=total)


# ---------------- MONTHLY ----------------
@app.route('/monthly')
def monthly():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT substr(date,1,7) AS month,
               SUM(amount)
        FROM expenses
        GROUP BY month
        ORDER BY month
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template('monthly.html', data=data)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)