import os
import csv
import io
from datetime import datetime, date, timedelta
from ml.services.predictor import predict_aspect, predict_sentiment



from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


# -------------------------
# Basic Setup
# -------------------------
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "instance", "database.db")

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -------------------------
# Database Models
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(120))


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    mess = db.Column(db.String(64), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(200), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(64), nullable=False)
    mess = db.Column(db.String(64), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.String(1000))

    predicted_aspect = db.Column(db.String(50))
    predicted_sentiment = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(64), nullable=False)
    mess = db.Column(db.String(64), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)


# -------------------------
# Helper
# -------------------------
def today():
    return date.today()


# Case & space-insensitive mess matching
def get_menu_for(mess, meal_type):
    normalized_mess = mess.replace(" ", "").lower()

    return (
        MenuItem.query
        .filter(
            func.replace(func.lower(MenuItem.mess), " ", "") == normalized_mess,
            func.lower(MenuItem.meal_type) == meal_type.lower(),
            MenuItem.date == today(),
        )
        .order_by(MenuItem.position)
        .all()
    )




# -------------------------
# Routes — Student Side
# -------------------------
@app.route("/")
def index():
    blue_dove_star = (
        db.session.query(Vote.item_name, func.avg(Vote.rating).label("avg_rating"))
        .filter(Vote.mess == "Blue Dove")
        .group_by(Vote.item_name)
        .order_by(func.avg(Vote.rating).desc())
        .first()
    )

    quess_star = (
        db.session.query(Vote.item_name, func.avg(Vote.rating).label("avg_rating"))
        .filter(Vote.mess == "Quess")
        .group_by(Vote.item_name)
        .order_by(func.avg(Vote.rating).desc())
        .first()
    )

    return render_template(
        "index.html",
        blue_dove_star=blue_dove_star[0] if blue_dove_star else None,
        quess_star=quess_star[0] if quess_star else None,
    )


@app.route("/select_mess")
def select_mess():
    mess = request.args.get("mess")
    return render_template("select_mess.html", mess=mess)


@app.route("/login", methods=["GET", "POST"])
def login():
    mess = request.args.get("mess") or request.form.get("mess")

    if request.method == "POST":
        reg_no = request.form["reg_no"].strip()

        if not reg_no:
            flash("Enter your registration number!", "error")
            return redirect(request.url)

        user = User.query.filter_by(reg_no=reg_no).first()
        if not user:
            user = User(reg_no=reg_no)
            db.session.add(user)
            db.session.commit()

        session["reg_no"] = reg_no
        session["mess"] = mess.replace(" ", "").lower()
        return redirect(url_for("choose_meal"))

    return render_template("login.html", mess=mess)


@app.route("/choose_meal")
def choose_meal():
    if "reg_no" not in session:
        return redirect(url_for("index"))

    normalized_mess = session.get("mess")
    display_mess = "Blue Dove" if normalized_mess == "bluedove" else "Quess"

    return render_template("choose_meal.html", mess=display_mess)


@app.route("/menu/<meal_type>", methods=["GET", "POST"])
def menu(meal_type):
    if "reg_no" not in session:
        return redirect(url_for("index"))
    
    print("DEBUG SESSION MESS =", session.get("mess"))
    print("DEBUG MEAL TYPE =", meal_type)

    normalized_mess = session.get("mess")
    display_mess = "Blue Dove" if normalized_mess == "bluedove" else "Quess"
    items = get_menu_for(normalized_mess, meal_type)

    if request.method == "POST":
        reg_no = session["reg_no"]

        for key in request.form:
            if key.startswith("rating_"):
                item_id = int(key.split("_", 1)[1])
                rating = int(request.form.get(key))
                feedback_text = request.form.get(
                    f"feedback_{item_id}", ""
                ).strip()

                item = MenuItem.query.get(item_id)
                if item:
                    vote = Vote(
                        reg_no=reg_no,
                        mess=normalized_mess,
                        meal_type=meal_type,
                        item_name=item.item_name,
                        rating=rating,
                        feedback=feedback_text,
                    )
                    db.session.add(vote)

                    predicted_aspect = predict_aspect(feedback_text)
                    vote.predicted_aspect = predicted_aspect
                    predicted_sentiment = predict_sentiment(feedback_text)
                    vote.predicted_sentiment = predicted_sentiment


        suggestion_text = request.form.get("suggestion_text", "").strip()
        if suggestion_text:
            suggestion = Suggestion(
                reg_no=reg_no,
                mess=normalized_mess,
                text=suggestion_text,
            )
            db.session.add(suggestion)

        db.session.commit()
        return redirect(url_for("thankyou"))

    print("MEAL TYPE:", meal_type)
    print("MENU ITEMS FOUND:", [i.item_name for i in items])

    return render_template(
        "menu.html",
        mess=display_mess,
        meal_type=meal_type,
        items=items,
    )


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# -------------------------
# Routes — Admin Side
# -------------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (
            request.form["username"] == "admin"
            and request.form["password"] == "admin123"
        ):
            session["admin"] = True
            return redirect(url_for("admin_menus"))
        else:
            flash("Invalid credentials", "error")

    return render_template("admin_login.html")


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return wrapped


