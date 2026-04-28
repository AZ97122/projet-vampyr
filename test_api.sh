#!/bin/bash
BASE="http://localhost:5000/api"

echo "--- Enregistrement ---"
curl -s -X POST $BASE/register -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -m json.tool

echo "--- Connexion ---"
TOKEN=$(curl -s -X POST $BASE/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
AUTH="Authorization: Bearer $TOKEN"

echo "--- Création de VMs ---"
VM_ID=$(curl -s -X POST $BASE/vms -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"Linux test","title":"RockyLinux 9.5 serveur test","description":"Serveur test","cpu":2,"ram_gb":4,"hypervisor":"VMWare Workstation://172.17.3.2","disks":[{"name":"disk_1","size_gb":10},{"name":"disk_2","size_gb":100}],"nics":["NIC_1","NIC_2"]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "VM ID: $VM_ID"

echo "--- Liste des VMs ---"
curl -s $BASE/vms -H "$AUTH" | python3 -m json.tool

echo "--- Récupération de VM ---"
curl -s $BASE/vms/$VM_ID -H "$AUTH" | python3 -m json.tool

echo "--- Power On ---"
curl -s -X POST $BASE/vms/$VM_ID/action -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"action":"power_on"}' | python3 -m json.tool

echo "--- Statut ---"
curl -s $BASE/vms/$VM_ID/status -H "$AUTH" | python3 -m json.tool

echo "--- Migration ---"
curl -s -X POST $BASE/vms/$VM_ID/migrate -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"target_hypervisor":"qemu+kvm://172.17.3.5"}' | python3 -m json.tool

echo "--- Rechercher (status=running) ---"
curl -s "$BASE/vms/search?status=running" -H "$AUTH" | python3 -m json.tool

echo "--- Mise à jour VMs ---"
curl -s -X PUT $BASE/vms/$VM_ID -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"cpu":4,"ram_gb":8}' | python3 -m json.tool

echo "--- Snapshot ---"
curl -s -X POST $BASE/vms/$VM_ID/action -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"action":"snapshot"}' | python3 -m json.tool

echo "--- Suspendre ---"
curl -s -X POST $BASE/vms/$VM_ID/action -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"action":"suspend"}' | python3 -m json.tool

echo "--- Sauvegarde ---"
curl -s -X POST $BASE/vms/$VM_ID/action -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"action":"sauvegarde"}' | python3 -m json.tool

echo "--- Supprimer VMs ---"
curl -s -X DELETE $BASE/vms/$VM_ID -H "$AUTH" | python3 -m json.tool

echo "--- Liste des VMs (Doit être vide) ---"
curl -s $BASE/vms -H "$AUTH" | python3 -m json.tool
