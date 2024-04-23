from transformers import pipeline
from sqlalchemy.orm import Session
import models

async def classify_text(articles):
    pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    results = []
    for article in articles:
        print("article", article['title'])
        if article['title'] != '[Removed]':
            results.append({"article_sentiment_analysis": pipe(article['title']), "article_name": article['title'], "article_description": article['description'], "article_url": article['url']})
    return results;

def create_mutiple_company_from_schema(row, db: Session):
    try:
        company_data = {
            'name': str(row['name']),
            'ticker': str(row['ticker']),
            'cik': str(row['cik']),
            'cusip': str(row['cusip']),
            'exchange': str(row['exchange']),
            'is_delisted': False,
            'category': str(row['category']),
            'sector': str(row['sector']),
            'industry': str(row['industry']),
            'sic': str(row['sic']),
            'sic_sector': str(row['sicSector']),
            'sic_industry': str(row['sicIndustry']),
            'fama_sector': str(row['famaSector']),
            'fama_industry': str(row['famaIndustry']),
            'currency': str(row['currency']),
            'location': str(row['location']),
            'id': str(row['id'])
        }

        # Create a new instance of the Company model
        db_company = models.Company(**company_data)

        # Add the new company instance to the session
        db.add(db_company)

        # Commit the transaction to persist all the changes made
        db.commit()
        db.refresh(db_company)
        return "Data successfully added to the database."

    except Exception as e:
        # If an error occurs, rollback the transaction
        db.rollback()
        return f"Error occurred: {str(e)}"

def get_companies(db: Session, exchange: str, page: int = 1, limit: int = 10):
    query = db.query(models.Company).filter(models.Company.exchange == exchange)
    total_count = query.count()
    companies = query.offset((page - 1) * limit).limit(limit).all()
    return {"total_count": total_count, "companies": companies}