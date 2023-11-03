FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY buyerApplication.py ./buyerApplication.py
COPY orders.py ./orders.py
COPY products.py ./products.py
COPY configuration.py ./configuration.py
COPY models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

ENTRYPOINT ["python","./buyerApplication.py"]
