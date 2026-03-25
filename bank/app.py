from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "bank_secret"

DB_FILE = "database.json"

# Initialize database if not exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"accounts": {}, "transactions": []}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Home Page
@app.route("/")
def index():
    db = load_db()
    total_accounts = len(db["accounts"])
    total_balance = sum([acc["balance"] for acc in db["accounts"].values()])
    return render_template("index.html", total_accounts=total_accounts, total_balance=total_balance)

# Create Account
@app.route("/create", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        db = load_db()
        acc_no = request.form["acc_no"]
        name = request.form["name"]
        balance = float(request.form["balance"])
        if acc_no in db["accounts"]:
            flash("Account already exists!", "error")
        else:
            db["accounts"][acc_no] = {"name": name, "balance": balance}
            db["transactions"].append({"acc_no": acc_no, "type": "Create", "amount": balance})
            save_db(db)
            flash("Account created successfully!", "success")
        return redirect(url_for("index"))
    return render_template("create_account.html")

# View Account
@app.route("/view/<acc_no>")
def view_account(acc_no):
    db = load_db()
    account = db["accounts"].get(acc_no)
    if not account:
        flash("Account not found!", "error")
        return redirect(url_for("index"))
    transactions = [t for t in db["transactions"] if t["acc_no"] == acc_no]
    return render_template("view_account.html", acc_no=acc_no, account=account, transactions=transactions)

# Deposit
@app.route("/deposit/<acc_no>", methods=["GET", "POST"])
def deposit(acc_no):
    db = load_db()
    account = db["accounts"].get(acc_no)
    if not account:
        flash("Account not found!", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        amount = float(request.form["amount"])
        account["balance"] += amount
        db["transactions"].append({"acc_no": acc_no, "type": "Deposit", "amount": amount})
        save_db(db)
        flash("Deposit successful!", "success")
        return redirect(url_for("view_account", acc_no=acc_no))
    return render_template("deposit.html", acc_no=acc_no, account=account)

# Withdraw
@app.route("/withdraw/<acc_no>", methods=["GET", "POST"])
def withdraw(acc_no):
    db = load_db()
    account = db["accounts"].get(acc_no)
    if not account:
        flash("Account not found!", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        amount = float(request.form["amount"])
        if amount > account["balance"]:
            flash("Insufficient balance!", "error")
        else:
            account["balance"] -= amount
            db["transactions"].append({"acc_no": acc_no, "type": "Withdraw", "amount": amount})
            save_db(db)
            flash("Withdrawal successful!", "success")
        return redirect(url_for("view_account", acc_no=acc_no))
    return render_template("withdraw.html", acc_no=acc_no, account=account)

# Transfer
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    db = load_db()
    if request.method == "POST":
        from_acc = request.form["from_acc"]
        to_acc = request.form["to_acc"]
        amount = float(request.form["amount"])
        if from_acc not in db["accounts"] or to_acc not in db["accounts"]:
            flash("One or both accounts not found!", "error")
        elif amount > db["accounts"][from_acc]["balance"]:
            flash("Insufficient balance in source account!", "error")
        else:
            db["accounts"][from_acc]["balance"] -= amount
            db["accounts"][to_acc]["balance"] += amount
            db["transactions"].append({"acc_no": from_acc, "type": f"Transfer to {to_acc}", "amount": amount})
            db["transactions"].append({"acc_no": to_acc, "type": f"Transfer from {from_acc}", "amount": amount})
            save_db(db)
            flash("Transfer successful!", "success")
        return redirect(url_for("index"))
    return render_template("transfer.html")

# Search Account
@app.route("/search", methods=["GET", "POST"])
def search_account():
    db = load_db()
    if request.method == "POST":
        acc_no = request.form["acc_no"]
        if acc_no in db["accounts"]:
            return redirect(url_for("view_account", acc_no=acc_no))
        else:
            flash("Account not found!", "error")
            return redirect(url_for("search_account"))
    return render_template("search_account.html")

# View all transactions
@app.route("/transactions")
def transactions():
    db = load_db()
    return render_template("transactions.html", transactions=db["transactions"])

if __name__ == "__main__":
    app.run(debug=True)