# from flask import Flask, request, jsonify
# from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
# from langchain_core.prompts import ChatPromptTemplate 
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain_openai import OpenAI, ChatOpenAI
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from shared.models import Base, Stock, StockPrice, StockRecommendation, StockEarnings
from resources.db_connection import generate_engine, generate_session
from resources.functions import is_market_open
from routines import get_stock_data
import time
import os

# if os.getenv("INIT", None) == 1:
from db_init import init_db

TEN_MINUTES_IN_SEC = 600

engine = generate_engine()
init_db(engine)

# MYSQL_USER = os.environ.get("MYSQL_USER")
# MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
# MYSQL_HOST = os.environ.get("MYSQL_HOST")
# MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

# connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
# engine = create_engine(connection_string, echo=True)

# Base.metadata.create_all(bind=engine)

session = generate_session(engine)
while True:
    if not is_market_open():
        time.sleep(TEN_MINUTES_IN_SEC)
        continue

    for stock in session.query(Stock).all():
        print(f"Collect data for {stock.symbol}")
        data = get_stock_data(stock.symbol)
        if data.get("price", None) is None:
            continue
        session.add(StockPrice(stock.symbol, data["price"]))
        session.commit()
        
    time.sleep(TEN_MINUTES_IN_SEC)

# Create list of all stocks
# from resources.stocks_list import get_stock_symbol_name_pairs

# Session = sessionmaker(bind=engine)
# session = Session()

# stocks_list = get_stock_symbol_name_pairs()
# import numpy as np
# for symbol, name in stocks_list:
#     if symbol is np.nan or name is np.nan or symbol is None or name is None or symbol == "" or name == "" or symbol == "None" or name == "None" or symbol == "nan" or name == "nan":
#         continue
#     print(symbol)
#     stock = Stock(symbol, name)
#     session.add(stock) 
# session.commit()

# stock_meta = Stock("META", "Meta")
# session.add(stock_meta)
# session.commit()

# stock_meta_price = StockPrice("META", 101)
# session.add(stock_meta_price)
# session.commit()





# Database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# Define the QueryLog model
# class QueryLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     query = db.Column(db.String(500))
#     ip = db.Column(db.String(100))
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     result = db.Column(db.Text)