from flask import Flask, render_template, request, redirect
import sqlite3
import random

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    cursor.execute("SELECT DISTINCT year FROM movies")
    years = cursor.fetchall()

    filtered_movies = []
    selected_year = request.form.get("year", "-")

    cursor.execute("""SELECT id, title, duration, metascore, age_rating, year 
        FROM movies
        WHERE 1 = 1 """ + (f"AND year = '{selected_year}'" if selected_year != "-" else ""))
    filtered_movies = cursor.fetchall()

    if selected_year != "-":
        cursor.execute("SELECT AVG(metascore), MIN(metascore), MAX(metascore) FROM movies WHERE year = ?", (selected_year,))
        metascore_analysis = cursor.fetchone()
    else:
        cursor.execute("SELECT AVG(metascore), MIN(metascore), MAX(metascore) FROM movies")
        metascore_analysis = cursor.fetchone()
    
    avg_metascore, min_metascore, max_metascore = metascore_analysis

    return render_template(
        'index.html',
        years=years,
        movies=filtered_movies,
        selected_year=selected_year,
        avg_metascore=avg_metascore,
        min_metascore=min_metascore,
        max_metascore=max_metascore
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

@app.route('/delete_movie', methods=["GET"])
def remove_movie():
    arg = request.args.get('id', default=None, type=int)
    if arg:
        cursor.execute('DELETE FROM movies WHERE id = ?', (arg,))
        conn.commit()
    return redirect("/")

@app.route('/best_and_worst', methods=["GET"])
def best_and_worst():
    cursor.execute("SELECT id, title, duration, metascore, age_rating, year FROM movies WHERE metascore != 'none' AND metascore IS NOT NULL ORDER BY metascore DESC LIMIT 15")
    best_movies = cursor.fetchall()

    cursor.execute("SELECT id, title, duration, metascore, age_rating, year FROM movies WHERE metascore != 'none' AND metascore IS NOT NULL ORDER BY metascore ASC LIMIT 15")
    worst_movies = cursor.fetchall()

    combined_movies = best_movies + worst_movies
    random.shuffle(combined_movies)

    return render_template(
        'best_and_worst.html',
        movies=combined_movies
    )

if __name__ == "__main__":
    app.run()
