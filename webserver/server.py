#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, jsonify
import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://mc4235:ku6z3@104.196.175.120/postgres"

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database\n\n\n\n\n\n"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

def redirect_url():
    return request.referrer or '/'

@app.route('/')
def index():
  login_name = None
  name = None
  if 'uid' in session:
      cursor = g.conn.execute('select name from users where uid=%s', (session['uid'],))
      name = list(cursor)[0][0]
      print('logged in as {} {}'.format(session['uid'], name))
      login_name = name

  # DEBUG: this is debugging code to see what request looks like
  # print request.args
  # print name
  context = dict(data = name, login_name = login_name)
  return render_template("index.html", **context)

@app.route('/registration', methods=['GET'])
def register():
    if 'uid' in session:
        return redirect_url()
    else:
        return render_template("register.html")

@app.route('/registered', methods=['POST'])
def registered():
    email = request.form['email']
    password = request.form['pass']
    username = request.form['username']
    dob = request.form['dob']
    cursor = g.conn.execute("SELECT 1 FROM users WHERE email = %s", (email));
    row = cursor.fetchone()
    msg = "User with email {} has already existed. Please login instead.".format(email)
    err = False
    if not row:
        msg = ""
    if password == "":
        msg = msg + "\n Empty password."
        err = True
    if email == "":
        msg = msg + "\n Empty email."
        err = True
    if username == "":
        msg = msg + "\n Empty user name."
        err = True
    if len(dob) > 10:
        msg = msg +"\n invalid birth date."
        err =True
    content = dict(error_msg = msg)

    if row or err:
        return render_template("register.html", **content)
    cursor = g.conn.execute("INSERT INTO users(email, name, dob, password) VALUES (%s, %s, %s, %s)", (email, username, dob, password))
    if cursor:
        cursor = g.conn.execute("SELECT uid FROM users WHERE email=%s;", email)
        session['uid'] = list(cursor)[0][0]
        return redirect('/')
    else:
        msg = "something is wrong with db"
        content["error_msg"] =  msg
        return render_template("register.html", **content)

@app.route('/users')
def show_users():
    cursor = g.conn.execute("SELECT uid, name, email FROM users")
    users = []
    for result in cursor:
        dict_user = {'uid': result['uid'], 'name': result['name'], 'email': result['email']}
        users.append(dict_user)
    cursor.close()
    print(users)

    context = dict(data = users)

    return render_template("user_list.html", **context)

@app.route('/login_page')
def show_login_page():
    if 'uid' in session:
        print('Already logged in as {}'.format(session['uid']))
        context = dict(error_msg = 'Already logged in!')
        return redirect(redirect_url())

    return render_template('login_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'uid' in session:
        print('Already logged in as {}'.format(session['uid']))
        context = dict(error_msg = 'Already logged in!')
        return render_template('index.html', **context)
        # return jsonify(error_message = "Already logged in"), 403

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = g.conn.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=%s and password=%s);", (email, password))

        is_exists = list(cursor)[0][0]
        if is_exists:
            cursor = g.conn.execute("SELECT uid FROM users WHERE email=%s;", email)
            session['uid'] = list(cursor)[0][0]
        else:
            context = dict(error_msg = 'Login credentials do not exist. Please try again.')
            return render_template("login_page.html", **context)
    else:
        pass
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect('/')

@app.route('/product')
def product():
    cursor = g.conn.execute('SELECT * FROM product;')
    result = cursor.fetchall()

    num_prod = len(result)

    context = dict(product_list = result, num_products = num_prod)
    return render_template('product.html', **context)

@app.route('/product/<pid>')
def product_page(pid):
    cursor = g.conn.execute('SELECT * FROM product WHERE pid=%s;', (pid,))
    result = cursor.fetchone()
    if result is None:
        print('Product for pid {} does not exist'.format(pid))
        return redirect('/')

    context = dict(product_name = result['name'], product_price = result['price'], product_description = result['description'],
                    product_rating = result['rating'], product_quantity = result['quantity'])
    return render_template('single_product.html', **context)

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    run()
