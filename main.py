from datetime import date
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from threading import Thread

from helpers import apology, login_required

# Configure application
app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dp.db")

itemlist = ["PURE GHEE U LAND 12*800G", "CHICKEN FRANK SPRME 24*340G",
    "EGG FRESH KHADI 12X30", "ALRAED RBD PALM OLEIN",
    "NO 7 CHANA AL AMEIN/AL TAWAQ 15KG", "HOT SAUCE GLORIA 12X474 ML",
    "7 OZ TEA CUP MODERN 20X50 PCS", "VINEGAR MAMIA (WHITE) 24X473 ML",
    "THAHINA LIQUID JOHRA 10KG", "LIPTON TEA CATERING 36X100 PCS", "PEPSI CAN",
    "CITRUS CAN", "DEW CAN", "ORANGE CAN", "7UP CAN", "STRAWBERRY CAN",
    "LIGHT PEPSI CAN", "SUGAR SAUDI 50KG", "KETCHUP BAIDAR 4X5KG",
    "RABEA ORANGE JUICE 30X250ML", "YASMIN E-Z PACK SLICE 8X160PC",
    "KUWAITY FLOUR 10X1 KG", "LOOSE BLACK PEPPER POWDER 1KG",
    "TOMATO PASTE LUNA 24X400GM", "A-1 CURRY POWDER 24X400GM POUCH",
    "1000 PCS SS BAG RAHIMA", "TEA CUP 20X50 PCS",
    "ALU FOIL MAGIC 6X300MM 1KG", "PLASTIC CUP 10OZ CLEAR 20X50",
    "OMELLA MILK BIG 48X405ML", "MAYONNAISE MAMIA 12X946 ML",
    "PUCK CHEESE 6X500 GM", "VINAYLE GLOVES 10*70 - LARGE",
    "VINAYLE GLOVES 10*70 - X LARGE", "SUGAR YELLOW 10KG", "SANDWICH PAPER 'MRS' ",
    "JEERAKASHALA INDIATOWER 10KG", "HI TEA ZIPPER PKT",
    "HAI JAM BOTTLE STRAWBERRY", "PEANUT BUTTER PEEP 1KG",
    "RICE BASMATI GREEN FARM 10KG", "NAPCO BURGER FOIL 5X500PCS",
    "SALT BAG 4KG", "SASA SALT 24X737", "NESCAFE CLASSIC 12X200GM",
    "PLASTIC FORK FALCON 20X50PC", "RICE PARMAL INDIA SHIP 40KG",
    "FAIRY BIG LEMON 12X1 LTR", "SUFRA ROLL NAHLA CTN",
    "RKG PURE GHEE 12X1LTR", "BROASTED POWDER 12X1KG", "CHICKEN FRANK SADIA",
    "LOOSE SODA POWDER 1KG", "MAYONAISE GOODY 1KG",
    "TRASH BAG HMC 50g x 10pkt", "SHANI CAN", "1000 PC SS BAG NAHLA",
    "TANG ORANGE TIN-6*2KG", "NAKKANAK SADIYA",
    "DEMITA CLING FILM SMALL 6*300MTR", "PLASTIC CUP 10 OZ CLEAR 20*50",
    "PAPPER COATING  STROW 40*250PC", "NO 9 CHANA JAMEEL 15 KG",
    "SAUSE GLORIA GALONE", "SHAMS SUN OIL BIG 4*2.9LTR",
    "HOT PACK ALU FOIL 6*30*150M", "ALSI CAN 30*250ML SADA", "PEANUT BUTTER ORBIX-12*1 KG"
]


@app.route("/")
def index():
    if not session:
        return render_template("index.html")
    else:
        return redirect("/additem")


@app.route("/meez")
def meez():
  return render_template("meez.html")

