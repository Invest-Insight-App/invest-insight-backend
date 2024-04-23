from transformers import pipeline
from sqlalchemy.orm import Session
import models

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