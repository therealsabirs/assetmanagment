from flask import Flask, render_template, request, redirect, session, flash, url_for
from config import Config
from db import db
from io import BytesIO
from models import Users, Employee, Hardware
from datetime import datetime
import base64
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import send_file
import io
import psycopg2

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Users.query.filter_by(email_id=email, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    
    return render_template("dashboard.html")

#-------------Employee Management--------------------------------------

@app.route("/employee", methods=["GET", "POST"])
def employee():
    if "user_id" not in session:
        return redirect("/")
    
    location_filter = request.args.get("location")
    
    if location_filter:
        employees = Employee.query.filter_by(location=location_filter).all()
    else:
        employees = Employee.query.all()
    
    return render_template("employee.html", employees=employees)

@app.route("/employee/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        new_employee = Employee(
            employee_id=request.form["employee_id"],
            employee_name=request.form["employee_name"],
            address=request.form["address"],
            phone_number=request.form["phone_number"],
            email_id=request.form["email_id"],
            gender=request.form["gender"],
            date_of_joining=datetime.strptime(request.form["date_of_joining"], "%Y-%m-%d"),
            date_of_exit=datetime.strptime(request.form["date_of_exit"], "%Y-%m-%d") if request.form["date_of_exit"] else None,
            status=request.form["status"],
            location=request.form["location"]
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("employee"))

    return render_template("add_employee.html")

@app.route("/employee/edit/<string:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == "POST":
        employee.employee_name = request.form["employee_name"]
        employee.address = request.form["address"]
        employee.phone_number = request.form["phone_number"]
        employee.email_id = request.form["email_id"]
        employee.gender = request.form["gender"]
        employee.date_of_joining = datetime.strptime(request.form["date_of_joining"], "%Y-%m-%d")
        employee.date_of_exit = datetime.strptime(request.form["date_of_exit"], "%Y-%m-%d") if request.form["date_of_exit"] else None
        employee.status = request.form["status"]
        employee.location = request.form["location"]

        db.session.commit()
        return redirect(url_for("employee"))

    return render_template("edit_employee.html", employee=employee)

@app.route("/employee/delete/<string:employee_id>")
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for("employee"))

#-----------------Hardware Management (UPDATED)-----------------------------------------

@app.route("/hardware", methods=["GET"])
def hardware():
    if "user_id" not in session:
        return redirect("/")
    
    location_filter = request.args.get("location")
    
    if location_filter:
        hardware_list = Hardware.query.filter_by(location=location_filter).all()
    else:
        hardware_list = Hardware.query.all()

    return render_template("hardware.html", hardware_list=hardware_list)

@app.route('/hardware/add', methods=['GET', 'POST'])
def add_hardware():
    if request.method == 'POST':
        file = request.files.get('attachment')  # Get the uploaded file

        file_data = None
        if file and file.filename:
            file_data = file.read()  # Read the file as binary

        new_hardware = Hardware(
            id=request.form['id'],
            type=request.form['type'],
            make=request.form['make'],
            model=request.form['model'],
            serial_number=request.form['serial_number'],
            date_of_purchase=datetime.strptime(request.form['date_of_purchase'], "%Y-%m-%d"),
            warranty_expire_on=datetime.strptime(request.form['warranty_expire_on'], "%Y-%m-%d"),
            warranty_days_left=int(request.form['warranty_days_left']),
            status=request.form['status'],
            vendor=request.form['vendor'],
            adp_status=request.form['adp_status'],
            attachment=file_data,  # Save actual file in DB
            location=request.form['location']
        )

        db.session.add(new_hardware)
        db.session.commit()
        return redirect(url_for('hardware'))

    return render_template('add_hardware.html')


@app.route('/hardware/edit/<string:id>', methods=['GET', 'POST'])
def edit_hardware(id):
    hardware = Hardware.query.filter_by(id=str(id)).first_or_404() 

    if request.method == 'POST':
        
        hardware.type = request.form['type']
        hardware.make = request.form['make']
        hardware.model = request.form['model']
        hardware.serial_number = request.form['serial_number']
        hardware.date_of_purchase = datetime.strptime(request.form['date_of_purchase'], "%Y-%m-%d")
        hardware.warranty_expire_on = datetime.strptime(request.form['warranty_expire_on'], "%Y-%m-%d")
        hardware.warranty_days_left = request.form['warranty_days_left']
        hardware.status = request.form['status']
        hardware.vendor = request.form['vendor']
        hardware.adp_status = request.form['adp_status']
        hardware.location = request.form['location']

        # **Check if file is uploaded**
        if 'attachment' in request.files and request.files['attachment'].filename != '':
            file = request.files['attachment']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            hardware.attachment = filename  # Store filename in DB

        db.session.commit()
        return redirect(url_for('hardware'))

    return render_template('edit_hardware.html', hardware=hardware)


@app.route("/hardware/delete/<string:id>")
def delete_hardware(id):
    hardware = Hardware.query.get_or_404(id)
    db.session.delete(hardware)
    db.session.commit()
    return redirect(url_for("hardware"))


@app.route('/hardware/download/<string:id>')
def download_hardware_file(id):
    hardware = Hardware.query.filter_by(id=str(id)).first_or_404()  # Convert ID to string

    if not hardware.attachment:
        return "No attachment found!", 404

    return send_file(
        io.BytesIO(hardware.attachment),
        as_attachment=True,
        download_name=f"hardware_{id}.pdf",  # Change extension as needed
        mimetype="application/octet-stream"
    )





#------------------Assing Hardware------------------------------------------


@app.route('/assign_hardware', methods=['GET', 'POST'])
def assign_hardware():
    employees = Employee.query.all()  # Fetch all employees

    # Fetch only unassigned hardware (assigned_to is NULL or empty)
    available_hardware = Hardware.query.filter((Hardware.assigned_to == None) | (Hardware.assigned_to == '')).all()

    if request.method == 'POST':
        employee_id = request.form['employee_id']
        hardware_id = request.form['hardware_id']

        hardware = Hardware.query.get(hardware_id)
        if hardware and not hardware.assigned_to:  # Ensure hardware is not already assigned
            hardware.assigned_to = employee_id  # Assign hardware
            db.session.commit()
            flash("Hardware assigned successfully!", "success")
            return redirect(url_for('assign_hardware'))

    return render_template("assign_hardware.html", employees=employees, available_hardware=available_hardware)







from flask import jsonify

@app.route('/get_assigned_hardware/<string:employee_id>')
def get_assigned_hardware(employee_id):
    try:
        assigned_hardware = Hardware.query.filter_by(assigned_to=employee_id).all()

        # If no hardware found, return empty list
        if not assigned_hardware:
            return jsonify([])

        hardware_list = [
            {"id": hw.id, "type": hw.type, "serial_number": hw.serial_number}
            for hw in assigned_hardware
        ]
        
        return jsonify(hardware_list)
    except Exception as e:
        return jsonify({"error": str(e)})




#----------------------------unassigned-----------------------------------



@app.route('/unassign_hardware', methods=['GET', 'POST'])
def unassign_hardware():
    employees = Employee.query.all()  # Fetch all employees

    if request.method == 'POST':
        hardware_id = request.form['hardware_id']
        hardware = Hardware.query.get(hardware_id)

        if hardware:
            hardware.assigned_to = None  # Unassign hardware
            db.session.commit()
            flash("Hardware unassigned successfully!", "success")
            return redirect(url_for('unassign_hardware'))

    return render_template("unassign_hardware.html", employees=employees)






from flask import jsonify, request

@app.route('/search_employee')
def search_employee():
    query = request.args.get('query', '')

    if query:
        employees = Employee.query.filter(
            (Employee.employee_id.ilike(f"%{query}%")) | 
            (Employee.employee_name.ilike(f"%{query}%"))
        ).all()
    else:
        employees = Employee.query.all()

    employee_data = [
        {
            "employee_id": emp.employee_id,
            "employee_name": emp.employee_name,
            "address": emp.address,
            "phone_number": emp.phone_number,
            "email_id": emp.email_id,
            "gender": emp.gender,
            "date_of_joining": emp.date_of_joining,
            "date_of_exit": emp.date_of_exit if emp.date_of_exit else "N/A",
            "status": emp.status,
            "location": emp.location,
        }
        for emp in employees
    ]

    return jsonify(employee_data)



from flask import jsonify, request

@app.route('/search_hardware')
def search_hardware():
    serial_number = request.args.get('serial_number', '')

    if serial_number:
        hardware_list = Hardware.query.filter(Hardware.serial_number.ilike(f"%{serial_number}%")).all()
    else:
        hardware_list = Hardware.query.all()

    hardware_data = [
        {
            "id": hw.id,
            "type": hw.type,
            "make": hw.make,
            "model": hw.model,
            "serial_number": hw.serial_number,
            "date_of_purchase": hw.date_of_purchase.strftime("%Y-%m-%d") if hw.date_of_purchase else "",
            "warranty_expire_on": hw.warranty_expire_on.strftime("%Y-%m-%d") if hw.warranty_expire_on else "",
            "warranty_days_left": hw.warranty_days_left(),
            "status": hw.status,
            "vendor": hw.vendor,
            "adp_status": hw.adp_status,
            "attachment": bool(hw.attachment),
            "location": hw.location,
            "assign_to": hw.assigned_to,
        }
        for hw in hardware_list
    ]

    return jsonify(hardware_data)







#--------------Dashboard-------------------------------------------------------------
from flask import jsonify
from sqlalchemy import text

from sqlalchemy import text

# Define the Dashboard Stats API
from sqlalchemy.sql import text

@app.route('/dashboard_stats', methods=['GET'])
def dashboard_stats():
    # Total hardware count
    total_hardware = db.session.execute(text("SELECT COUNT(*) FROM hardware")).scalar()
    
    # Total employees count
    total_employees = db.session.execute(text("SELECT COUNT(*) FROM employee")).scalar()
    
    # Total available hardware (not assigned)
    available_hardware = db.session.execute(text("SELECT COUNT(*) FROM hardware WHERE assigned_to IS NULL OR assigned_to = ''")).scalar()

    # Fetch hardware type breakdown (total count per type)
    hardware_types = db.session.execute(text("SELECT type, COUNT(*) FROM hardware GROUP BY type")).fetchall()
    hardware_types_dict = {row[0]: row[1] for row in hardware_types}

    # Fetch available hardware per type
    available_by_type = db.session.execute(text("SELECT type, COUNT(*) FROM hardware WHERE assigned_to IS NULL OR assigned_to = '' GROUP BY type")).fetchall()
    available_by_type_dict = {row[0]: row[1] for row in available_by_type}

    # Fetch assigned hardware per type
    assigned_by_type = db.session.execute(text("SELECT type, COUNT(*) FROM hardware WHERE assigned_to IS NOT NULL AND assigned_to <> '' GROUP BY type")).fetchall()
    assigned_by_type_dict = {row[0]: row[1] for row in assigned_by_type}

    stats = {
        "total_hardware": total_hardware,
        "total_employees": total_employees,
        "available_hardware": available_hardware,
        "hardware_types": hardware_types_dict,
        "available_by_type": available_by_type_dict,
        "assigned_by_type": assigned_by_type_dict,
    }

    return jsonify(stats)




















if __name__ == "__main__":
    app.run(debug=True)
