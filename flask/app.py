from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import numpy as np 
import sqlite3

app = Flask(__name__)


def get_db_connection():

    df = pd.read_csv('imdb_top_1000.csv')

    conn = sqlite3.connect("imdb_movies.db")
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        Poster_Link TEXT,
        Series_Title TEXT NOT NULL,
        Released_Year INTEGER,
        Certificate TEXT,
        Runtime TEXT,
        Genre TEXT,
        IMDB_Rating REAL,
        Overview TEXT,
        Meta_score REAL,
        Director TEXT,
        Star1 TEXT,
        Star2 TEXT,
        Star3 TEXT,
        Star4 TEXT,
        No_of_Votes INTEGER,
        Gross TEXT
    )
    ''')

    df.to_sql('movies', conn, if_exists='replace', index=False)
    conn.commit()
    
    return conn  



@app.route('/', methods=['GET', 'POST'])
def index():
    query = 'SELECT * FROM movies'
    params = []

    title = request.form.get('title')
    genre = request.form.get('genre')
    director = request.form.get('director')

    if title or genre or director:
        query += ' WHERE '
        filters = []

        if title:
            filters.append("Series_Title LIKE ?")
            params.append(f"%{title}%")
        if genre:
            filters.append("Genre LIKE ?")
            params.append(f"%{genre}%")
        if director:
            filters.append("Director LIKE ?")
            params.append(f"%{director}%")
        
        query += ' AND '.join(filters)

    conn = get_db_connection()
    movies_df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    movies = movies_df.to_dict(orient='records')

    return render_template('index.html', movies=movies)


@app.route('/top_movies')
def top_movies():
    query = '''
    SELECT * FROM movies
    ORDER BY IMDB_Rating DESC
    LIMIT 10
    '''
    conn = get_db_connection()
    cursor = conn.execute(query)

    column_names = [description[0] for description in cursor.description]
    movies = [dict(zip(column_names, row)) for row in cursor.fetchall()]

    conn.close()

    return render_template('top_movies.html', movies=movies)


if __name__ == '__main__':
    app.run(debug=True)