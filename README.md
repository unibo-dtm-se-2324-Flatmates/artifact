# Flatmate Manager App 🏠

A comprehensive web application designed to help flatmates manage their shared living space efficiently. Built with FastAPI for the backend and Streamlit for the frontend.

## ✨ Features

- **📅 Calendar**: Schedule and track shared events, cleaning duties, or house parties.
- **🛒 Shopping List**: Collaborative shopping list to keep track of what's needed.
- **💰 Expense Manager**: Track shared expenses, split bills, and simplify debt settlement.
- **⚙️ House Settings**: Configure house details and manage user profiles.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit, Pandas, Altair
- **Language**: Python

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Flatmate-Project-TEST2
   ```

2. **Create and activate a virtual environment** (Recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Running the Application

The application consists of two parts that need to run simultaneously.

### 1. Start the Backend API
Open a terminal and run:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`. You can view the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Start the Frontend Interface
Open a new terminal and run:
```bash
streamlit run frontend/app.py
```
The web application will open automatically in your default browser at [http://localhost:8501](http://localhost:8501).

## 📂 Project Structure

```
Flatmate-Project-TEST2/
├── backend/            # FastAPI backend
│   ├── routers/        # API endpoints (calendar, expenses, etc.)
│   ├── database.py     # Database configuration
│   ├── main.py         # Application entry point
│   └── models.py       # Data models
├── frontend/           # Streamlit frontend
│   ├── pages/          # Application pages
│   ├── app.py          # Main entry point
│   └── utils.py        # Utility functions
└── requirements.txt    # Project dependencies
```