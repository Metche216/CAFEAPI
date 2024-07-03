from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        
        dictionary = {}
        
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
            
        return dictionary
    
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record

@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes).to_dict()
    return jsonify(cafe=random_cafe)
    
@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Note, this may get more than one cafe per location
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add_cafe():
    with app.app_context():
        new_cafe = Cafe(
            name = request.form.get("name"), 
            map_url = request.form.get("map_url"), 
            img_url = request.form.get("img_url"), 
            location = request.form.get("location"), 
            seats = request.form.get("seats"),
            has_toilet = bool(request.form.get("has_toilet")), 
            has_wifi = bool(request.form.get("has_wifi")),
            has_sockets = bool(request.form.get("has_sockets")), 
            can_take_calls = bool(request.form.get("can_take_calls")), 
            coffee_price = request.form.get("coffee_price"), 
        )
        print(new_cafe)
        db.session.add(new_cafe)
        
        db.session.commit()
        
        return jsonify(response={
            "success":"successfully added a new Cafe"
        })
    
# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    element_to_update = db.get_or_404(Cafe,cafe_id)
    if element_to_update:
        element_to_update.coffee_price = request.args.get('coffee_price')
        db.session.commit()
        return jsonify(response={"success":"successfully updated coffee price"}), 200
    else:
        return jsonify( error = {"Not Found: Sorry, a cafe with that id was not found in our database"}), 404
# HTTP DELETE - Delete Record
API_KEY = "TopSecretAPIKey"
@app.route("/report_closed/<cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    element_to_delete = db.get_or_404(Cafe, cafe_id)
    if request.args.get('api_key') == API_KEY:
        db.session.delete(element_to_delete)
        db.session.commit()
        return jsonify(response={"success":"successfully deletede the Cafe reported closed"}), 200
    else:
        return jsonify( error = {"Not Found": "Sorry, you are not allowed to perform this action. Make sure you have the correct api_key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
