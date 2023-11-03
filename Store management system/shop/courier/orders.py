from flask import Blueprint, request, Response, jsonify;
from shop.models import database, Product, Category,ProductCategory,Order,ProductOrder;
from datetime import datetime;
from sqlalchemy import and_;
import io;
import csv;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;

orderBlueprint = Blueprint ( "orders", __name__ );

def roleCheck ( role ):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments ):
            verify_jwt_in_request ( );
            claims = get_jwt ( );
            if ( ( "roles" in claims ) and ( role in claims["roles"] ) ):
                return function ( *arguments, **keywordArguments );
            else:
                return Response ( "Access denied, wrong role!!!", status = 403 );

        return decorator;

    return innerRole;



@orderBlueprint.route("/orders_to_deliver",methods=["GET"])
@roleCheck(role='Kurir')
@jwt_required()
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

@orderBlueprint.route("/pick_up_order",methods=["POST"])
@roleCheck(role='Kurir')
@jwt_required()
def setPending():
    id = request.json.get("id", "");
    if (id == ""):
        return jsonify(message="Missing order id"), 400;
    id = int(id);
    if (not id or id < 0):
        return jsonify(message="Invalid order id"), 400;
    order = Order.query.filter(Order.id == id).first();
    if (not order or order.status != "CREATED"):
        return jsonify(message="Invalid order id"), 400;
    order.status="PENDING";
    database.session.commit();
    return Response("",status=200);