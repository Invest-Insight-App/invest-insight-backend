from sqlalchemy import Boolean, Column, String

from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    ticker = Column(String(20))
    cik = Column(String(20))
    cusip = Column(String(20))
    exchange = Column(String(50))
    is_delisted = Column(Boolean)
    category = Column(String(50))
    sector = Column(String(50))
    industry = Column(String(50))
    sic = Column(String(20))
    sic_sector = Column(String(50))
    sic_industry = Column(String(50))
    fama_sector = Column(String(50))
    fama_industry = Column(String(50))
    currency = Column(String(10))
    location = Column(String(255))