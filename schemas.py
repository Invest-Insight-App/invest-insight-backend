from typing import List
from pydantic import BaseModel

class Company(BaseModel):
    name: str
    ticker: str
    cik: str
    cusip: str
    exchange: str
    isDelisted: bool
    category: str
    sector: str
    industry: str
    sic: str
    sicSector: str
    sicIndustry: str
    famaSector: str
    famaIndustry: str
    currency: str
    location: str
    id: str

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