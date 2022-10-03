from configparser import ConfigParser
import os
from flask import Flask

from app.app_connector import create_app 

app = Flask(__name__)

config = ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    app.run()

# if __name__ == "__main__":
#     app.run(port=5000, debug = True)
    