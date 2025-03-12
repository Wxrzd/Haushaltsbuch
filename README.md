# Haushaltsbuch
Repository für das Modul "Programmierung von Webanwendungen"
Projekt: Entwicklung eines digitalen Haushaltsbuches zur Überwachung seiner Einnahmen/Ausgaben

## Setup Instructions

1. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory with the following content:
   ```env
   DB_USER=<your-database-username>
   DB_PASSWORD=<your-database-password>
   DB_PORT=<your-database-port>
   DB_NAME=<your-database-name>
   ```
3. **Run the applicatioin**
 ```sh
   python manage.py runserver
```