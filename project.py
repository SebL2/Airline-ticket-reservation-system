#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#MAIN HOME PAGE
#--------------
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/flightInformation', methods=['POST'])
def flightInformation():

    source = request.form['source']
    destination = request.form['destination']
    dep_date = request.form['departure'] + "%"
    ret_date = request.form['return']

    cursor1 = conn.cursor()
    query = 'SELECT  * FROM flight WHERE  dep_airport = %s and arrival_airport = %s and dep_date_time LIKE %s'
    cursor1.execute(query,(source,destination,dep_date))
    data1 = cursor1.fetchall()
    cursor1.close()
    if (ret_date!= 'NULL'):
        ret_date += "%"
        cursor2 = conn.cursor()
        query = 'SELECT  * FROM flight WHERE  dep_airport = %s and arrival_airport = %s and dep_date_time LIKE %s'
        cursor2.execute(query,(destination,source,ret_date))
        data2 = cursor2.fetchall()
        cursor2.close()
        return render_template('index.html',data1=data1,data2=data2)
    return render_template('index.html',data1=data1)

#Define route for register
@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/reg_cust')
def reg_cust():
    return render_template('reg_cust.html')

@app.route('/reg_staff')
def reg_staff():
    return render_template('reg_staff.html')

@app.route('/login_staff')
def login_staff():
    return render_template('login_staff.html')

@app.route('/login_cust')
def login_cust():
    return render_template('login_cust.html')


#REGISTRATIONS
#-------------

@app.route('/loginAuthCust', methods=['POST'])
def cust_login():
    email = request.form['email']
    password = request.form['password']
    session['email'] = email
    cursor = conn.cursor()
    query = 'SELECT * FROM Customer WHERE email = %s and password = md5(%s)'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    if(data):
        session['email'] = email
        return render_template('customer_index.html', user = data['name'])
    else:
        error = 'Invalid login or email'
        return render_template('login_cust.html', error=error)

@app.route('/loginAuthStaff', methods=['POST'])
def staff_login():
    username = request.form['username']
    password = request.form['password']
    session['username'] = username
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    if(data):
        session['username'] = username
        session['airline_name'] = data['airline_name']
        return flights_staff()
    else:
        error = 'Invalid login or username'
        return render_template('login_staff.html', error=error)
    
