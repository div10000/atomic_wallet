from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
import os
from dotenv import load_dotenv

# --- 1. Database Configuration (PostgreSQL) ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- 2. Database Models ---
class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    # Storing money as CENTS (Integer) to avoid float math errors
    balance_cents = Column(Integer, default=0) 

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("wallets.id"))
    receiver_id = Column(Integer, ForeignKey("wallets.id"))
    amount_cents = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# --- 3. Pydantic Schemas ---
class TransferRequest(BaseModel):
    sender_username: str
    receiver_username: str
    amount_dollars: float = Field(..., gt=0)

    @property
    def amount_cents(self):
        return int(self.amount_dollars * 100)

class WalletCreate(BaseModel):
    username: str

# --- 4. FastAPI Setup ---
app = FastAPI(title="AtomicWallet")

# Mount the static folder to serve the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. API Endpoints ---

@app.get("/")
def read_root():
    # Serves your Tailwind Frontend
    return FileResponse('static/index.html')

@app.post("/create_wallet")
def create_wallet(data: WalletCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(Wallet).filter(Wallet.user_name == data.username).first()
    if existing_user:
        return {"msg": "User already exists", "username": data.username}
    
    # Create new wallet with $100.00 bonus (10000 cents)
    new_wallet = Wallet(user_name=data.username, balance_cents=10000)
    db.add(new_wallet)
    db.commit()
    return {"msg": f"Wallet created for {data.username} with $100.00"}

@app.get("/balance/{username}")
def get_balance(username: str, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_name == username).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": username, 
        "balance": wallet.balance_cents / 100.0  # Convert cents back to dollars for display
    }

@app.post("/transfer")
def transfer_funds(req: TransferRequest, db: Session = Depends(get_db)):
    # --- THE FINTECH CORE LOGIC ---
    try:
        # 1. Start Transaction & Acquire Row Locks
        # with_for_update() generates "SELECT ... FOR UPDATE" SQL
        # This locks these specific rows so no other transaction can modify them
        # until this function finishes.
        
        # We fetch sender first to keep locking order consistent
        sender = db.query(Wallet).filter(Wallet.user_name == req.sender_username).with_for_update().first()
        receiver = db.query(Wallet).filter(Wallet.user_name == req.receiver_username).with_for_update().first()

        if not sender or not receiver:
            raise HTTPException(status_code=404, detail="One or more users not found")

        # 2. Check Balance (Safe because rows are locked)
        if sender.balance_cents < req.amount_cents:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # 3. Move Money (Atomic Swap)
        sender.balance_cents -= req.amount_cents
        receiver.balance_cents += req.amount_cents

        # 4. Create Audit Log
        txn_record = Transaction(
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount_cents=req.amount_cents
        )
        db.add(txn_record)
        
        # 5. Commit Transaction
        # This saves changes AND releases the locks
        db.commit()
        db.refresh(txn_record)
        
        return {
            "status": "success", 
            "tx_id": txn_record.id, 
            "message": f"Transferred ${req.amount_dollars} from {sender.user_name} to {receiver.user_name}"
        }

    except Exception as e:
        db.rollback() # If anything fails, undo everything
        raise e