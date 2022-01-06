from flask import Flask, render_template, request, make_response, abort
import psycopg2
import psycopg2.extras
import json
from decimal import Decimal

dbcon = psycopg2.connect(
        user='rwozksuc',
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc',
        host='john.db.elephantsql.com')

app = Flask(__name__)

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

@app.route("/")
def form():
    return render_template('Car_search.html')

@app.route("/car/<int:id>")
def car(id):
    cur = dbcon.cursor()

    cur.execute("SELECT * FROM cars WHERE id=%s", (id,))

    car = cur.fetchone()

    cur.execute("SELECT * FROM company WHERE name=%s", (car[2],))

    company = cur.fetchone()

    cur.close()

    return render_template('Car.html', company=company, car=car)

@app.route("/results", methods=['GET', 'POST'])
def results():
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

        return render_template("Home.html", company=company,cars=cars)

#API routes
@app.errorhandler(400)
def not_found(error):
    r = make_response(json.dumps({ 'error': 'Bad request' }), 400)
    r.mimetype = 'application/json'
    return r

@app.errorhandler(404)
def not_found(error):
    r = make_response(json.dumps({'error': 'Not found'}), 404)
    r.mimetype = 'application/json'
    return r

@app.route('/api/cars')
def get_cars():
    cur = dbcon.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select * from cars')
    cars = cur.fetchall()
    cur.close()

    r = make_response(json.dumps({'cars': cars}, default=default))
    r.mimetype = 'application/json'
    return r

@app.route('/api/cars', methods = ['POST'])
def create_car():
    if not request.json:
        abort(400)
    
    for key in ['name' , 'company' , 'image' , 'summary' , 'price_starting' , 'price_topend' , 'mileage_l' , 'mileage_u' , 'manual' , 'automatic' , 'petrol' , 'diesel' , 'cng' , 'electric' , 'seating']:
        if key not in request.json:
            abort(400)

    car = request.json

    cur = dbcon.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    SQL = '''INSERT INTO cars(name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'''
    
    params = (car['name'], car['company'], car['image'], car['summary'], car['price_starting'], car['price_topend'], car['mileage_l'], car['mileage_u'], car['manual'], car['automatic'], car['petrol'], car['diesel'], car['cng'], car['electric'], car['seating'])

    cur.execute(SQL, params)

    id = cur.fetchone()['id']
    cur.execute('SELECT * FROM cars WHERE id=%s', (id,))
    car = cur.fetchone()
    cur.close()

    dbcon.commit()
    
    r = make_response(json.dumps(car, default=default), 201)
    r.mimetype = 'application/json'
    return r

@app.route('/api/cars/<int:id>')
def get_car(id):
    cur = dbcon.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select * from cars where id=%s', (id,))
    car = cur.fetchone()
    cur.close()

    if car is None:
        abort(404)

    r = make_response(json.dumps(car, default=default))
    r.mimetype = 'application/json'
    return r

@app.route('/api/cars/<int:id>', methods = ['DELETE'])
def delete_car(id):
    cur = dbcon.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select * from cars where id=%s', (id,))
    car = cur.fetchone()

    if car is None:
        abort(404)

    cur.execute('delete from cars where id=%s', (id,))
    cur.close()

    return '', 204

@app.route('/api/cars/<int:id>', methods = ['PUT'])
def update_car(id):
    if not request.json:
        abort(400)
    
    for key in ['name' , 'company' , 'image' , 'summary' , 'price_starting' , 'price_topend' , 'mileage_l' , 'mileage_u' , 'manual' , 'automatic' , 'petrol' , 'diesel' , 'cng' , 'electric' , 'seating']:
        if key not in request.json:
            abort(400)

    cur = dbcon.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select * from cars where id=%s', (id,))
    car = cur.fetchone()

    if car is None:
        abort(404)

    car = request.json

    SQL = '''
        UPDATE cars 
            SET name=%s,
                company=%s, 
                image=%s, 
                summary=%s, 
                price_starting=%s, 
                price_topend=%s, 
                mileage_l=%s, 
                mileage_u=%s, 
                manual=%s, 
                automatic=%s, 
                petrol=%s, 
                diesel=%s,
                cng=%s, 
                electric=%s, 
                seating_capacity=%s
            WHERE id=%s
    '''
    params = (car['name'], car['company'], car['image'], car['summary'], car['price_starting'], car['price_topend'], car['mileage_l'], car['mileage_u'], car['manual'], car['automatic'], car['petrol'], car['diesel'], car['cng'], car['electric'], car['seating'], id)

    cur.execute(SQL, params)
    cur.close()

    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
    dbcon.close()
