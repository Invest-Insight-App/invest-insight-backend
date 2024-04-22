import datetime
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import requests
import os
from dotenv import load_dotenv
from data import DUMMY_DATA
from fastapi import FastAPI, HTTPException, status, Request
import time
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

load_dotenv()
API_KEY=os.environ.get("NEWS_API_KEY")

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

class Payload(BaseModel):
    text: str

# Define the Pydantic model for sentiment analysis response
class SentimentAnalysisScores(BaseModel):
    label: str
    score: float

class ArticleResponses(BaseModel):
    article_sentiment_analysis: List[SentimentAnalysisScores]
    article_name: str
    article_description: str
    article_url: str

class SentimentAnalysisResponses(BaseModel):
    responses: List[ArticleResponses]

class Tags(Enum):
    investmentInsight = "Investment Analysis"

async def classify_text(articles):
    pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    results = []
    for article in articles:
        print("article", article['title'])
        if article['title'] != '[Removed]':
            results.append({"article_sentiment_analysis": pipe(article['title']), "article_name": article['title'], "article_description": article['description'], "article_url": article['url']})
    return results;

@app.get("/investmentAnalysis/v1/sentimentAnalysis", response_model=SentimentAnalysisResponses, status_code=status.HTTP_200_OK, tags=[Tags.investmentInsight], summary="sentiment analysis on news articles")
async def classify(company_name: str, start_date: datetime.date):
    api_key = API_KEY
    print("api_key", api_key)

    if api_key:
        api_key = api_key.strip("()").strip("' ")
    else:
        raise HTTPException(status_code=404, detail="Internal server error")

    try:
        # articles = DUMMY_DATA["data"]["articles"]
        articles = requests.get(f'https://newsapi.org/v2/everything?q={company_name}&from={start_date}&sortBy=popularity&apiKey={api_key}')
    except Exception as e:
        raise HTTPException(status_code=articles.status_code) from e

    if articles.status_code != 200:
        raise HTTPException(status_code=articles.status_code, detail="Failed to fetch news articles")

    responses = articles.json()[ 'articles']
    results = await classify_text(responses)
    return {"responses": results, "totalResults": len(results), "status": "ok"}


