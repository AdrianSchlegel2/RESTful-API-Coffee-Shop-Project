from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import Column, String, Boolean, Integer


app = Flask(__name__)
API_KEY = "MYSECRETKEY"


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    map_url = Column(String(500), nullable=False)
    img_url = Column(String(500), nullable=False)
    location = Column(String(250), nullable=False)
    seats = Column(String(250), nullable=False)
    has_toilet = Column(Boolean, nullable=False)
    has_wifi = Column(Boolean, nullable=False)
    has_sockets = Column(Boolean, nullable=False)
    can_take_calls = Column(Boolean, nullable=False)
    coffee_price = Column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(
        cafe=[cafe.to_dict() for cafe in cafes]
    )


@app.route("/search", methods=["GET"])
def search_cafe():
    location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location).all()
    if cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a Cafe at this location"
        })


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    cafes = db.session.query(Cafe).all()
    cafe_length = len(cafes)
    new_cafe = Cafe(
        id=cafe_length + 1,
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH", "GET"])
def update_price(cafe_id):
    price = request.args.get("new_price")
    try:
        cafe = Cafe.query.filter_by(id=cafe_id).first()
        cafe.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully changed the coffee price."})
    except AttributeError:
        return jsonify(response={"Error 404": "No coffee shop has this ID in the Database"})


@app.route("/report-closed/<int:cafe_id>", methods=["GET", "DELETE"])
def report_closed(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == API_KEY:
        try:
            cafe = Cafe.query.filter_by(id=cafe_id).first()
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the Coffee Shop from the Database."})
        except AttributeError:
            return jsonify(response={"Error 404": "No coffee shop has this ID in the Database"})
    else:
        return jsonify(response={"Error 403": "You are not permitted to complete this action."})


if __name__ == '__main__':
    app.run(debug=True)
