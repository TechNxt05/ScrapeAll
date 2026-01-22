# ScrapeAll - Intelligent Web Scraping & Data Analysis Platform

![ScrapeAll Banner](https://img.shields.io/badge/Status-Operational-success) ![License](https://img.shields.io/badge/License-MIT-blue) ![Version](https://img.shields.io/badge/Version-1.0.0-purple)

**ScrapeAll** is an advanced, all-in-one platform designed to democratize web data extraction. Extracting meaningful data from the modern web is often plagued by complexity—from handling dynamic JavaScript and anti-bot measures to parsing messy HTML structures. **ScrapeAll** solves these challenges by combining robust, multi-method scraping (Static, Playwright, Selenium) with state-of-the-art AI analysis. This unique approach allows users to instantly turn any URL into actionable intelligence, structured summaries, and chat-ready knowledge bases without writing a single line of code.

## 🛠️ Tech Stack

### Frontend (Modern & Responsive)
*   **Framework**: [Next.js 14](https://nextjs.org/) (React)
*   **Styling**: Valid CSS + Tailwind CSS (Glassmorphism Design System)
*   **Icons**: Lucide React
*   **State Management**: React Hooks + Context API
*   **Build Tool**: TypeScript

### Backend (Robust & Scalable)
*   **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **Database**: SQLAlchemy ORM (SQLite/PostgreSQL compatible)
*   **AI Engine**: LangChain integration with multi-provider support (OpenAI, Groq, Gemini, HuggingFace)
*   **Vector DB**: FAISS (for RAG/Chat memory)

### Scraping Engine (The "Brain")
*   **StaticScraper**: `Requests` + `BeautifulSoup` (Fast, for simple sites)
*   **PlaywrightScraper**: Headless browser for modern, dynamic SPAs
*   **SeleniumScraper**: Robust fallback for stubborn websites
*   **SmartOrchestrator**: Automatically selects the best method and attempts fallbacks on failure.

## ✨ Key Features

### 1. 🤖 AI-Powered Analysis
Don't just get HTML. ScrapeAll uses LLMs to instantly provide:
*   **Executive Summary**: A concise overview of the page content.
*   **Key Points**: Bulleted takeaways.
*   **Entity Recognition**: Auto-detected Companies, People, and Locations.

### 2. 💬 Data Chat (RAG)
Talk to your data. ScrapeAll indexes scraped content into a Vector Database, allowing you to ask follow-up questions like:
> "What is the pricing model mentioned on this page?"
> "Compare the features listed here with the previous URL."

### 3. 🕸️ Multi-Source Knowledge Base
Create a project and add multiple URLs. The AI aggregates context from all sources, allowing for cross-page reasoning and comparison.

### 4. 🕵️‍♂️ Visual CSS Selector
Target specific data. Use the "Advanced Options" to provide a CSS selector (e.g., `.pricing-table` or `#main-content`) to scrape only what matters, reducing noise and token usage.

### 5. 📥 Data Export
Take your data with you. seamless export of summaries and extracted points to **JSON** (for developers) or **Markdown** (for documentation).

### 6. 📝 Form Detection
Automatically detects input forms on a webpage, analyzing their fields, types, and requirements—a precursor to automated form filling.

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Chrome/Chromium installed

### ⬇️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/ScrapeAll.git
    cd ScrapeAll
    ```

2.  **Start the Backend**
    ```bash
    ./start_backend.bat
    ```
    *This installs Python dependencies and starts the FastAPI server on port 8001.*

3.  **Start the Frontend**
    ```bash
    ./start_frontend.bat
    ```
    *This installs Node dependencies and starts the Next.js app on port 3000.*

4.  **Access the App**
    Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📄 API Documentation
Full API documentation is available at [http://localhost:8001/docs](http://localhost:8001/docs) when the backend is running.

## 🤝 Contributing
Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
