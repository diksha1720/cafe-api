import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import html

app = Flask(__name__)


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def random_cafe():
    cafes = Cafe.query.all()
    cafe = random.choice(cafes)
    return jsonify(cafe=cafe.to_dict())


@app.route('/all')
def all_cafes():
    cafes = Cafe.query.all()
    return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])


@app.route('/search')
def search_cafes():
    location = request.args.get("loc")
    cafe = Cafe.query.filter_by(location=location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())

    else:
        return jsonify(error={"Not found": "Sorry we don't have a cafe at that location"})


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
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


@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = request.form.get("new_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the coffee price."})
    else:
        return jsonify(error={"Not found": "Sorry a cafe with that id is not found in the database"})


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == 'TopSecretAPIKey':
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."})
        else:
            return jsonify(error={"Not found": "Sorry a cafe with that id is not found in the database"})
    else:
        return jsonify(error={"Not authorized": "The API KEY can't be verified"})


if __name__ == '__main__':
    app.run(debug=True)
