from flask import Flask, render_template, request
from flask import send_file
from docx import Document
from io import BytesIO
import psycopg2,logging

dbcon = psycopg2.connect(
        user='rwozksuc',
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc',
        host='john.db.elephantsql.com')

app = Flask(__name__)

@app.route("/")
def form():
    return render_template('Car_search.html')

@app.route("/download")
def download_doc():
    
    document = Document()
    f = BytesIO()
    # do staff with document
    document.save(f)
    f.seek(0)

    return send_file(
        f,
        as_attachment=True,
        attachment_filename='car_doc.docx'
    )


@app.route("/car/<int:id>")
def car(id):
    cur = dbcon.cursor()

    cur.execute("SELECT * FROM cars WHERE id=%s", (id,))

    car = cur.fetchone()
    cur.close()

    return render_template('Car.html', car=car)
   

@app.route("/results", methods=['GET', 'POST'])
def results():
    app.logger.info(request.form)
    if request.method == 'POST':
        company = request.form.get('company')

        price_starting = float(request.form.get('price_starting'))
        price_topend = float(request.form.get('price_topend'))

        manual = request.form.get('manual')
        if manual:
            manual = True

        automatic = request.form.get('automatic')
        if automatic:
            automatic = True

        petrol = request.form.get('petrol')
        if petrol:
            petrol = True

        diesel = request.form.get('diesel')
        if diesel:
            diesel = True

        cng = request.form.get('cng')
        if cng:
            cng = True

        electric = request.form.get('electric')
        if electric:
            cng = electric

        seating_capacity = int(request.form.get('seating_capacity'))

        car_sql = """
            SELECT id, name, company, image, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity
            FROM cars
            WHERE company = %s
                AND price_starting > %s 
                AND price_topend < %s
                AND manual = COALESCE(%s, manual)
                AND automatic = COALESCE(%s, automatic)
                AND petrol = COALESCE(%s, petrol)
                AND diesel = COALESCE(%s, diesel)
                AND cng = COALESCE(%s, cng)
                AND electric = COALESCE(%s, electric)
                AND seating_capacity = %s;
                """

        car_params = (company, price_starting, price_topend, manual, automatic, petrol, diesel, cng, electric, seating_capacity)

        cur = dbcon.cursor()

        cur.execute(car_sql, car_params)

        cars = cur.fetchall()

        cur.execute("SELECT * FROM company WHERE name=%s", (company,))   

        company = cur.fetchone()

        app.logger.info(company)
        return render_template("Home.html", company=company,cars=cars)

if __name__ == "__main__":
    app.run(debug=True)
    dbcon.close()


