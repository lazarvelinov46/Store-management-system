import os

from configuration import Configuration;
from flask import Flask, Response,jsonify;
from products import productBlueprint;
from categories import categoryBlueprint;
from functools import wraps;
from models import database;
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, jwt_required
import subprocess;

application = Flask ( __name__ );
application.config.from_object (Configuration )
jwt=JWTManager(application)

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

@application.route ( "/product_statistics", methods = ["GET"] )
def getProductStatistics ():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/sparkStatisticsProduct.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(['/template.sh'])
    products=result.decode();
    bulk=products.split('podaci');

    podaci=bulk[1]
    redovi=podaci.split('split');

    i=0;
    names=[]
    sold=[];
    waiting=[];

    for r in redovi:
        jedan = r.split('|');
        for j in jedan:
            if i==0:
                names.append(j);
            if i==1:
                sold.append(j);
            if i==2:
                waiting.append(j);
        i=i+1;
    i=0;
    stats=[];
    for n in names:
        jobj={
            'name':n,
            'sold':int(sold[i]),
            'waiting':int(waiting[i])
        };
        stats.append(jobj);

    return jsonify(statistics=stats),200;



@application.route ( "/category_statistics", methods = ["GET"] )
def getCategoryStatistics ():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/sparkStatisticsCategories.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
    result = subprocess.check_output(['/template.sh'])
    res = result.decode()
    bulk = res.split("podaci")

    wholeData = bulk[1]
    categories = wholeData.split("|")
    retdata=[]
    j=0;
    for c in categories:
        if(c=="\n" or c=="" or j==len(categories)-1):
            continue;
        retdata.append(c[19:-3]);
        j=j+1;

    return jsonify(statistics=retdata), 200
if (__name__ == "__main__"):
    database.init_app ( application );
    application.run ( debug = True,host = "0.0.0.0",port=5005 );
