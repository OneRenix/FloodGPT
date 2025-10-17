# Technical Documentation

This document provides a comprehensive technical overview of the FloodGPT application.

## 1. Project Overview

FloodGPT is an AI-powered web application that simplifies access to government data on flood control projects. It allows users to ask questions in plain English, and the system retrieves and presents the information in an easy-to-understand format. The goal is to make complex government data accessible to a wider audience, including citizens, journalists, and researchers.

### Problem Statement

This AI Agent uses an AI and Text-to-SQL approach to collect and simplify government reports, news, and audits into clear, easy-to-read insights.

### Key Features

*   **Natural Language Queries:** Users can ask questions in natural language, and the application will convert them into SQL queries.
*   **Data Visualization:** The application can generate a variety of charts to visualize the data, including bar charts, pie charts, and line charts.
*   **Data Insights:** The application can generate a human-friendly explanation of the data to help users understand the key insights and patterns.
*   **Guardrails:** The application has a set of guardrails to protect it from a variety of attacks, including prompt injection, SQL injection, and inappropriate content.

## 2. Architecture

### High-Level Overview

The application has a simple client-server architecture. The frontend is a single-page application built with HTML, CSS, and JavaScript, served as static files. The backend is a Python application that uses FastAPI to create a web server and LangChain to interact with the LLM.

### Architecture and Workflow Diagram

## 3. Components

### Frontend

*   **`index.html`:** This is the main HTML file that contains the structure of the application.
*   **`static/css/style.css`:** This file contains all the custom styles for the application.
*   **`static/js/script.js`:** This file contains all the JavaScript code for interactivity, including form submission, handling API responses, and rendering charts.

### Backend

*   **`api.py`:** This file contains the main FastAPI application. It defines the API endpoints, serves the frontend, and integrates all the security features.
*   **`main_agent.py`:** This file contains the core LangChain agent logic. It uses `langgraph` to define the agent workflow as a state machine.
*   **`tools.py`:** This file contains the tools that the LangChain agent uses to interact with the database and generate the visualizations.
*   **`llm_config.py`:** This file contains the configuration for the language model.
*   **LangGraph:** A library for building stateful, multi-step applications with LLMs. It is used in `main_agent.py` to define the agent workflow as a state machine.

### Database

*   **`analytics.db`:** This is a SQLite database that contains the data about the flood control projects.

## 4. Security

The application includes several security features to protect against common web vulnerabilities and abuse.

### reCAPTCHA v3

*   **Purpose:** To protect the form from spam and abuse by bots.
*   **Implementation:**
    *   **Frontend:** The reCAPTCHA v3 site key is included in `index.html`, and the JavaScript in `script.js` generates a token for each form submission.
    *   **Backend:** The `/stream-agent` endpoint in `api.py` verifies the token with Google's reCAPTCHA service using the secret key (stored as an environment variable `RECAPTCHA_SECRET_KEY`). Submissions with a score below 0.3 are rejected.

### Honeypot Field

*   **Purpose:** To trap bots that blindly fill out all form fields.
*   **Implementation:**
    *   **Frontend:** A hidden input field (`email_confirm`) is included in the form in `index.html`. It is hidden from human users with CSS.
    *   **Backend:** The `/stream-agent` endpoint in `api.py` checks if this field has a value. If it does, the request is rejected.

### Rate Limiting

*   **Purpose:** To prevent brute-force attacks and denial-of-service attacks.
*   **Implementation:** The `slowapi` library is used to apply a rate limit to the `/stream-agent` endpoint. The limit is set to 5 requests per minute per IP address.

### Iframe Embedding Prevention

*   **Purpose:** To prevent clickjacking attacks, where the application is embedded in a malicious website.
*   **Implementation:** A middleware in `api.py` adds the `X-Frame-Options: DENY` and `Content-Security-Policy: frame-ancestors 'none'` headers to all responses.

## 5. Technologies Used

### Frontend

*   **HTML:** The standard markup language for creating web pages.
*   **Tailwind CSS:** A utility-first CSS framework for rapid UI development.
*   **JavaScript:** A programming language that enables interactive web pages.
*   **jQuery:** A fast, small, and feature-rich JavaScript library.
*   **DataTables:** A plug-in for the jQuery JavaScript library for advanced table interactions.
*   **Plotly.js:** A high-level, declarative charting library.
*   **Lucide:** An open-source icon set.
*   **Showdown:** A JavaScript Markdown to HTML converter.

### Backend

*   **Python:** A high-level, general-purpose programming language.
*   **FastAPI:** A modern, fast web framework for building APIs.
*   **LangChain:** A framework for developing applications powered by language models.
*   **SQLAlchemy:** The Python SQL toolkit and Object Relational Mapper.
*   **Uvicorn:** An ASGI web server implementation for Python.
*   **slowapi:** A rate-limiting library for Starlette and FastAPI.
*   **httpx:** A fully featured HTTP client for Python 3.
*   **Cerberus:** A lightweight and extensible data validation library for Python.

### Database

*   **SQLite:** A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

## 6. File Structure

