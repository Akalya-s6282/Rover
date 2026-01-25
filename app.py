from dotenv import load_dotenv
import os

from Crds import create_app
load_dotenv()  
app = create_app()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
