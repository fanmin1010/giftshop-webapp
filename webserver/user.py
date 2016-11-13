from flask import Flask, request, render_template, g, redirect, Response, session, jsonify
from flask_login import (LoginManager, login_required, login_user, current_user, logout_user, UserMixin)

class User(UserMixin):
    def __init__(self, uid, password):
        self.uid = uid
        self.password = password

        self.shopping_cart = []

        cursor = g.conn.execute("SELECT name, email, dob FROM users WHERE uid=%s;", (uid,))
        details = list(cursor)[0]

        self.name = details[0]
        self.email = details[1]
        self.dob = details[2]

    def get_auth_token(self):
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    def add_to_cart(self, pid):
        self.shopping_cart.append(pid)

    def clear_shopping_cart(self):
        self.shopping_cart = []

    @staticmethod
    def get(email, password):
        cursor = g.conn.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=%s and password=%s);", (email, password))
        is_exists = list(cursor)[0][0]

        if is_exists:
            cursor = g.conn.execute("SELECT uid, password FROM users WHERE email=%s;", email)
            result = list(cursor)[0]
            uid = result[0]
            password = result[1]
            return User(uid, password)

        return None


