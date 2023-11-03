from flask import Blueprint, request, Response, jsonify;
from shop.models import database, Product, Category,ProductCategory;
from sqlalchemy import and_;
import io;
import csv;
from functools import wraps;
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request;

productBlueprint = Blueprint ( "products", __name__ );

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


@productBlueprint.route ( "/search", methods = ["GET"] )
@roleCheck(role='Kupac')
@jwt_required()
def getProduct ():
    name=request.args.get('name');
    categ=request.args.get('category')
    #asdf
    cats=[];
    prods=[];
    cats = Category.query.join(ProductCategory).join(Product).filter \
        (and_(Category.categoryName.like(f"%{categ}%"),Product.name.like(f"%{name}%"))).all();
    categoriesRet=[];
    for c in cats:
        categoriesRet.append(c.categoryName);
    print(categoriesRet);
    prods=Product.query.join(ProductCategory).join(Category).filter \
        (and_(Category.categoryName.like(f"%{categ}%"),Product.name.like(f"%{name}%"))).all();
    productsRet=[];
    for p in prods:
        prodcats=[]
        for cat in p.categories:
            prodcats.append(cat.categoryName);
        print(prodcats)
        productsRet.append({
            'categories':prodcats,
            'id':p.id,
            'name':p.name,
            'price':p.price
        })
    retval={
        'categories':categoriesRet,
        'products':productsRet
    }
    return jsonify(retval),200;


