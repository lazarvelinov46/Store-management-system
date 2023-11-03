from flask import Blueprint, request, Response, jsonify;
from shop.models import database, Product, Category,ProductCategory;
from sqlalchemy import and_;
import io;
import csv;

productBlueprint = Blueprint ( "products", __name__ );


@productBlueprint.route ( "/update", methods = ["POST"] )
def updateProduct ():

    content = request.files["file"].stream.read ( ).decode ( "utf-8" );
    stream = io.StringIO ( content );
    reader = csv.reader ( stream );

    products = [ ];
    for row in reader:
        categories=row[0];
        categoryList=categories.split("|");
        catIds=[];
        for cat in categoryList:
            check=Category.query.filter(Category.categoryName==cat).first();
            if(not(check)):
                addCat=Category(categoryName=cat);
                database.session.add(addCat);
                database.session.commit();
                id=Category.query.filter(Category.categoryName==cat).first();
                catIds.append(id);
        product=Product(name=row[1],price=float(row[2]));
        database.session.add(product);
        database.session.commit();
        for catid in catIds:
            pc=ProductCategory(productId=product.id,categoryId=catid.id);
            database.session.add(pc);
            database.session.commit();


@productBlueprint.route ( "/search?name=<PRODUCT_NAME>&category=<CATEGORY_NAME>", methods = ["GET"] )
def getProduct (PRODUCT_NAME,CATEGORY_NAME):
    #asdf
    cats=[];
    prods=[];
    cats = database.session.query(Category.categoryName).join(ProductCategory).join(Product).filter \
        (and_(Category.categoryName.like(f"%{CATEGORY_NAME}%"),Product.name.like(f"%{PRODUCT_NAME}%")));
    prods=Product.query.join(ProductCategory).join(Category).filter \
        (and_(Category.categoryName.like(f"%{CATEGORY_NAME}%"),Product.name.like(f"%{PRODUCT_NAME}%")));
    return Response(jsonify(categories=cats,products=prods),status=200);
