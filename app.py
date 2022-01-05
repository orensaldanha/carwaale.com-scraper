from flask import Flask, render_template, request
import psycopg2

dbcon = psycopg2.connect(
        user='rwozksuc',
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc',
        host='john.db.elephantsql.com')

app = Flask(__name__)

@app.route("/")
def form():
    return render_template('Car_search.html')

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        company = request.form.get('company')
        if len(company) == 0:
            company = None

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

        SQL = """
            SELECT id, name, company, image, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity
            FROM cars
            WHERE company = COALESCE(%s, company)
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

        params = (company, price_starting, price_topend, manual, automatic, petrol, diesel, cng, electric, seating_capacity)

        cur = dbcon.cursor()

        cur.execute(SQL, params)

        cars = cur.fetchall()

        app.logger.info(cars)

        return render_template("result.html", cars=cars)

if __name__ == "__main__":
    app.run(debug=True)
    dbcon.close()