```
. (project root)
├── .dockerignore                  # Specifies files to ignore when building a Docker image.
├── .env                           # Stores environment variables (e.g., API keys). Not version controlled.
├── .gitignore                     # Specifies files to ignore for Git version control.
├── .python-version                # Specifies the Python version for the project.
├── api.py                         # The main FastAPI application file, containing API endpoints and security.
├── create_all_indexes.py          # A script to create database indexes for performance.
├── deploy.md                      # Deployment instructions.
├── Dockerfile                     # Instructions for building the application's Docker image.
├── formatter.py                   # Contains the DataFormatter class for chart data.
├── gemini.bat                     # A batch script for running the application.
├── index.html                     # The main HTML file for the frontend.
├── LICENSE.txt                    # The project's software license.
├── llm_config.py                  # Configuration for the language model.
├── main_agent.py                  # Contains the core LangChain agent and graph logic.
├── pyproject.toml                 # Project metadata and dependencies for Python packaging.
├── README.md                      # The main README file for the project.
├── requirements.txt               # A list of Python dependencies.
├── technical_documentation.md     # This technical documentation file.
├── tools.py                       # Contains the tools used by the LangChain agent.
├── uv.lock                        # A lock file for the uv package manager.
├── static/
│   ├── css/
│   │   └── style.css              # The main stylesheet for the application.
│   └── js/
│       └── script.js              # The main JavaScript file for the application.
├── __pycache__/                   # Directory for Python's cached bytecode.
├── .git/                          # Directory for the Git version control system.
├── .venv/                         # Directory for the Python virtual environment.
├── db/
│   └── analytics.db               # The SQLite database file.
└── src_data_loader/
    └── analyze_flood_control.ipynb  # A Jupyter notebook for data analysis.
```

## 7. Backend Script Documentation

### `api.py`

This script contains the main FastAPI application. It is responsible for serving the frontend, handling API requests, and implementing security measures.

**Modules Used:**
*   `fastapi`: The main web framework.
*   `fastapi.staticfiles`: Used to serve static files like CSS and JavaScript.
*   `slowapi`: Used for rate limiting.
*   `httpx`: Used to make HTTP requests for reCAPTCHA verification.
*   `pydantic`: Used for data validation of request bodies.

**Key Components:**
*   **FastAPI app instance:** The main application object.
*   **Static Files Mount:** Mounts the `static` directory to serve CSS and JavaScript files.
*   **Security Middleware:** Adds headers to prevent iframe embedding.
*   **Rate Limiter:** Initializes and applies rate limiting to endpoints.
*   **`/stream-agent` Endpoint:** The main API endpoint that receives user questions, performs security checks (reCAPTCHA, honeypot, rate limiting), and streams the agent's response.
*   **`/` Endpoint:** Serves the `index.html` file.

### `main_agent.py`

This script contains the main LangChain agent. It uses `langgraph` to define the agent workflow as a state machine.

**Modules Used:**
*   `langgraph.graph`: Used for creating the LangChain agent workflow.
*   `tools`: A custom module that contains the tools that the LangChain agent uses.
*   `formatter`: A custom module that contains the `DataFormatter` class.
*   `llm_config`: A custom module that contains the configuration for the language model.

**Functions:**
*   `content_classification_node(state: AgentState) -> dict`: Classifies the content of the insight.
*   `insight_node(state: AgentState) -> dict`: Generates an insight from the data.
*   `validate_question_node(state: AgentState) -> dict`: Validates the user's question.
*   `sql_generation_node(state: AgentState) -> dict`: Generates a SQL query.
*   `sql_validation_node(state: AgentState) -> dict`: Validates the SQL query.
*   `sql_execution_node(state: AgentState) -> dict`: Executes the SQL query.
*   `visualizer_node(state: AgentState) -> dict`: Recommends a visualization type.
*   `formatter_node(state: AgentState) -> dict`: Formats the data for visualization.

### `tools.py`

This file contains the tools that the LangChain agent uses to interact with the database and generate the visualizations.

**Modules Used:**
*   `pandas`: Used for data manipulation and analysis.
*   `sqlalchemy`: Used for interacting with the SQLite database.
*   `langchain_core.prompts.ChatPromptTemplate`: Used for creating prompts for the language model.
*   `cerberus`: Used for data validation and sanitization.

**Functions:**
*   `sanitize_and_validate_data(df: pd.DataFrame) -> pd.DataFrame`: Sanitizes and validates data.
*   `is_prompt_injection(question: str) -> bool`: Classifies prompt injection attempts.
*   `is_question_related(question: str, db_schema: str) -> bool`: Classifies if a question is related to the database.
*   `generate_sql_query(question: str, db_schema: str) -> str`: Generates a SQL query.
*   `validate_and_correct_sql(sql_query: str, db_schema: str) -> dict`: Validates and corrects a SQL query.
*   `execute_sql_query(sql_query: str) -> dict`: Executes a SQL query.
*   `recommend_visualization(user_question: str, sql_result_df: pd.DataFrame) -> str`: Recommends a visualization.
*   `generate_insight_from_data(question: str, df: pd.DataFrame) -> str`: Generates an insight from data.

### `llm_config.py`

This file contains the configuration for the language model.

**Modules Used:**
*   `langchain_google_genai`: Used for interacting with the Google Generative AI models.

**Functions:**
*   `get_llm(model_name: str, temperature: float) -> ChatGoogleGenerativeAI`: Returns a configured instance of the language model.

### `formatter.py`

This script contains the `DataFormatter` class, which is responsible for formatting data for visualizations.

**Modules Used:**
*   `pandas`: Used for data manipulation and analysis.

**Classes:**
*   `DataFormatter`: A class for formatting data for visualizations.

### `create_all_indexes.py`

This script is used to create all the necessary indexes for the database.

**Modules Used:**
*   `sqlite3`: Used for interacting with the SQLite database.

**Functions:**
*   `create_indexes()`: Creates indexes on the tables in the database.