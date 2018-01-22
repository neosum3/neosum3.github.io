from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from time import localtime, strftime

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    stocks = db.execute("SELECT * FROM :name", name = rows[0]["username"])
    total=0
    for stock in stocks:
        s = lookup (stock["symbol"])
        stock["symbol"] =stock["symbol"].upper()
        stock["name"] = s["name"]
        temp = s["price"]
        stock["price"] = usd(temp)
        temp2 = temp * stock["quantity"]
        stock["total"] = usd(temp2)
        total += temp2
    return render_template("index.html", stocks = stocks, ctotal = usd(rows[0]["cash"]), total = usd(total + rows[0]["cash"]))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("missing symbol", 400)
        if not request.form.get("shares"):
            return apology("missing shares", 400)
        s = lookup (request.form.get("symbol"))
        if s == None: return apology("symbol doesn't exist", 400)

        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        quantity = int(request.form.get("shares"))
        if s["price"] * quantity > rows[0]["cash"]:
            return apology("can't afford", 400)

        else:
            x = db.execute("SELECT * FROM :name WHERE symbol = :symbol",
                name = rows[0]["username"], symbol=request.form.get("symbol"))
            if len(x) == 0:  #add new stock
                db.execute("INSERT INTO :name (symbol, quantity) VALUES (:symbol, :quantity)", name = rows[0]["username"],
                    symbol=request.form.get("symbol"), quantity=request.form.get("shares"))
            else:            #update existing stoke
                new_shares = x[0]["quantity"] + quantity
                db.execute("UPDATE :name SET quantity= :new WHERE symbol = :symbol", name = rows[0]["username"],
                    new = new_shares, symbol=request.form.get("symbol"))
            new_cash = rows[0]["cash"] - s["price"] * quantity   #update balance
            db.execute("UPDATE users SET cash= :new WHERE id = :id", new = new_cash, id=session["user_id"])
            db.execute("INSERT INTO history (user, stock, quantity, price, datetime) VALUES (:user, :stock, :quantity, :price, :datetime)",
                user = rows[0]["username"], stock=request.form.get("symbol"), quantity=quantity, price=s["price"],
                datetime =strftime("%Y-%m-%d %H:%M:%S", localtime()) )
            flash ("Bought!")
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")

