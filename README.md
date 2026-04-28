# VAMPIRE — API REST pour manager des VMs

***

## Prérequis

- Python 3.8+
- pip

***

## Structure du projet

```
vampire/
├── app.py           # Point d'entrée, configuration Flask
├── models.py        # Modèles SQLAlchemy (User, VM, Disk, NIC)
├── auth.py          # Routes d'authentification (register, login)
├── routes_vm.py     # Routes de gestion des VMs
├── test_api.sh      # Script de validation
├── requirements.txt # Dépendances Python
└── README.md        # Documentation
```

***

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/vampire.git
cd vampire

# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

***

## Lancement

```bash
python app.py
```

L'API démarre sur `http://localhost:5000`. une base SQLite est créée automatiquement dans le dossier `instance/` au premer lancement.

***

## Authentification

Toutes les routes (sauf `/api/register` et `/api/login`) nécessitent un token JWT passé dans le header :

```
Authorization: Bearer <token>
```

### Créer un compte

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Se connecter et récupérer le token

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

> Chaque utilisateur ne voit et ne gère que ses propres VMs.

***

## Attributs d'une VM

| Attribut | Description | Exemple |
|---|---|---|
| `id` | Identifiant interne API (auto) | `1` |
| `uuid` | Identifiant unique hyperviseur (auto) | `41adb2b6-78f9-...` |
| `name` | Nom technique de la VM | `Linux Server Test` |
| `title` | Titre lisible | `RockyLinux 9.5 serveur Web` |
| `description` | Description libre | `Serveur web Nginx` |
| `cpu` | Nombre de vCPU | `2` |
| `ram_gb` | RAM en Go | `4` |
| `hypervisor` | URI de l'hyperviseur | `VMWare Workstation://172.17.3.2` |
| `status` | État courant | `stopped`, `running`, `suspended` |
| `disks` | Liste de disques avec capacité | `[{"name":"disk_1","size_gb":10}]` |
| `nics` | Liste d'interfaces réseau | `["NIC_1","NIC_2"]` |

***

## Endpoints

### Gestion des VMs

| Méthode | URL | Descripion |
|---|---|---|
| `POST` | `/api/vms` | Créer une VM |
| `GET` | `/api/vms` | Lister ses VMs |
| `GET` | `/api/vms/<id>` | Détail d'une VM |
| `PUT` | `/api/vms/<id>` | Mettre à jour une VM |
| `DELETE` | `/api/vms/<id>` | Supprimer une VM |
| `GET` | `/api/vms/<id>/status` | Interroger l'état d'une VM |
| `POST` | `/api/vms/<id>/action` | Exécuter une action sur une VM |
| `POST` | `/api/vms/<id>/migrate` | Migrer une VM vers un autre hyperviseur |
| `GET` | `/api/vms/search` | Rechercher des VMs par critères |

### Authentification

| Méthode | URL | Description |
|---|---|---|
| `POST` | `/api/register` | Créer un compte utilisateur |
| `POST` | `/api/login` | Se connecter et obtenir un token JWT |

***

## Exemples d'utilisation

### Crér une VM

```bash
curl -X POST http://localhost:5000/api/vms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "P41_LINUX_RL_003",
    "title": "RockyLinux 9.5 serveur Web projet 41",
    "description": "Serveur web Nginx",
    "cpu": 2,
    "ram_gb": 4,
    "hypervisor": "qemu+kvm://172.17.3.2",
    "disks": [
      {"name": "disk_1", "size_gb": 10},
      {"name": "disk_2", "size_gb": 100}
    ],
    "nics": ["NIC_1", "NIC_2"]
  }'
```

### Lister ses VMs

```bash
curl http://localhost:5000/api/vms \
  -H "Authorization: Bearer $TOKEN"
```

### Démarrer une VM

```bash
curl -X POST http://localhost:5000/api/vms/1/action \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"action": "power_on"}'
```

### Actions disponibles

| Action | Effet |
|---|---|
| `power_on` | `running` |
| `power_off` | `stopped` |
| `suspend` | `suspended` |
| `snapshot` | inchangé |
| `sauvegarde` | inchangé |

***

## Validation

Un script de validation enchaîne automatiquement tous les appels API pour vérifier le bon fonctionnement :

```bash
chmod +x test_api.sh
./test_api.sh
```


## Stack technique

- **Flask**
- **Flask-JWT-Extended**
- **Flask-SQLAlchemy**
- **SQLite** (fichier `instance/vampire.db`)
