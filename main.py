import datetime
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline , AutoTokenizer, AutoModelForSeq2SeqLM, BartForConditionalGeneration #- Added in TB
import requests
import os
from dotenv import load_dotenv
from data import DUMMY_DATA  # data taken from stockdata API
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

class TextSummary(BaseModel):
    #article_name: str
    article_summary: str 
    combined_text: str
    #article_url: str

class ArticleResponses(BaseModel):
    article_sentiment_analysis: List[SentimentAnalysisScores]
    article_name: str
    article_description: str
    article_url: str
    article_snippet: str 

class SentimentAnalysisResponses(BaseModel):
    responses: List[ArticleResponses]
    summary: List[TextSummary]

class Tags(Enum):
    investmentInsight = "Investment Analysis"



# text classification function
async def classify_text(data):
    pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    results = []
    for d in data[:2]:
        print("article", d['title'])
        if d['title'] != 'null':
            results.append({"article_sentiment_analysis": pipe(d['title']), 
                            "article_name": d['title'],
                            "article_description": d['description'], 
                            "article_url": d['url'],
                            "article_snippet": d['snippet'] 
                            })
    return results;

# summarization function

async def summarize_text(data):
    """ Summarizes the news article 'highlight' within the data < entity list from the api"""
    sum_pipe = pipeline("summarization", model="facebook/bart-large-cnn")
    results = []
    for d in data:
             # Check if the item contains entities
        if "entities" in d:
            entities = d["entities"]
            
            # Iterate over each entity
        for entity in entities:
            # Check if the entity contains highlights
            if "highlights" in entity:
                highlights = entity["highlights"]
                    
             # Iterate over each article highlight
            for highlight in highlights:
                # Check if the highlight contains text
                if "highlight" in highlight:
                    # text = highlight["highlight"] - if not using combined text
                    # Combine snippet and highlight
                    text = d.get("snippet", "") + " " + highlight["highlight"]
                            
                    # Summarize the highlight using BART
                    summary = sum_pipe(text, max_length=80, min_length=30, do_sample=False, num_beams=2)[0]["summary_text"]
                                
                    # Append the summary to the list
                    results.append({"combined_text": text, "article_summary": summary })
    return results;

# API endpoint for sentiment analysis and text summarization
@app.get("/investmentAnalysis/v1/sentimentAnalysis", response_model=SentimentAnalysisResponses, status_code=status.HTTP_200_OK, tags=[Tags.investmentInsight], summary="sentiment analysis on news articles")
async def classify(symbol: str, start_date: datetime.date):
    api_key = API_KEY
    print("api_key", api_key)

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
    results = await classify_text(responses)
    summary = await summarize_text(responses)
    return {"responses": results, "totalResults": len(results), "status": "ok", "summary": summary}