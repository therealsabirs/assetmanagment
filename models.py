from db import db
from datetime import date 
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.Text, nullable=False)
    email_id = db.Column(db.String(255), unique=True, nullable=False)
class Employee(db.Model):
    employee_id = db.Column(db.String(255), primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    email_id = db.Column(db.String(255), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    date_of_joining = db.Column(db.Date, nullable=False)
    date_of_exit = db.Column(db.Date)
    status = db.Column(db.String(50))
    location = db.Column(db.String(255))
class Hardware(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    date_of_purchase = db.Column(db.Date, nullable=False)
    warranty_expire_on = db.Column(db.Date, nullable=False)
    warranty_days_left = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    adp_status = db.Column(db.String(50), nullable=False)
    attachment = db.Column(db.LargeBinary)  # Store file data as bytes
    location = db.Column(db.String(100), nullable=False)
    assigned_to = db.Column(db.String(100), nullable=False)

    # ✅ Fixed function to calculate warranty days left
    def warranty_days_left(self):
        if self.warranty_expire_on:
            return max((self.warranty_expire_on - date.today()).days, 0)
        return "No Warranty"