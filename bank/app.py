from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"accounts": [], "transactions": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# Path to the JSON database
DB_FILE = "database.json"

# Helper function to read database
def read_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return {"accounts": []}

# Helper function to write database
def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Home page / Dashboard
@app.route('/')
def index():
    data = read_db()
    total_accounts = len(data["accounts"])
    total_balance = sum(acc.get("balance", 0) for acc in data["accounts"])
    return render_template("index.html", total_accounts=total_accounts, total_balance=total_balance)

@app.route('/dashboard')
def dashboard():
    data = load_data()
    total_accounts = len(data.get('accounts', []))
    total_balance = sum(acc.get('balance', 0) for acc in data.get('accounts', []))

    return render_template('dashboard.html',
                           total_accounts=total_accounts,
                           total_balance=total_balance)

# Create Account page
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        name = request.form["name"]
        balance = float(request.form["balance"])

        data = load_data()

        account = {
            "account_number": len(data["accounts"]) + 1,
            "name": name,
            "balance": balance
        }

        data["accounts"].append(account)
        save_data(data)

        return redirect(url_for("index"))

    return render_template("create_account.html")

# Transfer Money page
@app.route('/transfer', methods=['GET', 'POST'])
def transfer_money():
    data = read_db()
    if request.method == 'POST':
        from_id = int(request.form['from_id'])
        to_id = int(request.form['to_id'])
        amount = float(request.form['amount'])

        accounts = {acc["id"]: acc for acc in data["accounts"]}
        if from_id in accounts and to_id in accounts and accounts[from_id]["balance"] >= amount:
            accounts[from_id]["balance"] -= amount
            accounts[to_id]["balance"] += amount
            write_db(data)
            flash("Transfer successful!", "success")
        else:
            flash("Invalid transfer!", "error")
        return redirect(url_for('transfer_money'))

    return render_template("transfer.html", accounts=data["accounts"])

# View Account page
@app.route('/view')
def view_account():
    data = read_db()
    return render_template("view_account.html", accounts=data["accounts"])

# Deposit page
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    data = read_db()
    if request.method == 'POST':
        account_id = int(request.form['account_id'])
        amount = float(request.form['amount'])
        for acc in data["accounts"]:
            if acc["id"] == account_id:
                acc["balance"] += amount
                write_db(data)
                flash("Deposit successful!", "success")
                break
        return redirect(url_for('deposit'))
    return render_template("deposit.html", accounts=data["accounts"])

@app.route('/transactions')
def transactions():
    data = load_data()
    transactions = data.get('transactions', [])
    return render_template('transactions.html', transactions=transactions)

@app.route('/search', methods=['GET', 'POST'])
def search_account():
    data = load_data()
    account = None

    if request.method == 'POST':
        acc_no = request.form['account_number']
        account = next((acc for acc in data['accounts'] if acc['account_number'] == acc_no), None)

    return render_template('search_account.html', account=account)

# Withdraw page
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    data = read_db()
    if request.method == 'POST':
        account_id = int(request.form['account_id'])
        amount = float(request.form['amount'])
        for acc in data["accounts"]:
            if acc["id"] == account_id and acc["balance"] >= amount:
                acc["balance"] -= amount
                write_db(data)
                flash("Withdrawal successful!", "success")
                break
        else:
            flash("Insufficient balance!", "error")
        return redirect(url_for('withdraw'))
    return render_template("withdraw.html", accounts=data["accounts"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)