#Authenticates the register
@app.route('/registerAuthCust', methods=['POST'])
def registerAuthCust():
    #grabs information from the forms
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This email is already registered"
        cursor.close()
        return render_template('reg_cust.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        session['email'] = email
        return render_template('customer_index.html', user = name)

@app.route('/registerAuthStaff', methods=['POST'])
def registerAuthStaff():
    username = request.form['username']
    airline_name = request.form['airline_name']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    email = request.form['email']
    phone_number = request.form['phone_number']
    date_of_birth = request.form['date_of_birth']

    cursor = conn.cursor()
    query = 'SELECT * FROM Staff_Email WHERE email = %s'
    cursor.execute(query, (email))
    data1 = cursor.fetchone()
    cursor.close()
    if (data1):
        error = "This email is already in use"
        return render_template('reg_staff.html', error = error)
    else:
        cursor = conn.cursor()
        query = 'SELECT * FROM Phone_Number WHERE phone_num = %s'
        cursor.execute(query, (phone_number))
        data2 = cursor.fetchone()
        cursor.close()
        if (data2):
            error = "This phone number is already in use"
            return render_template('reg_staff.html', error = error)
        else:
            cursor = conn.cursor()
            query = 'SELECT * FROM Airline_Staff WHERE username = %s'
            cursor.execute(query, (username))
            data3 = cursor.fetchone()
            cursor.close()
            if (data3):
                error = "This username is already in use"
                return render_template('reg_staff.html', error = error)
            else:
                cursor = conn.cursor()
                query = 'SELECT * FROM Airline WHERE airline_name = %s'
                cursor.execute(query, (airline_name))
                data4 = cursor.fetchone()
                cursor.close()
                if (data4):
                    cursor = conn.cursor()
                    ins = 'INSERT INTO Airline_Staff VALUES(%s,%s,%s,%s,md5(%s),%s)'
                    cursor.execute(ins,(username,airline_name,first_name,last_name,password,date_of_birth))
                    ins = 'INSERT INTO Staff_Email VALUES(%s,%s)'
                    cursor.execute(ins, (email,username))
                    ins = 'INSERT INTO Phone_number VALUES(%s,%s)'
                    cursor.execute(ins, (phone_number,username))
                    conn.commit()
                    cursor.close()
                    return render_template('index.html')
                else:
                    error = "Airline does not exist"
                    return render_template('reg_staff.html', error = error)

#CUSTOMER
#--------
@app.route('/viewFlights')
def viewFlights():
    try:    
        error = request.args['error']
    except:
        error = None
    try:
        email = session['email']
    except:
        return redirect(url_for("login_cust"))
    cursor = conn.cursor()
    query = "SELECT * FROM (ticket NATURAL JOIN customer),flight WHERE email = %s AND ticket.flight_num = flight.flight_num AND ticket.airline_name = flight.airline_name AND ticket.dep_date_time = flight.dep_date_time "
    user_query = "SELECT name FROM customer WHERE email = %s"
    
    
    cursor.execute(query,(email))
    data = cursor.fetchall()
    current_date_query  = "SELECT CURRENT_TIMESTAMP()"
    cursor.execute(current_date_query)
    curr_date = cursor.fetchone()
    for entry in data:
        if entry['dep_date_time'] < curr_date['CURRENT_TIMESTAMP()']:
            rating = True
        else:
            rating = False
        if entry['dep_date_time']-datetime.timedelta(days=1) > curr_date['CURRENT_TIMESTAMP()']:
            cancel = True
        else:
            cancel = False
        entry['rating'] = rating
        entry['cancel'] = cancel
    cursor.execute(user_query,(email))
    username = cursor.fetchone()
    cursor.close()
    return render_template('customer_flights.html',username = username,email=email,data=data,error=error)

@app.route('/cancelFlight',methods = ['POST'])
def cancelFlight():
    email = session['email']
    ticket_ID = request.form['ID']
    cursor = conn.cursor()
    query = "DELETE FROM ticket WHERE email = %s and ID = %s"
    error = cursor.execute(query,(email,ticket_ID))
    conn.commit()
    cursor.close()
    if(error == False):
        return redirect(url_for('viewFlights', error = error))
    else:    
        return redirect(url_for('viewFlights'))

@app.route('/rateFlight', methods = ['POST'])
def rateFlight():
    cursor = conn.cursor()
    email = session['email']
    airline = request.form['airline_name']
    flight_num = request.form['flight_num']
    dep_date_time = request.form['dep_date_time']
    rating = request.form['Rating']
    comment = request.form['Comment'] 
    exists = "SELECT * FROM rated WHERE email = %s AND airline_name = %s AND flight_num = %s AND dep_date_time = %s"
    cursor.execute(exists,(email,airline,flight_num,dep_date_time))
    checkExists = cursor.fetchall()
    if(checkExists):
        query = "UPDATE rated SET  Rating = %s, Comment = %s   WHERE email = %s AND airline_name = %s AND flight_num = %s AND dep_date_time = %s"
        cursor.execute(query,(rating,comment,email,airline,flight_num,dep_date_time))
    else:
        query = "INSERT INTO rated VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (airline, flight_num, dep_date_time, email, rating, comment))
    
    conn.commit() 
    cursor.close()
    return redirect(url_for('viewFlights'))

@app.route('/flightSearch')
def flightSearch():
    try:
        email = session['email']
    except:
        return redirect(url_for("login_cust"))
    return render_template('customer_search_flights.html')

@app.route('/purchase')
def purchase():
    cursor = conn.cursor()
    try:
        email = session['email']
    except:
        return redirect(url_for("login"))
    query = '''  
            SELECT flight_num, dep_date_time, airline_name,arrival_date_time, dep_airport, arrival_airport, base_price, 0 as tickets_sold, seats
            FROM flight NATURAL JOIN airplane
            WHERE (flight_num, airline_name, dep_date_time) NOT IN (SELECT flight_num,airline_name,dep_date_time FROM ticket) AND dep_date_time > (SELECT CURRENT_TIMESTAMP())

            UNION
   
            SELECT S.flight_num, S.dep_date_time, S.airline_name, S.arrival_date_time, S.dep_airport, S.arrival_airport, base_price, COUNT(*) as tickets_sold, seats
                FROM (flight as S NATURAL JOIN airplane), ticket as R
                WHERE S.flight_num = R.flight_num AND S.dep_date_time = R.dep_date_time AND S.airline_name = R.airline_name AND R.dep_date_time > (SELECT CURRENT_TIMESTAMP()) 
                GROUP BY S.flight_num, S.dep_date_time,S.airline_name,S.arrival_date_time, S.dep_airport, S.arrival_airport
                    HAVING COUNT(*) < (SELECT seats
                        FROM airplane NATURAL JOIN flight as T
                        WHERE T.flight_num = S.flight_num AND T.dep_date_time = S.dep_date_time AND T.airline_name = S.airline_name AND 
                        T.arrival_date_time = S.arrival_date_time AND T.dep_airport = S.dep_airport AND T.arrival_airport = S.arrival_airport)'''
    cursor.execute(query)
    data = cursor.fetchall()
    for entry in data:
        if entry['tickets_sold']/entry['seats'] >= 0.6:
            entry['base_price']*=1.2
    conn.commit()
    return render_template('purchase.html',data=data)

@app.route('/purchaseTicket',methods=['POST'])
def purchaseTicket():
    flight_num = request.form['flight_num']
    airline_name = request.form['airline_name']
    dep_date_time = request.form['dep_date_time']
    print(dep_date_time)
    price = request.form['price']
    return render_template("purchaseTicket.html",flight_num = flight_num, airline_name = airline_name, dep_date_time = dep_date_time,price=price)

@app.route('/finalizePurchase', methods = ['POST'])
def finalizePurchase():
    cursor = conn.cursor()
    email = session['email']
    flight_num = request.form['flight_num']
    airline_name = request.form['airline_name']
    dep_date_time = request.form['dep_date_time']
    price = request.form['price']
    card_type = request.form['card_type']
    card_number = request.form['card_number']
    name = request.form['name_on_card']
    exp_date = request.form['exp_date']
    
    query = "INSERT INTO Ticket VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    ticket_id = 1
    inserted = False
    while not inserted:
        try:
            cursor.execute(query,(ticket_id,email,airline_name,flight_num,dep_date_time,price,card_type,card_number,name,exp_date,datetime.datetime.now()))
            conn.commit()
            inserted = True
        except pymysql.IntegrityError:
            ticket_id += 1
    user_query = "SELECT name FROM customer WHERE email = %s"
    cursor.execute(user_query,(email))    
    data = cursor.fetchone()
    cursor.close()
    return render_template('customer_index.html', user = data['name'])

        
@app.route('/customerLogout')
def customerLogout():
    try:
        email = session['email']
    except: 
        return redirect(url_for("login_cust"))
    session.pop('email')
    return redirect('/login')

#AIRLINE STAFF
#------------
@app.route('/createFlight', methods=['POST'])
def createFlight():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        airplane_id = request.form['airplane_id']
        flight_num = request.form['flight_num']
        dep_airport = request.form['dep_airport']
        arrival_airport = request.form['arrival_airport']
        dep_date_time = request.form['dep_date_time']
        arrival_date_time = request.form['arrival_date_time']
        base_price = request.form['base_price']
        status = request.form['status']
        airline_name = session['airline_name']
        cursor = conn.cursor()
        query = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        try:
            cursor.execute(query, (flight_num, dep_date_time, airline_name, airplane_id, arrival_date_time, arrival_airport, dep_airport, base_price, status))
        except:
            error = 'Error creating flight'
            return flights_staff(error)
        conn.commit()
        cursor.close()
        return flights_staff()
    else:
        return render_template('index.html', message='You are not an authorized staff member')
    
@app.route('/change_status_page')
def change_status_page():
    try:
        user = session['username']
    except:
        return redirect("/")
    return render_template('change_status.html')
    
@app.route('/changeStatus', methods=['POST'])
def changeStatus():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        flight_num = request.form['flight_num']
        dep_date_time = request.form['dep_date_time']
        status = request.form['status']
        cursor = conn.cursor()
        query = 'UPDATE flight SET status = %s WHERE flight_num = %s and dep_date_time = %s and airline_name = %s'
        try:
            cursor.execute(query, (status, flight_num, dep_date_time, session['airline_name']))
        except:
            error = 'Error changing status'
            return flights_staff(error)
        conn.commit()
        cursor.close()
        return flights_staff()
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/add_airplane_page')
def add_airplane_page():
    try:
        user = session['username']
    except:
        return redirect("/")
    return render_template('add_airplane.html')

@app.route('/addAirplane', methods=['POST'])
def addAirplane():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        airplane_id = request.form['ID']
        seats = request.form['seats']
        manufacturer = request.form['manufacturer']
        age = request.form['age']
        cursor = conn.cursor()
        query = 'INSERT INTO airplane VALUES(%s, %s, %s, %s, %s)'
        try:
            cursor.execute(query, (session['airline_name'], airplane_id, seats, manufacturer, age))
        except:
            error = 'Error adding airplane'
            return airplanes(error)
        conn.commit()
        cursor.close()
        return airplanes("Airplane added successfully")
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/airplanes')
def airplanes(msg=''):
    cursor = conn.cursor()
    try:
        user = session['username']
    except:
        return render_template('index.html', message='You are not an authorized staff member')
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    print(data)
    if(data):
        cursor = conn.cursor()
        query = 'SELECT * FROM airplane WHERE airline_name = %s'
        cursor.execute(query, (session['airline_name']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('airplanes.html', data=data, message=msg)
    else:
        return render_template('index.html', message='You are not an authorized staff member')


@app.route('/add_airport_page')
def add_airport_page():
    try:
        user = session['username']
    except:
        return redirect("/")
    return render_template('add_airport.html')

@app.route('/addAirport', methods=['POST'])
def addAirport():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        airport_name = request.form['airport_name']
        city = request.form['city']
        country = request.form['country']
        type = request.form['type']
        cursor = conn.cursor()
        query = 'INSERT INTO airport VALUES(%s, %s, %s, %s)'
        try:
            cursor.execute(query, (airport_name, city, country, type))
        except:
            error = 'Error adding airport'
            return flights_staff(error)
        conn.commit()
        cursor.close()
        return flights_staff()
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/view_flight_ratings_prep')
def view_flight_ratings_prep():
    try:
        user = session['username']
    except:
        return redirect("/")
    return render_template('view_flight_ratings_prep.html')

@app.route('/viewFlightRatings', methods=['POST'])
def viewFlightRatings():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        flight_num = request.form['flight_num']
        dep_date_time = request.form['dep_date_time']
        cursor = conn.cursor()
        query1 = 'SELECT comment, rating FROM rated WHERE flight_num = %s and dep_date_time = %s and airline_name = %s'
        query2 = 'SELECT avg(rating) as avg_rating FROM rated WHERE flight_num = %s and dep_date_time = %s and airline_name = %s group by flight_num, dep_date_time, airline_name'
        cursor.execute(query1, (flight_num, dep_date_time, session['airline_name']))
        data1 = cursor.fetchall()
        cursor.execute(query2, (flight_num, dep_date_time, session['airline_name']))
        data2 = cursor.fetchall()
        cursor.close()
        return render_template('view_flight_ratings.html', ratings=data1, avg_rating=data2)
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/reports')
def reports():
    cursor = conn.cursor()
    try:
        user = session['username']
    except:
        return redirect("/")
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        cursor = conn.cursor()
        query = "SELECT EXTRACT(YEAR FROM purchase_date_time) AS year, EXTRACT(MONTH FROM purchase_date_time) AS month, COUNT(*) AS tickets_sold FROM ticket where airline_name = %s GROUP BY year, month ORDER BY year, month;"
        cursor.execute(query, (session['airline_name']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('reports.html', data=data)
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/searchFlights', methods=['POST'])
def searchFlights():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        dep_airport = request.form['dep_airport']
        arrival_airport = request.form['arrival_airport']
        dep_date_time_beg = request.form['dep_date_time_beg']
        dep_date_time_end = request.form['dep_date_time_end']
        arrival_date_time_beg = request.form['arrival_date_time_beg']
        arrival_date_time_end = request.form['arrival_date_time_end']
        cursor = conn.cursor()
        query = 'SELECT * FROM flight WHERE airline_name = %s'
        inputs=[session['airline_name']]
        if dep_airport:
            query += ' and dep_airport = %s'
            inputs.append(dep_airport)
        if arrival_airport:
            query += ' and arrival_airport = %s'
            inputs.append(arrival_airport)
        if dep_date_time_beg:
            query += ' and dep_date_time >= %s'
            inputs.append(dep_date_time_beg)
        if dep_date_time_end:
            query += ' and dep_date_time <= %s'
            inputs.append(dep_date_time_end)
        if arrival_date_time_beg:
            query += ' and arrival_date_time >= %s'
            inputs.append(arrival_date_time_beg)
        if arrival_date_time_end:
            query += ' and arrival_date_time <= %s'
            inputs.append(arrival_date_time_end)
        cursor.execute(query, inputs)
        data = cursor.fetchall()
        cursor.close()
        return render_template('staff_index.html', flights=data)
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/checkPassengers', methods=['POST'])
def checkPassengers():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        flight_num = request.form['flight_num']
        dep_date_time = request.form['dep_date_time']
        cursor = conn.cursor()
        query = 'SELECT DISTINCT ID, name, email, phone_number FROM ticket NATURAL JOIN customer WHERE flight_num = %s and dep_date_time = %s and airline_name = %s'
        cursor.execute(query, (flight_num, dep_date_time, session['airline_name']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('passengers.html', passengers=data)
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/flights_staff')
def flights_staff(msg=''):
    cursor = conn.cursor()
    try:
        user = session['username']
    except:
        return redirect('/')
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        cursor = conn.cursor()
        query = 'SELECT  * FROM flight WHERE airline_name = %s and dep_date_time > CURRENT_TIMESTAMP() and dep_date_time < CURRENT_TIMESTAMP() + INTERVAL 30 DAY ORDER BY dep_date_time'
        cursor.execute(query, (session['airline_name']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('staff_index.html',flights=data, message=msg)
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/addPhoneNumber', methods=['POST'])
def addPhoneNumber():
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (session['username']))
    data = cursor.fetchall()
    if(data):
        phone_number = request.form['phone_number']
        cursor = conn.cursor()
        query = 'INSERT INTO phone_number VALUES(%s, %s)'
        try:
            cursor.execute(query, (phone_number, session['username']))
        except:
            error = 'Error adding phone number'
            return flights_staff(error)
        conn.commit()
        cursor.close()
        return flights_staff()
    else:
        return render_template('index.html', message='You are not an authorized staff member')

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 3306, debug = True)