@app.route("/admin/menus", methods=["GET", "POST"])
@admin_required
def admin_menus():
    if request.method == "POST":
        mess = request.form.get("mess", "").strip()
        normalized_mess = mess.replace(" ", "").lower()
        meal_type = request.form.get("meal_type", "").strip().lower()

        if not mess or not meal_type:
            flash("Please select mess and meal type.", "error")
            return redirect(url_for("admin_menus"))

        MenuItem.query.filter(
            MenuItem.mess == normalized_mess,
            func.lower(MenuItem.meal_type) == meal_type,
            MenuItem.date == today(),
        ).delete()

        for pos in (1, 2, 3):
            name = request.form.get(f"meal{pos}", "").strip()
            if name:
                mi = MenuItem(
                    date=today(),
                    mess=normalized_mess,
                    meal_type=meal_type,
                    position=pos,
                    item_name=name.strip(),
                )
                db.session.add(mi)

        db.session.commit()
        flash(
            f"{mess} — {meal_type.title()} menu uploaded successfully!",
            "success",
        )
        return redirect(url_for("admin_menus", mess=mess))

    selected_mess = request.args.get("mess", "Blue Dove")
    normalized_mess = selected_mess.replace(" ", "").lower()

    menus = (
        MenuItem.query
        .filter_by(date=today(), mess=normalized_mess)
        .order_by(MenuItem.meal_type, MenuItem.position)
        .all()
    )

    return render_template(
        "admin_menus.html",
        menus=menus,
        selected_mess=selected_mess,
    )


@app.route("/admin/suggestions")
@admin_required
def admin_suggestions():
    suggestions = (
        db.session.query(
            Suggestion.text,
            func.count(Suggestion.id).label("cnt"),
        )
        .group_by(Suggestion.text)
        .order_by(func.count(Suggestion.id).desc())
        .all()
    )

    return render_template(
        "suggestions_view.html",
        suggestions=suggestions,
    )


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    meal_averages_query = (
        db.session.query(
            Vote.meal_type,
            func.avg(Vote.rating).label("avg_rating"),
        )
        .group_by(Vote.meal_type)
        .all()
    )

    meal_averages = [
        (m.meal_type, round(m.avg_rating, 2))
        for m in meal_averages_query
    ]

    dish_averages_query = (
        db.session.query(
            Vote.item_name,
            func.avg(Vote.rating).label("avg_rating"),
        )
        .group_by(Vote.item_name)
        .order_by(func.avg(Vote.rating).desc())
        .all()
    )

    dish_averages = [
        (d.item_name, round(d.avg_rating, 2))
        for d in dish_averages_query
    ]

    star_meal = dish_averages[0][0] if dish_averages else None

    return render_template(
        "admin_dashboard.html",
        meal_averages=meal_averages,
        dish_averages=dish_averages,
        star_meal=star_meal,
    )


@app.route("/admin/export")
@admin_required
def admin_export():
    si = io.StringIO()
    cw = csv.writer(si)

    cw.writerow(
        [
            "reg_no",
            "mess",
            "meal_type",
            "item_name",
            "rating",
            "feedback",
            "date",
        ]
    )

    votes = Vote.query.order_by(Vote.date.desc()).all()
    for v in votes:
        cw.writerow(
            [
                v.reg_no,
                v.mess,
                v.meal_type,
                v.item_name,
                v.rating,
                v.feedback or "",
                v.date.isoformat(),
            ]
        )

    output = io.BytesIO()
    output.write(si.getvalue().encode())
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        download_name="votes_export.csv",
        as_attachment=True,
    )


