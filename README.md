# AI Financial Advisor for Elderly

## Project Overview

This project is an AI-powered Financial Advisor bot specifically designed to assist elderly and visually impaired users with their financial queries and concerns. It aims to provide accessible, personalized financial advice using natural language processing and machine learning techniques.

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

## Model and Architecture Choices

1. **Language Model - GPT-3.5 (OpenAI)**: Chosen for its advanced natural language understanding and generation capabilities. It produces context-aware, human-like responses, crucial for providing empathetic and personalized financial advice.

2. **Sentiment Analysis - DistilBERT (Hugging Face)**: A lightweight version of BERT, fine-tuned on the SST-2 (Stanford Sentiment Treebank) dataset. It's suitable for real-time sentiment analysis in our application.

3. **Transformer Architecture**: Both GPT-3.5 and DistilBERT are based on the Transformer architecture, ideal for understanding complex financial queries and generating coherent, contextually relevant responses.

4. **Modular Design**: The project uses a modular design, separating concerns like user profile management, sentiment analysis, and response generation.

## Setup and Installation
### Prerequisites
- Python 3.7+
- pip (Python package manager)
- MongoDB installed and running
