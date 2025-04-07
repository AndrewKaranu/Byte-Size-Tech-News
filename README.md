# Byte Sized Tech News

## Overview

Byte Sized Tech News is a project that delivers concise and relevant tech updates directly to your inbox. It combines a user-friendly frontend for signup with a sophisticated backend system for content aggregation, processing, and delivery.

## Key Features

*   **User Signup:** A React-based frontend allows users to easily subscribe to the newsletter.
*   **Content Aggregation:** A Python script scrapes tech news from various sources using libraries like BeautifulSoup and Feedparser.
*   **Ranking and Tagging:** Natural Language Processing (NLP), Machine Learning (ML), and data handling techniques are employed to rank and tag articles based on relevance and category.
*   **Summarization:** Generative AI is used to create concise summaries of the selected articles.
*   **Email Delivery:** AWS Simple Email Service (SES) is used to reliably deliver the newsletter to subscribers.
*   **Admin Interface:** A Flask-based backend provides an admin interface for managing articles, batches, and settings.
*   **Terminal Interface:** A terminal interface is available for interacting with the system.

## Technologies Used

### Frontend

*   React
*   CSS

### Backend

*   Flask (Python)
*   Flask-SQLAlchemy
*   boto3 (AWS SDK for Python)
*   google.generativeai
*   BeautifulSoup
*   Feedparser
*   nltk
*   scikit-learn
*   APScheduler


## Usage

1.  **Signup:** Access the frontend in your browser and sign up for the newsletter.
2.  **Admin Interface:** Access the admin interface via the `/admin` route in your browser.  You'll need to implement proper authentication to protect this.
3.  **Scheduler:** The backend includes a scheduler that automates article collection, summarization, and newsletter dispatch.  Configure the scheduler settings in `config.py` or via environment variables.
4.  **Terminal:** Interact with the system using the terminal interface in the frontend. Type `help` for a list of available commands.
