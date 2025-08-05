Starting the virtual environment:  source ./.venv/bin/activate
Installing all requirements: pip install -r requirements.txt
Start the backend server: python manage.py runserver
Start the frontend: from the frontend directory, run `npm start`



Remember to check for conflicting running processes on port 8000:
python manage.py runserver 0.0.0.0:8000
If: Error: That port is already in use.
kill unwanted_pid_id
python manage.py runserver 0.0.0.0:8000
