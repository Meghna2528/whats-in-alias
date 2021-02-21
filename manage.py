import os

from flask import Flask, render_template, request, redirect

from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "urlshortener.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class urlShortener(db.Model):
    original_url = db.Column(db.String(30), unique=True, primary_key=True)
    shortened_url = db.Column(db.String(10), unique=True)

    def __repr__(self):
        return (
            "urlShortener(original_url=%s, shortened_url=%s)"
            % (self.original_url, self.shortened_url)
        )

@app.route('/', methods=["GET", "POST"])
def insert():
    urls = None
    if request.form:
        try:
            original_url = request.form.get("original_url")
            shortened_url = request.form.get("shortened_url")
            url = urlShortener(shortened_url=shortened_url, original_url=original_url)
            print('url: ', url)
            db.session.add(url)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return "Failed to add url. Please check your inputs, and avoid duplicate values."
    urls = urlShortener.query.all()
    return render_template("urlshortener.html",urls=urls)

@app.route("/update", methods=["POST"])
def update():
    try:
        data = dict(request.form)
        original_url = data.get('original_url')
        new_shortened_url = data.get('new_shortened_url')
        url = urlShortener.query.filter_by(original_url=original_url).first()
        url.shortened_url = new_shortened_url
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return ("Couldn't update url alias")
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    data = dict(request.form)
    print('data', data)
    original_url = data.get("original_url")
    url = db.session.query(urlShortener).filter(urlShortener.original_url==original_url).delete()
    print('url', url)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
