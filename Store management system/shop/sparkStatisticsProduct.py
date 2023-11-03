from pyspark.sql import SparkSession
from pyspark.sql.functions import sum
from flask import jsonify
import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_URL = os.environ["DATABASE_URL"] if ("DATABASE_URL" in os.environ) else "localhost"

builder = SparkSession.builder.appName("PySpark productStatistics")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

products_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shopDatabase") \
    .option("dbtable", "shopDatabase.products") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

product_order_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shopDatabase") \
    .option("dbtable", "shopDatabase.product_order") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

orders_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shopDatabase") \
    .option("dbtable", "shopDatabase.orders") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

result1=products_data_frame.join(
    product_order_data_frame,
    products_data_frame['id']==product_order_data_frame['productId']
).join(
    orders_data_frame,
    product_order_data_frame['orderId']==orders_data_frame['id']
).groupBy(products_data_frame['name'])\
    .agg(sum(product_order_data_frame['quantity']+0).alias('sold')).filter(orders_data_frame['status']=="COMPLETE")

result2=products_data_frame.join(
    product_order_data_frame,
    products_data_frame['id']==product_order_data_frame['productId']
).join(
    orders_data_frame,
    product_order_data_frame['orderId']==orders_data_frame['id']
).groupBy(products_data_frame['name'])\
    .agg(sum(product_order_data_frame['quantity']+0).alias('waiting')).filter(orders_data_frame['status']!="COMPLETE");


names=result1.select('name').collect()
sold=result1.select('sold').collect()
waiting=result2.select('waiting').collect()

print('podaci');
for n in names:
    print(n);
    print('|');
print('split');
for s in sold:
    print(s);
    print('|');
print('split');
for w in waiting:
    print(w);
    print('|');
print('podaci');
spark.stop();

# people_data_frame.show ( )
# result = people_data_frame.filter ( people_data_frame["gender"] == "Male" ).collect ( )
# print ( result )
