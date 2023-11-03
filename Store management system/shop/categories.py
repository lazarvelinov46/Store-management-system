from flask import Blueprint, request, Response, jsonify;
from models import database, Product, Category,ProductCategory,ProductOrder,Order;
from configuration import Configuration
from sqlalchemy import and_,or_,func,desc;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;
import io;
import csv;

categoryBlueprint = Blueprint ( "categories", __name__ );

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



@categoryBlueprint.route ( "/category_statistics", methods = ["GET"] )
@roleCheck(role='owner')
def getProductStatistics ():
    categoriesDelivered=database.session.query(Category.categoryName).order_by(
        desc(Category.delivered),Category.categoryName
    ).all();
    catret=[]
    for c in categoriesDelivered:
        catret.append(c[0]);
    return jsonify(categories=catret),200;