@app.route("/choose_login/<mess>")
def choose_login(mess):
    return render_template("choose_login.html", mess=mess)

@app.route("/admin/aspect_summary")
@admin_required
def admin_aspect_summary():
    """
    Aspect-wise complaint breakdown with sentiment distribution.
    """

    votes = Vote.query.filter(
        Vote.predicted_aspect.isnot(None)
    ).all()

    if not votes:
        return render_template(
            "admin_aspect_summary.html",
            aspect_data=None,
            student_summary=None,
            sentiment_data=None
        )

    # -----------------------------------
    # STEP 1: Build stats dictionary
    # -----------------------------------
    aspect_stats = {}

    for vote in votes:
        aspect = vote.predicted_aspect
        sentiment = vote.predicted_sentiment or "neutral"

        if aspect not in aspect_stats:
            aspect_stats[aspect] = {
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }

        aspect_stats[aspect]["total"] += 1

        if sentiment in ["positive", "neutral", "negative"]:
            aspect_stats[aspect][sentiment] += 1

    # -----------------------------------
    # STEP 2: Calculate percentages
    # -----------------------------------
    grand_total = sum(data["total"] for data in aspect_stats.values())

    aspect_data = []
    sentiment_data = {}

    for aspect, data in aspect_stats.items():
        percentage = round((data["total"] / grand_total) * 100, 1)

        aspect_data.append({
            "aspect": aspect,
            "total": data["total"],
            "percentage": percentage,
        })

        total_aspect = data["total"]

        sentiment_data[aspect] = {
            "positive": round((data["positive"] / total_aspect) * 100, 1) if total_aspect else 0,
            "neutral": round((data["neutral"] / total_aspect) * 100, 1) if total_aspect else 0,
            "negative": round((data["negative"] / total_aspect) * 100, 1) if total_aspect else 0,
        }

    # Sort by highest complaint %
    aspect_data.sort(key=lambda x: x["percentage"], reverse=True)

    # -----------------------------------
    # STEP 3: Intelligent Summary
    # -----------------------------------
    filtered = [a for a in aspect_data if a["aspect"] != "other"]

    if filtered:
        top = filtered[0]
    else:
        top = aspect_data[0]

    top_sentiments = sentiment_data[top["aspect"]]

    negative_percent = top_sentiments["negative"]
    positive_percent = top_sentiments["positive"]

    if negative_percent >= 60:
        severity = "⚠️ Critical issue — Immediate action required."
    elif negative_percent >= 40:
        severity = "⚡ Moderate concern — Needs monitoring."
    elif positive_percent > negative_percent:
        severity = "✅ Under control — Mostly positive feedback."
    else:
        severity = "Mixed feedback — Requires observation."

    student_summary = (
        f"The biggest issue right now is {top['aspect']}. "
        f"It represents {top['percentage']}% of all complaints. "
        f"{severity}"
    )

    return render_template(
        "admin_aspect_summary.html",
        aspect_data=aspect_data,
        sentiment_data=sentiment_data,
        student_summary=student_summary
    )





@app.route("/admin/weekly_report")
@admin_required
def weekly_report():
    today_date = date.today()
    week_ago = today_date - timedelta(days=7)

    votes = (
        db.session.query(
            Vote.mess,
            Vote.meal_type,
            Vote.item_name,
            func.avg(Vote.rating).label("avg_rating"),
            func.count(Vote.id).label("total_votes"),
        )
        .filter(Vote.date >= week_ago)
        .group_by(Vote.mess, Vote.meal_type, Vote.item_name)
        .order_by(func.avg(Vote.rating).desc())
        .all()
    )

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(
        ["Mess", "Meal Type", "Item Name", "Average Rating", "Total Votes"]
    )

    for v in votes:
        cw.writerow(
            [
                v.mess,
                v.meal_type,
                v.item_name,
                round(v.avg_rating, 2),
                v.total_votes,
            ]
        )

    output = io.BytesIO()
    output.write(si.getvalue().encode())
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        download_name="weekly_report.csv",
        as_attachment=True,
    )


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)
