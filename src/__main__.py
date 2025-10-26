from app import app
from flask import send_from_directory
from dotenv import load_dotenv

load_dotenv()


app.run(host="0.0.0.0", port=5001, debug=True)
