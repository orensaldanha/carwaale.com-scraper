from flask import Flask,render_template
import psycopg2

dbcon = psycopg2.connect(
        user='rwozksuc', 
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc', 
        host='john.db.elephantsql.com')
app = Flask(__name__)

@app.route("/")
def form():
    return render_template('submit.html')

@app.route("/results")
def results():
    cur = dbcon.cursor()

    SQL = """ 
		SELECT *
		FROM cars
		WHERE manual=%s AND automatic=%s"""
    params = (manual, automatic)
    cur.execute(SQL, params)


if __name__=="__main__":
    app.run(debug=True)

