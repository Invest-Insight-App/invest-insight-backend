import datetime
from typing import List
import pandas as pd
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status, Request, Depends
from data import DUMMY_DATA  # data taken from stockdata API

import time
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from sec_api import MappingApi

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import utils
import schemas

load_dotenv()
API_KEY=os.environ.get("API_KEY")
SEC_API_KEY=os.environ.get("SEC_API_KEY")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(debug=True, title="Investment Insight API")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

class Tags(Enum):
    investmentInsight = "Investment Analysis"
    exchange = "Exchange Market"

# API endpoint for sentiment analysis and text summarization
@app.get("/investmentAnalysis/v1/sentimentAnalysis", response_model=schemas.SentimentAnalysisResponses, status_code=status.HTTP_200_OK, tags=[Tags.investmentInsight], summary="Sentiment Analysis On News Articles")
async def classify(symbol: str, start_date: datetime.date):
    """
    Fetches AI sentiment analysis and summaries of news articles.

    Args:

    symbol (str): The symbol representing the ticker.

    start_date (str): The start date in the format YYYY-MM-DD.
    """
    api_key = API_KEY

    if api_key:
        api_key = api_key.strip("()").strip("' ")
    else:
        raise HTTPException(status_code=404, detail="Internal server error")

    try:
        data = requests.get(f' https://api.stockdata.org/v1/news/all?symbols={symbol}&filter_entities=true&published_before={start_date}&language=en&api_token={api_key}')
    except Exception as e:
        raise HTTPException(status_code=data.status_code) from e

    if data.status_code != 200:
        raise HTTPException(status_code=data.status_code, detail="Failed to fetch news articles")

    responses = data.json()[ 'data']
    results = await utils.classify_text(responses)
    summary = await utils.summarize_text(responses)
    return {"responses": results, "totalResults": len(results), "status": "ok", "summary": summary}

# @app.post("/ExchangeMarket/v1/CompaniesCsv", response_model=[], status_code=status.HTTP_200_OK, tags=[Tags.exchange])
# async def create_csv_files_for_listed_companies(exchange: str):
#     """
#     Create CSV files for listed companies.

#     Args:
#         exchange (str): The exchange for which the companies are listed.
#             Must be one of: NYSE, NASDAQ, NYSEMKT, NYSEARCA, OTC, BATS, INDEX

#     Returns:
#         dict: A message indicating the operation is done.
#     """
#     try:
#         mappingApi = MappingApi(api_key=SEC_API_KEY)
#         by_exchange = mappingApi.resolve('exchange', exchange)
#         all_listings = pd.DataFrame(by_exchange)
#         all_listings.to_csv("f{exchange}.csv", index=False)
#         return {"message": "done"}
#     except Exception as e:
#         return {"error": str(e)}

@app.post("/ExchangeMarket/v1/Companies", status_code=status.HTTP_200_OK, tags=[Tags.exchange])
def create_companies(db: Session = Depends(get_db)):
    """
    Updates the database with exchange data from CSV files.

    Returns:
        dict: A dictionary containing a message indicating that the operation has been completed.
    """

    exchanges = [
        "bats",
        "index",
        "nasdaq",
        "nyse",
        "nysearca",
        "nysemkt",
        "otc"
    ]

    for exchange in exchanges:
        df_bats = pd.read_csv(f"./exchange_data/{exchange}.csv")
        for _, row in df_bats.iterrows():
            row = row.fillna('')
            try:
                utils.create_mutiple_company_from_schema(row, db=db)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process data") from e

    return {"message": "done"}

@app.get("/ExchangeMarket/v1/Companies/{exchange}", tags=[Tags.exchange])
def read_companies(exchange: str, page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetches companies listed on a specified exchange market.

    Args:

    exchange (str): The exchange for which the companies are listed.
            Must be one of: NYSE, NASDAQ, NYSEMKT, NYSEARCA, OTC, BATS, INDEX.

    page (int): The page number of results to retrieve. Default is 1.

    Returns:
        dict: A dictionary containing information about 100 companies from the selected exchange market.
    """

    db_companies = utils.get_companies(db, exchange=exchange, page=page, limit=limit)
    if not db_companies:
        raise HTTPException(status_code=404, detail="No companies found for the specified exchange.")
    return db_companies

