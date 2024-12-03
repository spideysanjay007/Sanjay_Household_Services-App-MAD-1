from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Users Table: For Professionals and Customers
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    role = db.Column(db.String(15), nullable=False)  # professional or customer
    active = db.Column(db.Boolean, default=False, nullable=False)
    # Relationships
    professionals = db.relationship('Professional', backref='user', uselist=False, lazy=True, cascade="all, delete-orphan")
    customers = db.relationship('Customer', backref='user', uselist=False, lazy=True, cascade="all, delete-orphan")

# Services Table
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Relationships
    professionals = db.relationship('Professional', backref='service', lazy=True, cascade="all, delete-orphan")
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True, cascade="all, delete-orphan")

# Professionals Table
class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete="CASCADE"), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True, cascade="all, delete-orphan")

# Customers Table
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(15), nullable=False)

    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True, cascade="all, delete-orphan")

# Service Requests Table
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete="CASCADE"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete="SET NULL"), nullable=True)
    status = db.Column(db.String, nullable=False, default='Pending')
