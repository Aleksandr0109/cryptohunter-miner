# core/models.py — ПОЛНАЯ ВЕРСИЯ С PendingDeposit
from sqlalchemy import (
    Column, BigInteger, String, DECIMAL, TIMESTAMP, Integer,
    func, Text, Boolean, ForeignKey, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_seen = Column(TIMESTAMP, server_default=func.now())
    wallet_address = Column(String(255), nullable=True)
    invested_amount = Column(DECIMAL(15,6), default=0)
    free_mining_balance = Column(DECIMAL(15,6), default=0)
    total_earned = Column(DECIMAL(15,6), default=0)
    mining_speed = Column(DECIMAL(5,3), default=1.0)
    last_activity = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    referral_count = Column(Integer, default=0)
    referrer_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    status = Column(String(20), default='active')
    language = Column(String(10), default='ru')
    notifications = Column(Boolean, default=True)

    # ДЛЯ MINI-APP
    pending_deposit = Column(DECIMAL(15,6), nullable=True)
    pending_address = Column(String(255), nullable=True)

    referrals = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")
    referred_by = relationship("Referral", back_populates="referred", foreign_keys="Referral.referred_id", uselist=False)

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    source_channel = Column(String(255), nullable=False)
    source_type = Column(String(50), default='group')
    found_at = Column(TIMESTAMP, server_default=func.now())
    interest_keywords = Column(Text, default='[]')
    contact_attempts = Column(Integer, default=0)
    conversion_status = Column(String(20), default='not_contacted')
    interest_score = Column(Integer, default=0)
    last_contact = Column(TIMESTAMP, nullable=True)
    notes = Column(Text, nullable=True)

    @property
    def status(self):
        return self.conversion_status

    @status.setter
    def status(self, value):
        self.conversion_status = value

    @property
    def keywords_list(self):
        if self.interest_keywords and self.interest_keywords != '[]':
            try:
                return json.loads(self.interest_keywords)
            except:
                return []
        return []

    @keywords_list.setter
    def keywords_list(self, value):
        if isinstance(value, list):
            self.interest_keywords = json.dumps(value, ensure_ascii=False)
        else:
            self.interest_keywords = '[]'

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    type = Column(String(20), nullable=False)  # deposit, withdraw, bonus
    amount = Column(DECIMAL(15,6), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    tx_hash = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    referred_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    level = Column(Integer, default=1)
    bonus_paid = Column(DECIMAL(15,6), default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(20), default='active')

    referrer = relationship("User", back_populates="referrals", foreign_keys=[referrer_id])
    referred = relationship("User", back_populates="referred_by", foreign_keys=[referred_id])

class PendingDeposit(Base):
    __tablename__ = "pending_deposits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(DECIMAL(15, 6), nullable=False)
    comment = Column(String(255), nullable=False, unique=True, index=True)
    address = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, expired, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<PendingDeposit {self.id} user={self.user_id} amount={self.amount} status={self.status}>"
