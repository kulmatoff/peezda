from flask import Flask, render_template, request
import sqlite3

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    cursor.execute("SELECT DISTINCT year FROM movies")
    years = cursor.fetchall()

    filtered_movies = []
    selected_year = request.form.get("year", "-")

    cursor.execute("""SELECT title, duration, metascore, age_rating, year 
        FROM movies
        WHERE 1 = 1 """ + (f"AND year = '{selected_year}'" if selected_year != "-" else ""))
    filtered_movies = cursor.fetchall()

    return render_template(
        'index.html',
        years=years,
        movies=filtered_movies,
        selected_year=selected_year
    )

@app.route('/submit', methods=['POST'])
def submit_movie():
    title = request.form['title']
    duration = request.form['duration']
    metascore = int(request.form['metascore'])
    age_rating = request.form['age_rating']
    year = int(request.form['year'])
    cursor.execute('''
        INSERT INTO movies (title, duration, metascore, age_rating, year)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, duration, metascore, age_rating, year))
    conn.commit()

    return render_template("movie_added.html")
    
@app.route('/new_movie', methods=["GET"])
def new_movie():
    return render_template("adding.html")

if __name__ == "__main__":
    app.run()
