# 🛡️ AtomicWallet

**AtomicWallet** is a high-performance Fintech API designed to handle financial transactions with strict **ACID guarantees**. 

It uses **PostgreSQL Row-Level Locking** to prevent Race Conditions (Double-Spending), ensuring that high-concurrency transfers remain accurate and secure.

## 🚀 Key Features

* **Concurrency Control:** Uses `SELECT ... FOR UPDATE` to lock database rows during transfers, preventing race conditions.
* **ACID Transactions:** Ensures all-or-nothing execution. If one step fails, the entire transaction rolls back.
* **Precision Math:** Uses Integer-based arithmetic (cents) to avoid Floating Point errors common in financial software.
* **Modern Stack:** Built with **FastAPI** (Python) for high-performance async processing and **Pydantic** for strict data validation.

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, FastAPI
* **Database:** PostgreSQL 16+
* **ORM:** SQLAlchemy (Async)
* **Frontend:** HTML5, Vanilla JS, Tailwind CSS (via CDN)
* **Testing:** Custom Python script for simulating concurrent requests.

---

## 💻 Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/atomic-wallet-fastapi.git
cd atomic-wallet-fastapi
```

### 2. Set up the Environment

It is recommended to use a virtual environment.

```bash
# Create virtual env
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

Ensure PostgreSQL is running, then:

1. Create a database named `atomicwallet`
2. Create a `.env` file in the root directory with your connection string:

```plaintext
# .env file
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/atomicwallet"
```

> **Note:** Replace `YOUR_PASSWORD` with your actual PostgreSQL password.

## ▶️ Running the Application

Start the development server using Uvicorn:

```bash
uvicorn main:app --reload
```

- **Frontend UI:** Open http://localhost:8000 in your browser
- **API Docs:** Open http://localhost:8000/docs for Swagger UI

## 🧪 Testing Concurrency (The "Double Spend" Test)

To prove the system handles race conditions, a stress-test script is included. This script attempts to send money faster than the database can write, simulating a hacker attack.

1. Keep the server running in one terminal
2. Open a new terminal
3. Run the test:

```bash
python test_concurrency.py
```

**Expected Result:** The system will process transactions sequentially. The final balance will be exactly correct, with zero "double spend" errors.

## 📂 Project Structure

```plaintext
atomic_wallet/
│
├── static/              # Frontend Assets
│   └── index.html       # Single Page UI
├── main.py              # Application Entry Point & Logic
├── models.py            # Database Models
├── requirements.txt     # Python Dependencies
└── test_concurrency.py  # Stress Test Script
```

---

📿 Chant Hare Krishna & Be Happy