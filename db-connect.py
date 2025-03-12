import mysql.connector
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Verbindung zur MySQL-Datenbank herstellen
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(buffered=True)