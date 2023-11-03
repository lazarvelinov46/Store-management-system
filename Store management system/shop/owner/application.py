from shop.configuration import Configuration;
from flask import Flask;
from shop.products import productBlueprint;
from shop.categories import categoryBlueprint;
from shop.models import database;
from flask_jwt_extended import JWTManager

application = Flask ( __name__ );
application.config.from_object (Configuration )
jwt=JWTManager(application)

application.register_blueprint ( productBlueprint, url_prefix = "/products" );
application.register_blueprint(categoryBlueprint,url_prefix='/categories');

if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True );
