from flask import Flask,Blueprint, request, Response, jsonify;
from datetime import datetime;
from sqlalchemy import and_;
from orders import orderBlueprint;
from configuration import Configuration;
from models import database, Product, Category,ProductCategory,Order,ProductOrder;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;

application = Flask ( __name__ );
application.config.from_object ( Configuration )
jwt=JWTManager(application)


#application.register_blueprint(orderBlueprint,url_prefix='/orders');

def roleCheck ( role ):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments ):
            verify_jwt_in_request ( );
            claims = get_jwt ( );
            if ( ( "roles" in claims ) and ( role in claims["roles"] ) ):
                return function ( *arguments, **keywordArguments );
            else:
                return jsonify({'msg':"Missing Authorization Header"}),401;

        return decorator;

    return innerRole;

@application.route("/orders_to_deliver",methods=["GET"])
@roleCheck(role='courier')
def getUndelivered():
    ordersInfo=database.session.query(Order.id,Order.email).filter(Order.status=="CREATED").all();
    ordersjson=[];
    for o in ordersInfo:
        jtemp={
            "id":o[0],
            "email":o[1]
        }
        ordersjson.append(jtemp);
    return jsonify(orders=ordersjson),200;

@application.route("/pick_up_order",methods=["POST"])
@roleCheck(role='courier')
def setPending():
    id = request.json.get("id", "");
    if (id == ""):
        return jsonify(message="Missing order id."), 400;
    try:
        id = int(id);
    except ValueError:
        return jsonify(message="Invalid order id."), 400;
    if (not id or id < 0):
        return jsonify(message="Invalid order id."), 400;
    order = Order.query.filter(Order.id == id).first();
    if (not order or order.status != "CREATED"):
        return jsonify(message="Invalid order id."), 400;
    order.status="PENDING";
    database.session.commit();
    return Response("",status=200);

if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True ,host = "0.0.0.0",port=5004);