@app.route("/topup", methods=["GET", "POST"])
@login_required
def topup():
    """Top up cash"""
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    records = db.execute("SELECT * FROM topup WHERE user = :name", name = rows[0]["username"])
    for record in records:
        record["amount"] = usd(record["amount"])
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("money"):
            return apology("Top up unsucessful", 400)

        new_money = rows[0]["cash"] + int(request.form.get("money"))

        db.execute("UPDATE users SET cash= :new WHERE id = :id", new = new_money, id=session["user_id"])
        db.execute("INSERT INTO topup (user, amount, datetime) VALUES (:user, :amount, :datetime)", user = rows[0]["username"],
            amount=int(request.form.get("money")), datetime =strftime("%Y-%m-%d %H:%M:%S", localtime()) )
        flash ("Top up sucessful!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("topup.html", records = records)


@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    stocks = db.execute("SELECT * FROM history WHERE user = :name", name = rows[0]["username"])
    for stock in stocks:
        stock["stock"] =stock["stock"].upper()
        stock["price"] = usd(stock["price"])
    return render_template("history.html", stocks = stocks)

@app.route("/Jalter")
@login_required
def Jlter():
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    stocks = db.execute("SELECT * FROM history WHERE user = :name", name = rows[0]["username"])
    for stock in stocks:
        stock["stock"] =stock["stock"].upper()
        stock["price"] = usd(stock["price"])
    return render_template("Jalter.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        flash("Welcome back, master!")
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/") #should be ("/"), here just to be lazy

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/fgo", methods=["GET"])   #preivous name: quote
@login_required
def fgo():
    """Provide guildance for FGO CN and US servers and update fgo info"""

    rows = db.execute("SELECT * FROM FGO_info WHERE server = :s", s = "CN")
    CN_info = {"act_time": rows[0]["act_time"], "guild1": rows[0]["guild1"],"guild1_link": rows[0]["guild1_link"],
                "guild2": rows[0]["guild2"],"guild2_link": rows[0]["guild2_link"],"weekly": rows[0]["weekly"], "weekly_link": rows[0]["weekly_link"],
                "quartz": rows[0]["quartz"], "ticket": rows[0]["ticket"], "note": rows[0]["note"]}
    rows = db.execute("SELECT * FROM FGO_info WHERE server = :s", s = "US")
    US_info = {"act_time": rows[0]["act_time"], "guild1": rows[0]["guild1"],"guild1_link": rows[0]["guild1_link"],
            "guild2": rows[0]["guild2"],"guild2_link": rows[0]["guild2_link"],"weekly": rows[0]["weekly"], "weekly_link": rows[0]["weekly_link"],
            "quartz": rows[0]["quartz"], "ticket": rows[0]["ticket"], "note": rows[0]["note"]}

    if request.method == "GET":      # User reached route via GET (as by clicking a link or via redirect)
        if request.args.get('CN_act_time'):
            db.execute("UPDATE FGO_info SET act_time= :new WHERE server = :s", new =request.args.get('CN_act_time'), s = "CN")
            db.execute("UPDATE FGO_info SET guild1= :new WHERE server = :s", new =request.args.get('CN_guild1'), s = "CN")
            db.execute("UPDATE FGO_info SET guild1_link= :new WHERE server = :s", new =request.args.get('CN_guild1_link'), s = "CN")
            db.execute("UPDATE FGO_info SET guild2= :new WHERE server = :s", new =request.args.get('CN_guild2'), s = "CN")
            db.execute("UPDATE FGO_info SET guild2_link= :new WHERE server = :s", new =request.args.get('CN_guild2_link'), s = "CN")
            db.execute("UPDATE FGO_info SET weekly= :new WHERE server = :s", new =request.args.get('CN_weekly'), s = "CN")
            db.execute("UPDATE FGO_info SET weekly_link= :new WHERE server = :s", new =request.args.get('CN_weekly_link'), s = "CN")
            db.execute("UPDATE FGO_info SET quartz= :new WHERE server = :s", new =int(request.args.get('CN_stone')), s = "CN")
            db.execute("UPDATE FGO_info SET ticket= :new WHERE server = :s", new =int(request.args.get('CN_ticket')), s = "CN")
            db.execute("UPDATE FGO_info SET note= :new WHERE server = :s", new = request.args.get('CN_note'), s = "CN")
            #rows = db.execute("SELECT * FROM FGO_info WHERE server = :s", s = "CN")
            #CN_info = {"quartz": rows[0]["quartz"], "ticket": rows[0]["ticket"], "note": rows[0]["note"]}
            return jsonify(CN_info) #will get error if return nothing
        elif request.args.get('US_act_time'):
            db.execute("UPDATE FGO_info SET act_time= :new WHERE server = :s", new =request.args.get('US_act_time'), s = "US")
            db.execute("UPDATE FGO_info SET guild1= :new WHERE server = :s", new =request.args.get('US_guild1'), s = "US")
            db.execute("UPDATE FGO_info SET guild1_link= :new WHERE server = :s", new =request.args.get('US_guild1_link'), s = "US")
            db.execute("UPDATE FGO_info SET guild2= :new WHERE server = :s", new =request.args.get('US_guild2'), s = "US")
            db.execute("UPDATE FGO_info SET guild2_link= :new WHERE server = :s", new =request.args.get('US_guild2_link'), s = "US")
            db.execute("UPDATE FGO_info SET weekly= :new WHERE server = :s", new =request.args.get('US_weekly'), s = "US")
            db.execute("UPDATE FGO_info SET weekly_link= :new WHERE server = :s", new =request.args.get('US_weekly_link'), s = "US")
            db.execute("UPDATE FGO_info SET quartz= :new WHERE server = :s", new =int(request.args.get('US_stone')), s = "US")
            db.execute("UPDATE FGO_info SET ticket= :new WHERE server = :s", new =int(request.args.get('US_ticket')), s = "US")
            db.execute("UPDATE FGO_info SET note= :new WHERE server = :s", new = request.args.get('US_note'), s = "US")
            return jsonify(US_info)

        else:
            return render_template("fgo.html",  CN_info=CN_info, US_info=US_info)
    else:
        return render_template("fgo.html",  CN_info=CN_info, US_info=US_info)

@app.route("/japanese", methods=["GET"])   #preivous name: quote
@login_required
def japanese():
    """Provide guildance for FGO CN and US servers and update fgo info"""

    rows = db.execute("SELECT * FROM JAP WHERE 	user_id = :s", s = session["user_id"])
    info = {"note": rows[0]["note"]}

    if request.method == "GET":      # User reached route via GET (as by clicking a link or via redirect)
        if request.args.get('JP_note'):
            db.execute("UPDATE JAP SET note= :new WHERE user_id = :s", new =request.args.get('JP_note'), s = session["user_id"])
            #db.execute("UPDATE JAP SET note= :new WHERE user = :s", new =request.args.get('JP_note'), s = "x")
            #rows = db.execute("SELECT * FROM FGO_info WHERE server = :s", s = "CN")
            #CN_info = {"quartz": rows[0]["quartz"], "ticket": rows[0]["ticket"], "note": rows[0]["note"]}
            return jsonify(info) #will get error if return nothing

        else:
            return render_template("japanese.html",  info=info)
    else:
        return render_template("japanese.html",  info=info)

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    stocks = db.execute("SELECT * FROM :name", name = rows[0]["username"])

    if request.method == "POST":
        if not request.form.get("shares"):
            return apology("missing shares", 400)

        x = db.execute("SELECT * FROM :name WHERE symbol = :symbol",
            name = rows[0]["username"], symbol=request.form.get("symbol"))
        quantity = int(request.form.get("shares"))
        if quantity > x[0]["quantity"]: return apology("too many shares", 400)

        new_shares = x[0]["quantity"] - quantity

        if new_shares>0:
            db.execute("UPDATE :name SET quantity= :new WHERE symbol = :symbol", name = rows[0]["username"],
                new = new_shares, symbol=request.form.get("symbol"))
        elif new_shares==0:
            db.execute("DELETE FROM :name WHERE symbol = :symbol", name = rows[0]["username"], symbol=request.form.get("symbol"))
        s = lookup (request.form.get("symbol"))
        new_cash = rows[0]["cash"] + s["price"] * quantity   #update balance
        db.execute("UPDATE users SET cash= :new WHERE id = :id", new = new_cash, id=session["user_id"])
        db.execute("INSERT INTO history (user, stock, quantity, price, datetime) VALUES (:user, :stock, :quantity, :price, :datetime)",
            user = rows[0]["username"], stock=request.form.get("symbol"), quantity=-quantity, price=s["price"],
            datetime =strftime("%Y-%m-%d %H:%M:%S", localtime()) )

        flash ("Sold!")

        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", stocks = stocks)

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
