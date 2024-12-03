from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Professional, Service, Customer, ServiceRequest
from functools import wraps
from datetime import datetime

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash('You are not authorized to access this page.', 'error')
                return redirect(url_for('home'))
            return func(*args, **kwargs)
        return decorated_view
    return decorator


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register-professional', methods=['GET', 'POST'])
def register_professional():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile_no = request.form.get('mobile_no')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        description = request.form.get('description')
        service_id = request.form.get('service_id')

        if not all([username, email, password, description, service_id]):
            flash('All fields are required', 'error')
            return redirect(url_for('register_professional'))

        if User.query.filter_by(email=email).first():
            flash('User email already exists', 'error')
            return redirect(url_for('register_professional'))

        new_user = User(username=username, email=email, password=password, mobile_no=mobile_no, address=address, pincode=pincode, role='professional')
        db.session.add(new_user)
        db.session.commit()

        new_professional = Professional(user_id=new_user.id, service_id=service_id, description=description)
        db.session.add(new_professional)
        db.session.commit()

        flash('Professional registration successful')
        return redirect(url_for('login_professional'))
    services = Service.query.all()
    return render_template('register_professional.html', services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile_no = request.form.get('mobile_no')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        if not all([username, email, password, mobile_no, address, pincode]):
            flash('All fields are required', 'error')
            return redirect(url_for('register'))


        if User.query.filter_by(email=email).first():
            flash('User email already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password, mobile_no=mobile_no, address=address, pincode=pincode, role='customer')
        db.session.add(new_user)
        db.session.commit()

        new_customer = Customer(user_id=new_user.id, address=address, phone=mobile_no)
        db.session.add(new_customer)
        db.session.commit()

        flash('Customer registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'admin@gmail.com' and password == '2323':
            session['role'] = 'admin'
            session['user_id'] = 0
            flash('Admin login successful')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'error')
        return redirect(url_for('adminlogin'))
    return render_template('adminlogin.html')

@app.route('/login-professional', methods=['GET', 'POST'])
def login_professional():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password, role='professional').first()
        if user and password:
            session['user_id'] = user.id
            session['role'] = 'professional'
            flash('Professional login successful')
            return redirect(url_for('professional_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login_professional.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password, role='customer').first()
        if user and password:
            session['user_id'] = user.id
            session['role'] = 'customer'
            flash('Customer login successful')
            return redirect(url_for('customer_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/admin-dashboard')
@role_required('admin')
def admin_dashboard():
    # Admin-specific logic
    services = Service.query.all()
    return render_template('admin_dashboard.html', services=services)

@app.route('/professional-dashboard')
@role_required('professional')
def professional_dashboard():
    # Professional-specific logic
    user_id = session['user_id']
    professional = Professional.query.filter_by(user_id=user_id).first()
    pending_requests = ServiceRequest.query.filter_by(service_id=professional.service_id, status='Pending').all()
    service_requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
    return render_template('professional_dashboard.html', requests=service_requests, pending_requests=pending_requests)

@app.route('/customer-dashboard')
@role_required('customer')
def customer_dashboard():
    # Customer-specific logic
    user_id = session['user_id']
    customer = Customer.query.filter_by(user_id=user_id).first()
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    return render_template('customer_dashboard.html', requests=service_requests, services=services)

@app.route('/services/new', methods=['GET', 'POST'])
@role_required('admin')
def create_service():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        time_required = request.form.get('time_required')
        new_service = Service(name=name, description=description, time_required=time_required, price=price)
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_service.html')

@app.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        service.name = request.form.get('name')
        service.description = request.form.get('description')
        service.price = request.form.get('price')
        service.time_required = request.form.get('time_required')
        db.session.commit()
        flash('Service updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_service.html', service=service)

@app.route('/services/delete/<int:service_id>', methods=['POST'])
@role_required('admin')
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/service-requests/new', methods=['GET', 'POST'])
@role_required('customer')
def create_service_request():
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        new_request = ServiceRequest(
            customer_id=Customer.query.filter_by(user_id=session['user_id']).first().id,
            service_id=service_id,
            status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Service request created successfully', 'success')
        return redirect(url_for('customer_dashboard'))
    services = Service.query.all()
    return render_template('new_service_request.html', services=services)

@app.route('/service-requests/delete/<int:request_id>', methods=['POST'])
@role_required('customer')
def delete_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.status != 'Pending':
        flash('You can only delete pending requests.', 'error')
        return redirect(url_for('customer_dashboard'))
    db.session.delete(service_request)
    db.session.commit()
    flash('Service request deleted successfully', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/service-requests/accept/<int:request_id>', methods=['POST'])
@role_required('professional')
def accept_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    professional = Professional.query.filter_by(user_id=session['user_id']).first()
    if service_request.status != 'Pending':
        flash('Request already handled.', 'error')
        return redirect(url_for('professional_dashboard'))
    service_request.professional_id = professional.id
    service_request.status = 'Accepted'
    db.session.commit()
    flash('Service request accepted.', 'success')
    return redirect(url_for('professional_dashboard'))

@app.route('/service-requests/complete/<int:request_id>', methods=['POST'])
@role_required('customer')
def complete_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.status != 'Accepted':
        flash('Only accepted requests can be completed.', 'error')
        return redirect(url_for('customer_dashboard'))
    service_request.status = 'Completed'
    db.session.commit()
    flash('Service request marked as completed.', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
