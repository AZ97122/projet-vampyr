# Les utilisateurs ne pourront voir que leurs propres vms, les routes nécessitent un token JWT valide

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, VM, Disk, NIC

vm_bp = Blueprint('vm', __name__)

def vm_to_dict(vm):
    return {
        'id': vm.id, 'uuid': vm.uuid, 'name': vm.name,
        'title': vm.title, 'description': vm.description,
        'cpu': vm.cpu, 'ram_gb': vm.ram_gb,
        'hypervisor': vm.hypervisor, 'status': vm.status,
        'disks': [{'name': d.name, 'size_gb': d.size_gb} for d in vm.disks],
        'nics': [n.name for n in vm.nics]
    }

# Création
@vm_bp.route('/vms', methods=['POST'])
@jwt_required()
def create_vm():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    vm = VM(name=data['name'], title=data.get('title'), description=data.get('description'),
            cpu=data.get('cpu', 1), ram_gb=data.get('ram_gb', 1),
            hypervisor=data.get('hypervisor'), user_id=user_id)
    db.session.add(vm)
    db.session.flush()
    for disk in data.get('disks', []):
        db.session.add(Disk(name=disk['name'], size_gb=disk['size_gb'], vm_id=vm.id))
    for nic in data.get('nics', []):
        db.session.add(NIC(name=nic, vm_id=vm.id))
    db.session.commit()
    return jsonify(vm_to_dict(vm)), 201

# Liste
@vm_bp.route('/vms', methods=['GET'])
@jwt_required()
def list_vms():
    user_id = int(get_jwt_identity())
    vms = VM.query.filter_by(user_id=user_id).all()
    return jsonify([vm_to_dict(v) for v in vms]), 200

# Détail
@vm_bp.route('/vms/<int:vm_id>', methods=['GET'])
@jwt_required()
def get_vm(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    return jsonify(vm_to_dict(vm)), 200

# Mise à jour
@vm_bp.route('/vms/<int:vm_id>', methods=['PUT'])
@jwt_required()
def update_vm(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    data = request.get_json()
    for field in ['name', 'title', 'description', 'cpu', 'ram_gb', 'hypervisor']:
        if field in data:
            setattr(vm, field, data[field])
    if 'disks' in data:
        Disk.query.filter_by(vm_id=vm.id).delete()
        for disk in data['disks']:
            db.session.add(Disk(name=disk['name'], size_gb=disk['size_gb'], vm_id=vm.id))
    if 'nics' in data:
        NIC.query.filter_by(vm_id=vm.id).delete()
        for nic in data['nics']:
            db.session.add(NIC(name=nic, vm_id=vm.id))
    db.session.commit()
    return jsonify(vm_to_dict(vm)), 200

# Suppression
@vm_bp.route('/vms/<int:vm_id>', methods=['DELETE'])
@jwt_required()
def delete_vm(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    db.session.delete(vm)
    db.session.commit()
    return jsonify({'message': 'VM deleted'}), 200

# Actions : power_on, power_off, suspend, snapshot, sauvegarde, migration, état
VALID_ACTIONS = ['power_on', 'power_off', 'suspend', 'snapshot', 'sauvegarde']

@vm_bp.route('/vms/<int:vm_id>/action', methods=['POST'])
@jwt_required()
def vm_action(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    data = request.get_json()
    action = data.get('action')
    if action not in VALID_ACTIONS:
        return jsonify({'error': 'Invalid action'}), 400
    status_map = {'power_on': 'running', 'power_off': 'stopped', 'suspend': 'suspended'}
    if action in status_map:
        vm.status = status_map[action]
        db.session.commit()
    return jsonify({'message': f'Action {action} executed', 'status': vm.status}), 200

# Migration
@vm_bp.route('/vms/<int:vm_id>/migrate', methods=['POST'])
@jwt_required()
def migrate_vm(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    data = request.get_json()
    target = data.get('target_hypervisor')
    if not target:
        return jsonify({'error': 'target_hypervisor required'}), 400
    vm.hypervisor = target
    db.session.commit()
    return jsonify({'message': f'VM migrated to {target}', 'vm': vm_to_dict(vm)}), 200

# État
@vm_bp.route('/vms/<int:vm_id>/status', methods=['GET'])
@jwt_required()
def vm_status(vm_id):
    user_id = int(get_jwt_identity())
    vm = VM.query.filter_by(id=vm_id, user_id=user_id).first_or_404()
    return jsonify({'id': vm.id, 'name': vm.name, 'status': vm.status}), 200

# Recherche (marhce par hyperviseur, statut, CPU min, RAM min)
@vm_bp.route('/vms/search', methods=['GET'])
@jwt_required()
def search_vms():
    user_id = int(get_jwt_identity())
    query = VM.query.filter_by(user_id=user_id)
    if hypervisor := request.args.get('hypervisor'):
        query = query.filter(VM.hypervisor.like(f'%{hypervisor}%'))
    if status := request.args.get('status'):
        query = query.filter_by(status=status)
    if min_cpu := request.args.get('min_cpu'):
        query = query.filter(VM.cpu >= int(min_cpu))
    if min_ram := request.args.get('min_ram'):
        query = query.filter(VM.ram_gb >= int(min_ram))
    return jsonify([vm_to_dict(v) for v in query.all()]), 200
