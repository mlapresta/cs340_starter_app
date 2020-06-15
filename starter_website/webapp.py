from flask import Flask, render_template
from flask import request, redirect
from flask_mysqldb import MySQL
from db_credentials import host, user, passwd, db
from db_connector import connect_to_database, execute_query

app = Flask(__name__)

app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = passwd
app.config['MYSQL_DB'] = db
mysql = MySQL(app)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/hello')
def hello_world():
    return 'Hello, World!'


@app.route("/certification", methods=["GET", "POST"])
def browse_add_certifications():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        query = "SELECT title from bsg_cert;"
        cur.execute(query)
        result = cur.fetchall()
        print(result)
        return render_template("certification.html", certifications=result)

    elif request.method == "POST":
        cur = mysql.connection.cursor()
        data = (request.form["certname"],)
        insert_query = "INSERT into `bsg_cert` (title) VALUES (%s)"
        cur.execute(insert_query, data)
        query = "SELECT title from bsg_cert"
        cur.execute(query)
        result =cur.fetchall()
        print(result)
        return render_template("certification.html", certifications=result)


@app.route("/people", methods=["POST", "GET"])
def browse_add_people():
    if request.method == "GET":
        #This contains the list of scripts we want to show on the page. This is shown in the layout.html page
        scripts = ["people.js"]
        cur = mysql.connection.cursor()
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        query = "SELECT id, fname, lname, homeworld, age FROM bsg_people"
        cur.execute(query)
        people_results = cur.fetchall()
        print(people_results)
        #Render the template with the people and certificate results we generated
        return render_template('people.html', people=people_results, certs = certs_results, jsscripts = scripts)
    elif request.method == "POST":
        scripts = ["people.js"]
        cur = mysql.connection.cursor()
        #Grab form data & insert into database
        fname_input = request.form['fname']
        lname_input = request.form['lname']
        hworld_input = request.form['hworld']
        age_input = request.form['age']
        insert_query = query = 'INSERT INTO bsg_people (fname, lname, homeworld, age) VALUES (%s,%s,%s,%s)'
        data = (fname_input, lname_input, hworld_input, age_input)
        cur.execute(insert_query, data)

        #For every selected certification, we add a new row into the intersection table
        #We can get the previously inserted people_id using LAST_INSERT_ID()
        selected_certs_input = request.form.getlist("cert")
        for selected_cert in selected_certs_input:
            insert_query = "INSERT into bsg_cert_people (cid, pid) VALUES (%s, LAST_INSERT_ID())" % (selected_cert)
            cur.execute(insert_query)

        #Now we render the people.html page again
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        query = "SELECT id, fname, lname, homeworld, age FROM bsg_people"
        cur.execute(query)
        people_results = cur.fetchall()
        print(people_results)
        return render_template('people.html', people=people_results, certs = certs_results, jsscripts = scripts)


@app.route("/people/<int:people_id>", methods=["GET", "POST", "DELETE"])
def delete_update_people(people_id):
    if request.method == "DELETE":
        cur = mysql.connection.cursor()
        #Because of our fk constraints, we first delete the rows in the intersection table that belong to the person we are deleting
        query = "DELETE FROM bsg_cert_people WHERE pid = %s"
        data = (people_id,)
        cur.execute(query, data)

        #Then delete the person from bsg_people
        delete_query = "DELETE FROM bsg_people WHERE id = %s"
        data = (people_id,)
        cur.execute(delete_query, data)

        #display all people
        scripts = ["people.js"]
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        query = "SELECT id, fname, lname, homeworld, age FROM bsg_people"
        cur.execute(query)
        people_results = cur.fetchall()
        print(people_results)
        #Render the template with the people and certificate results we generated
        return render_template('people.html', people=people_results, certs = certs_results, jsscripts = scripts)

    #This is used to generate the prefilled update form
    elif request.method == "GET":
        cert_list = []
        cur = mysql.connection.cursor()
        #get certificates so that we can dynamically show them on the form
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        #get person's results associated with the people_id
        query = "SELECT id, fname, lname, homeworld, age FROM bsg_people WHERE id = %s" % (people_id)
        cur.execute(query)
        person_results = cur.fetchone()
        print(person_results)
        query = "SELECT cid FROM bsg_cert_people WHERE pid = %s" % (people_id)
        cur.execute(query)
        persons_certs = cur.fetchall()
        print(persons_certs)
        for cert in persons_certs:
            cert_list.append(cert[0])
        return render_template('update_people.html', person=person_results, certs = certs_results, person_certs_list = cert_list)
    elif request.method == "POST":
        cur = mysql.connection.cursor()
        #Grab form data & update the people_id in the database
        fname_input = request.form['fname']
        lname_input = request.form['lname']
        hworld_input = request.form['hworld']
        age_input = request.form['age']
        update_query = "UPDATE bsg_people SET fname = %s, lname = %s, homeworld = %s, age = %s WHERE id = %s"
        data = (fname_input, lname_input, hworld_input, age_input, people_id)
        cur.execute(insert_query, data)

        #Now we will delete all the rows in the intersection table the person_id we are updating
        query = "DELETE FROM bsg_cert_people WHERE pid = %s"
        data = (people_id)
        cur.execute(query, data)

        #Now, for every selected certification in the updated form, we add a new row into the intersection table
        #Even the rows that existed before the update
        selected_certs_input = request.form.getlist("cert")
        for selected_cert in selected_certs_input:
            insert_query = "INSERT into bsg_cert_people (cid, pid) VALUES (%s, %s)" % (selected_cert, people_id)
            cur.execute(insert_query)

        #display all people
        scripts = ["people.js"]
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        query = "SELECT id, fname, lname, homeworld, age FROM bsg_people"
        cur.execute(query)
        people_results = cur.fetchall()
        print(people_results)
        #Render the template with the people and certificate results we generated
        return render_template('people.html', people=people_results, certs = certs_results, jsscripts = scripts)


@app.route("/filter_people/<int:cert_id>", methods=["GET"])
def filter_people(cert_id):
    if request.method == "GET":
        scripts = ["people.js"]
        cur = mysql.connection.cursor()
        query = "SELECT id, title FROM bsg_cert"
        cur.execute(query)
        certs_results = cur.fetchall()
        print(certs_results)
        query = "SELECT p.id, fname, lname, homeworld, age FROM bsg_people p INNER JOIN bsg_cert_people cp ON cp.pid = p.id INNER JOIN bsg_cert c ON c.id = cp.cid WHERE c.id = %s" % (cert_id)
        cur.execute(query)
        people_filtered = cur.fetchall()
        print(people_filtered)
        return render_template('people.html', people = people_filtered, certs = certs_results, jsscripts = scripts)


@app.route('/db-test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from bsg_people;"
    result = execute_query(db_connection, query);
    return result

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html')
