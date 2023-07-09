FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt openpyxl
RUN pip3 install --no-cache-dir -r requirements.txt openpyxl
RUN pip install flask_sqlalchemy
RUN pip install pandas
RUN pip install matplotlib
COPY assets/css /assets/css
COPY . .


CMD ["python3", "app.py"]
