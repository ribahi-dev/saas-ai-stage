"""
setup_db.py -- Script de configuration de la base de donnees PostgreSQL
Cree la base plateforme_stages_db si elle n existe pas, puis applique les migrations.

Usage :
  .\venv\Scripts\python setup_db.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Charger les variables .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env', encoding='utf-8-sig')
except ImportError:
    print("[ERREUR] python-dotenv n est pas installe.")
    sys.exit(1)

DB_NAME = os.getenv('DB_NAME', 'plateforme_stages_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

print("=" * 60)
print("  SETUP -- Plateforme de Recommandation de Stages")
print("=" * 60)
print(f"  Base de donnees : {DB_NAME}")
print(f"  Utilisateur     : {DB_USER}")
print(f"  Hote            : {DB_HOST}:{DB_PORT}")
print("=" * 60)

# Etape 1 : Creer la base de donnees si elle n existe pas
print("\n[1/3] Creation de la base de donnees...")
try:
    import psycopg

    # Connexion a la base 'postgres' (toujours disponible)
    conn = psycopg.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        dbname='postgres',
        user=DB_USER,
        password=DB_PASS,
        autocommit=True
    )
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cur.fetchone():
            print(f"  [OK] La base '{DB_NAME}' existe deja.")
        else:
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"  [OK] Base '{DB_NAME}' creee avec succes !")
    conn.close()

except psycopg.OperationalError as e:
    print(f"\n  [ERREUR] Connexion a PostgreSQL impossible :")
    print(f"  {e}")
    print("\n  Verifiez que :")
    print("  1. PostgreSQL est installe et en cours d'execution")
    print("  2. Le mot de passe DB_PASSWORD dans .env est correct")
    print("  3. La base 'postgres' (par defaut) est accessible")
    sys.exit(1)

# Etape 2 : Appliquer les migrations
print("\n[2/3] Application des migrations Django...")
manage_py = Path(__file__).parent / 'backend' / 'manage.py'
result = subprocess.run(
    [sys.executable, str(manage_py), 'migrate', '--verbosity=1'],
    cwd=str(Path(__file__).parent)
)
if result.returncode != 0:
    print("  [ERREUR] Les migrations ont echoue.")
    sys.exit(1)
print("  [OK] Migrations appliquees avec succes !")

# Etape 3 : Creer le superutilisateur
print("\n[3/3] Creation du compte administrateur...")
print("  (Appuyez sur Entree pour utiliser les valeurs par defaut)")
result = subprocess.run(
    [sys.executable, str(manage_py), 'createsuperuser'],
    cwd=str(Path(__file__).parent)
)

print("\n" + "=" * 60)
print("  SETUP COMPLET !")
print("=" * 60)
print("\n  Lancez le serveur avec :")
print("  .\\venv\\Scripts\\python backend\\manage.py runserver")
print("\n  API disponible sur : http://localhost:8000/api/")
print("  Admin Django      : http://localhost:8000/admin/")
print("=" * 60)
