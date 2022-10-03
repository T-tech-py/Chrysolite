from flask import Flask, jsonify


class User:

    def signup(self):
        user = {
            "_id":'',
            "firstname":'',
            "lastname":'',
            "email":'',
            "d.o.b": '',
            "password":'',
        }
        return jsonify(user),200

    def otp(self):
        otp = {
            'email':'',
            'otp':''
        }
        return jsonify(otp),200
    
    def login(self):
        login = {
            'email':'',
            'password':'',
        }
        return login 
    
    