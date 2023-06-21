from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, UniqueConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import datetime

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Customer:
    __tablename__ = "customers"
    
    #attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    
    #relationships
    locations = db.association_proxy('reservations', 'location')
    reservations = db.relationship('Reservation', back_populates='customer')
    serialize_rules = ('-reservations.customer')
    
    #validation
    @validates('customer')
    def validate_customer(self, key, name):
        if not name or len(name) < 1:
            raise ValueError('rekt')
        return name
    
    @validates('customer')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('rekt')
        return email
    
    def __repr__(self):
        return f'<Customer name={self.name}, email={self.email}>'
    
class Location:
    __tablename__ = "locations"
    
    #attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    max_party_size = db.Column(db.Integer)
    
    #relationships
    customers = db.association_proxy('reservations', 'customer')
    reservations = db.relationship('Reservation', back_populates='location') 
    serialize_rules = ('-reservations.location')
    
    @validates("name")
    def validate_name(self, key, name):
        if not name or len(name) < 1:
            raise ValueError("Location must have a name")
        return name

    @validates("max_party_size")
    def validate_max_party_size(self, key, max_party_size):
        if not isinstance(max_party_size, int):
            raise TypeError("Max party size must be an integer")
        return max_party_size

class Reservation:
    __tablename__ = "reservations"

    #attributes
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.date)
    party_name = db.Column(db.String)
    
    #relationships
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'))
    location_id = db.Column(db.Integer, ForeignKey('location.id'))
    serialize_rules = ('-customers.reservation', '-locations.reservation')

    #validation
    @validates('reservation')
    def validate_date(self, key, date):
        if not isinstance(date, datetime.date):
            raise ValueError('rekt')
        return date
    
    @validates('reservation')
    def validate_party_name(self, key, party_name):
        if not party_name or len(party_name) < 1:
            raise ValueError('rekt')
        return party_name
    
    @validates('reservation')
    def validate_customer_id(self, key, customer_id):
        if not customer_id or not isinstance(customer_id, int):
            raise ValueError('rekt')
        return customer_id
    
    @validates('reservation')
    def validate_location_id(self, key, location_id):
        if not location_id or not isinstance(location_id, int):
            raise ValueError('rekt')
        return location_id