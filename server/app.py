#!/usr/bin/env python3

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get(
#     "DB_URI", f"sqlite://{os.path.join(BASE_DIR, 'instance/app.db')}"
# )

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models import db, Customer, Location, Reservation
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    BASE_DIR, "instance/app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def home():
    return ""

class Customers(Resource):
    def get(self):
        try:
            customers = [customer.to_dict(only=('id','name','email')) 
                         for customer in Customer.query.all()]
            return customers, 200
        except:
            return {'error': 'rekt'}, 400
        
    def post(self):
        data = request.get_json()
        try:
            customer = Customer(
                id = data('id'),
                name = data('name'), 
                email = data('email')
            )
            db.session.add(customer)
            db.session.commit()    
            return customer, 201
        except:
            return {'error': 'rekt'}, 400
        
api.add_resources(Customer, '/customers')

class CustomerById(Resource):
    def get(self, id):
        data = request.get_json()
        try:
            customer = Customer.query.filter(Customer.id == id).first().to_dict(
                rules=('id','name','email', 'reservations'))
            return customer, 200
        except:
            return {'error': 'rekt'}, 404
        
api.add_resources(Customer, '/customers/<int:id>')

class LocationsById(Resource):
    def get(self, id):
        try:
            location = Location.query.filter_by(id=id).first()
            return location.to_dict(), 200
        except:
            raise Exception({"error": "404 NOT FOUND"}, 404)
        
    def delete(self, id):
        try:
            location = Location.query.filter_by(id=id).first()
            db.session.delete(location)
            db.session.commit()
            
            return {}, 204
        except:
            raise Exception({'error': '404 NOT FOUND'}, 404)

api.add_resources(Location, '/locations/<int:id>')

#Mike: if you're reading this, you got me good here lol I had to look at the solution! 
#Learned some new things, thank you, sir!
class Reservations(Resource):
    def get(self):
        try:
            reservations = [
                reservation.to_dict()
                for reservation in Reservation.query.all()
            ]
            return reservations, 200
        except:
            return ({"error": "400 bad request"}, 400)

    def post(self):
        data = request.get_json()
        # print(
        #     datetime.date(
        #         datetime.datetime.strptime(
        #             data.get("reservation_date"), "%Y-%m-%d"
        #         )
        #     )
        # )
        try:
            reservation = Reservation(
                reservation_date=datetime.datetime.strptime(
                    data.get("reservation_date"), "%Y-%m-%d"
                ).date(),
                customer_id=data.get("customer_id"),
                location_id=data.get("location_id"),
                party_size=data.get("party_size"),
                party_name=data.get("party_name"),
            )

            db.session.add(reservation)
            db.session.commit()

            return reservation.to_dict(), 201

        except IntegrityError:
            return ({"error": "500 server went boom"}, 400)
        except AttributeError:
            return ({"error": "incorrect"}, 400)
        except ValueError:
            return ({"error": "incorrect"}, 400)
        except Exception:
            return ({"error": "incorrect"}, 400)


api.add_resource(Reservations, "/reservations")

class ReservationsByID(Resource):
    def get(self, id):
        try:
            reservation = (
                Reservation.query.filter(Reservation.id == id)
                .first()
                .to_dict()
            )
            return reservation, 200
        except:
            return ({"error": "404 not found"}, 404)

    def patch(self, id):
        print("in the patch route")
        data = request.get_json()
        reservation = Reservation.query.filter(Reservation.id == id).first()
        if not reservation:
            return ({"error": "404 not found"}, 404)
        for attr in data:
            print(attr, data)
            if attr == "reservation_date":
                setattr(
                    reservation,
                    attr,
                    datetime.datetime.strptime(
                        data.get("reservation_date"), "%Y-%m-%d"
                    ).date(),
                )
            else:
                setattr(reservation, attr, data.get(attr))
        try:
            db.session.add(reservation)
            db.session.commit()
            return reservation.to_dict(), 200
        except Exception:
            return ({"error": "error"}, 400)

    def delete(self, id):
        reservation = Reservation.query.filter(Reservation.id == id).first()
        if not reservation:
            return ({"error": "404 not found"}, 404)
        db.session.delete(reservation)
        db.session.commit()
        return ({}, 204)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
