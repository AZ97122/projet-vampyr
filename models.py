# Classes nécéssaires pour le projet. Une classe User, VM, Disk et NIC

from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    secret_key = db.Column(db.String(256), default=lambda: str(uuid.uuid4()))
    vms = db.relationship('VM', backref='owner', lazy=True)

class VM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    cpu = db.Column(db.Integer, default=1)
    ram_gb = db.Column(db.Integer, default=1)
    hypervisor = db.Column(db.String(200))
    status = db.Column(db.String(50), default='stopped')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disks = db.relationship('Disk', backref='vm', cascade='all, delete-orphan')
    nics = db.relationship('NIC', backref='vm', cascade='all, delete-orphan')

class Disk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    size_gb = db.Column(db.Integer)
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))

class NIC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