@app.route("/pursale", methods=["GET", "POST"])
@login_required
def pursale():
    if request.method == "GET":
        return render_template("pursale.html")
    else:
        sale = request.form.get("sale")
        purchase = request.form.get("purchase")
        tdate = request.form.get("date")
        db.execute(
            "DELETE FROM pursale WHERE user_id = ? AND dt = ?",
            session["user_id"], tdate)
        if sale.replace('.', '', 1).isdigit() == False or purchase.replace(
                '.', '', 1).isdigit() == False:
            flash("Enter all details")
            return redirect("/pursale")
        sale = float(sale)
        salevat = sale-(sale*100)/115
        purchase = float(purchase)
        purvat = purchase-(purchase*100)/115
        db.execute(
            "INSERT INTO pursale(user_id, sales, salevat, purchase, purvat, dt) VALUES(?,?,?,?,?,?)",
            session["user_id"], sale-salevat, salevat, purchase, purvat, tdate)
        return redirect("/pursale")


@app.route("/vatview", methods=["GET", "POST"])
@login_required
def pursaleview():
    mlist = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]
    if request.method == "GET":
        return render_template("vatview.html", mlist=mlist)
    else:
        month = request.form.get("month")
        year = request.form.get("year")
        if not month or not year:
            flash("Forgot to enter year or month")
            return redirect("/vatview")

        if int(month) < 10:
            month = '0' + month
        details = db.execute(
            "SELECT * FROM pursale WHERE user_id = ? AND strftime('%m', dt) = ? AND strftime('%Y', dt) = ? ORDER BY strftime('%d', dt)",
            session["user_id"], month, year)
        if len(details) == 0:
            return apology("No entries in that month or selected year")
        total = db.execute(
            "SELECT sum(sales) AS sums, sum(purchase) AS sump, sum(salevat) AS sumsv, sum(purvat) AS sumpv FROM pursale WHERE user_id = ? AND strftime('%m', dt) = ? AND strftime('%Y', dt) = ?",
            session["user_id"], month, year)
        sump = total[0]["sump"]-total[0]["sumpv"]
        sumpv = total[0]["sumpv"]
        sums = total[0]["sums"]-total[0]["sumsv"]
        sumsv = total[0]["sumsv"]
        vat = (sums - sump) + (sumsv - sumpv)
        vats = round((vat - vat * 0.15) * 0.15, 2)
        return render_template("vatviewprint.html",
                               details=details,
                               sales=total[0]["sums"],
                               purchase=sump,
                               vats=vats,
                               month=mlist[int(month) - 1])


@app.route("/additem", methods=["GET", "POST"])
@login_required
def addItem():
    if request.method == "GET":
        return render_template("additem.html", itemlist=itemlist)
    else:
        item = request.form.get("item")
        qty = request.form.get("qty")
        db.execute(
            "INSERT INTO list (user_id, item, qty, dt) values(?, ?, ?, ?)",
            session["user_id"], item, qty, date.today())
        return redirect("/additem")


@app.route("/itemlist", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "GET":
        return render_template("date.html")
    else:
        chosendate = request.form.get("date")
        lists = db.execute(
            "SELECT * FROM list WHERE user_id = ? AND date(dt) == date(?)",
            session["user_id"], chosendate)
        if len(lists) == 0:
            flash("No items added today or invalid date")
            return redirect("/itemlist")
        username = db.execute("SELECT * FROM users WHERE id = ?",
                              session["user_id"])
        return render_template("itemlist.html", lists=lists, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/additem")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Store name in name and password in db and check if previously exist
        name = request.form.get("username")
        prev = db.execute(
            "SELECT EXISTS(SELECT * FROM users WHERE username = ?) ", name)
        prev = [i for i in prev[0].items()]
        if prev[0][1] or not name:
            return apology("Username invalid or not available")

        # Check if passwords match
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not password or password != confirm:
            return apology("Password invalid")

        # Store the details in the database
        else:
            hash = generate_password_hash(password,
                                          method='pbkdf2:sha256',
                                          salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name,
                       hash)
            flash("User had been registered successfully!")
            return redirect("/login")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    # Run the Flask app
    t = Thread(target=app.run(host='0.0.0.0', port=8080, debug=True))
    t.start()
