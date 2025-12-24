# 🛒 AI Price Comparison – Shopping Agent

An AI-powered shopping agent that searches real shopping websites, compares prices in Indian Rupees (₹), and recommends the best deals using AI.

This project combines **real-time product search**, **AI-based query understanding**, **price comparison**, and **intelligent recommendations** into a single web application.

---

## 🚀 Features

- 🔍 Search products across **real shopping websites** (Amazon, Flipkart, etc.) using Google Shopping
- 🇮🇳 Prices shown in **Indian Rupees (INR)**
- 🤖 AI-powered product understanding using **Gemini**
- 📊 Intelligent ranking based on price and availability
- 🧠 AI-generated recommendations
- 💬 Shopping Assistant & Research Assistant
- 🗂 Vector database (ChromaDB) for semantic product search
- 🌐 Clean interactive UI built with **Streamlit**

---

## 🛠 Tech Stack

| Component | Technology |
|---------|------------|
| Frontend | Streamlit |
| Backend | Python |
| AI Model | Google Gemini (google-genai) |
| Shopping Data | SerpAPI (Google Shopping) |
| Vector DB | ChromaDB |
| Embeddings | Sentence Transformers |
| Environment | Python Virtual Environment |

---

## 📁 Project Structure

```text
Shopping-agent/
├── frontend/
│   ├── app.py
│   └── test_terminal.py
│
├── backend/
│   ├── app.py
│   ├── parser.py
│   ├── scraper.py
│   ├── recommender.py
│   ├── agents.py
│   ├── vector_db.py
│   ├── config.py
│   └── __init__.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions (Step-by-Step)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/ai-price-comparison.git
cd ai-price-comparison
```
### 2️⃣ Create and Activate Virtual Environment

Windows
```bash
python -m venv .venv
.\.venv\Scripts\activate
```
3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
4️⃣ Create .env File (IMPORTANT)

Create a file named .env in the root directory:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```
5️⃣ Run the Application
```
python -m streamlit run frontend/app.py
```


## ⚙️ How the System Works (Step-by-Step)

1. **User Query Input**  
   The user enters a natural language product query (e.g., “iPhone 15”, “Samsung S23 under 50,000”) through the Streamlit-based web interface.

2. **AI-Based Query Understanding**  
   The system uses the Gemini large language model to analyze the user query and extract structured information such as product name, preferences, region, and intent.

3. **Real-Time Shopping Website Search**  
   The extracted product information is sent to Google Shopping via SerpAPI, which searches real online shopping platforms (Amazon, Flipkart, etc.) and returns live product data.

4. **Data Normalization and Cleaning**  
   The raw shopping results are cleaned and normalized into a unified format containing product title, price, seller, rating, availability, and purchase links.

5. **Region and Currency Enforcement**  
   The system enforces India-specific search parameters and converts all prices to Indian Rupees (₹ INR) to ensure regional accuracy.

6. **Product Ranking and Filtering**  
   The retrieved products are ranked based on price, availability, and user preferences to identify the best deals.

7. **Vector Embedding Generation**  
   Each product is converted into numerical embeddings using Sentence Transformers and stored in a ChromaDB vector database for semantic understanding.

8. **AI-Powered Recommendation Generation**  
   Gemini analyzes the top-ranked real products and generates a concise, human-like recommendation highlighting the best option.

9. **Shopping Assistant Interaction**  
   The Shopping Assistant uses stored context and product embeddings to answer user follow-up questions related to pricing, sellers, and product comparisons.

10. **Research Assistant Interaction**  
    The Research Assistant provides deeper comparative analysis and product insights using AI reasoning and vector-based similarity search.

11. **Results Presentation**  
    The final ranked products, prices, sellers, and AI recommendation are displayed to the user through an interactive Streamlit interface.

12. **Graceful Fallback Handling**  
    If any AI component fails, the system automatically falls back to deterministic logic to ensure uninterrupted user experience.



------------------

🧑‍💻 Author

B. Umesh Kumar

AI & ML Project | 2025
