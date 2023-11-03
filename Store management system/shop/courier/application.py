from flask import Flask;

from shop.courier.orders import orderBlueprint;
from shop.configuration import Configuration;
from shop.models import database;
from flask_jwt_extended import JWTManager;

application = Flask ( __name__ );
application.config.from_object ( Configuration )
jwt=JWTManager(application)


application.register_blueprint(orderBlueprint,url_prefix='/orders');

if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True ,port=5004);
