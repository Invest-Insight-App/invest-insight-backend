from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
PASSWORD=os.environ.get("DATABASE_PASSWORD")

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://root:{PASSWORD}@localhost:3306/InvestmentInsightApplication'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()