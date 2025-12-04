import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL", "")
JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
INFERENCE_API_KEY = os.getenv("API_KEY", "")
COLAB_URL = os.getenv("COLAB_URL", "")