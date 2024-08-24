# Financial AI Advisor for Elderly People

## Project Overview
This project is an AI-powered Financial Advisor specifically designed to assist elderly users with their financial queries and concerns. It aims to provide accessible, personalized financial advice using natural language processing and machine learning techniques.

## Key Features

1. **Personalized User Profiles**: The bot creates and maintains individual user profiles, storing relevant financial information securely.
2. **Sentiment Analysis**: It analyzes the user's emotional state to provide empathetic responses.
3. **Financial Context Recognition**: The bot identifies the specific financial context of each query (e.g., spending, saving, investments).
4. **Synthetic Spending Data**: For demonstration purposes, the bot generates realistic spending data to provide insights.
5. **Persistent Storage**: User profiles and conversation histories are securely stored for continuity across sessions.
6. **Natural Language Interaction**: Users can communicate with the bot using natural language, making it accessible for those who might struggle with complex interfaces.
7. **User Authentication**: Implements a login system to securely manage multiple users.

## Technical Details

- **Language**: Python
- **AI/ML Libraries**: OpenAI's GPT-3.5, Hugging Face Transformers
- **Data Storage**: MongoDB
- **User Interface**: Text-based interface (can be extended to voice interface for increased accessibility)
- **Backend Framework**: FastAPI
- **Frontend**: Streamlit

## Model and Technical Architecture

Our AI Financial Advisor application is built using a modern, modular architecture that separates concerns and allows for scalability and easy maintenance. Here's an overview of the key technical layers:

### Frontend Layer
- **Technology**: Streamlit
- **Purpose**: Provides an intuitive, web-based user interface for interacting with the AI Financial Advisor.
- **Key Features**:
  - User authentication and profile management
  - Chat interface for communicating with the AI
  - Display of financial insights and advice
  - Visualization of spending data and financial trends

### Backend Layer
- **REST API**: Built with FastAPI
  - Provides endpoints for user management, profile operations, and AI interactions
  - Handles request validation and response formatting
  - Implements JWT-based authentication for secure API access

- **Database**: MongoDB
  - Stores user profiles, financial data, and conversation histories
  - Provides efficient querying and updating of user information
  - Ensures data persistence across sessions

### Machine Learning Layer
- **Conversational AI**: OpenAI GPT-3.5-turbo
  - Generates human-like responses to user queries
  - Provides personalized financial advice based on user context
  - Handles a wide range of financial topics without extensive domain-specific training

- **Sentiment Analysis**: DistilBERT
  - Analyzes the emotional tone of user inputs
  - Allows the AI to provide empathetic responses
  - Fine-tuned on the SST-2 (Stanford Sentiment Treebank) dataset for efficient performance

- **Architecture**: Transformer-based models
  - Both GPT-3.5 and DistilBERT use the Transformer architecture
  - Excellent at capturing long-range dependencies in text
  - Enables understanding of complex financial queries and generation of coherent, contextually relevant responses

1. **Language Model - GPT-3.5 (OpenAI)**: Chosen for its advanced natural language understanding and generation capabilities. It produces context-aware, human-like responses, crucial for providing empathetic and personalized financial advice.

2. **Sentiment Analysis - DistilBERT (Hugging Face)**: A lightweight version of BERT, fine-tuned on the SST-2 (Stanford Sentiment Treebank) dataset. It's suitable for real-time sentiment analysis in our application.

3. **Transformer Architecture**: Both GPT-3.5 and DistilBERT are based on the Transformer architecture, ideal for understanding complex financial queries and generating coherent, contextually relevant responses.

## Setup and Installation
### Prerequisites
- Python 3.7+
- pip (Python package manager)
- MongoDB installed and running

### 1. Clone the repository
```bash
git clone https://github.com/alipala/ai4elderly1.git
cd ai4elderly1
```
### 2. Set up a virtual environment
```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Replace your_secret_key_here with a secure random string and your_openai_api_key_here with your actual OpenAI API key.
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=financial_advisor_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your_openai_api_key_here
API_URL=http://localhost:8000
```

### 5. Start MongoDB

### 6. Start the backend server
```bash
cd backend
uvicorn main:app --reload
```

### 7. Start the frontend
```bash
cd frontend
streamlit run streamlit_app.py
```

### 8. Access the application
Open your web browser and go to http://localhost:8501 to access the Streamlit interface

## Usage
1. Open the Streamlit app in your web browser (at http://localhost:8501).
2. Log in with test admin user
3. Create a new user profile(or load an existing one)
4. Generate syntetic spending data to have accurate advice based on this
3. Interact with the Financial AI Advisor by typing your financial queries or concerns.
4. View personalized advice, spending insights, and conversation history