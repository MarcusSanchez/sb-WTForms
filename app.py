from flask import Flask, render_template, request, redirect

from WTForms.forms import UpdatePetForm, CreatePetForm
from WTForms.models import connect_db, db, Pets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/adopt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def render_homepage():
    pets = Pets.query.all()
    return render_template("home.jinja2", pets=pets)


@app.route("/add", methods=["GET", "POST"])
def create_pet():
    form = CreatePetForm()
    if not form.validate_on_submit():
        return render_template("create_pet.jinja2", form=form)

    data = {k: v for k, v in form.data.items() if k != "csrf_token"}
    pet = Pets(**data)

    db.session.add(pet)
    db.session.commit()

    return redirect("/")


@app.route('/<int:pet_id>', methods=["GET", "POST"])
def update_pet(pet_id):
    pet = Pets.query.get(pet_id)
    if not pet:
        return render_template("error.jinja2", error="Pet not found")

    form = UpdatePetForm(obj=pet)
    if not form.validate_on_submit():
        return render_template("update_pet.jinja2", form=form, pet=pet)

    for k, v in form.data.items():
        if k == "csrf_token":
            continue
        setattr(pet, k, v)

    db.session.commit()
    return redirect("/")

