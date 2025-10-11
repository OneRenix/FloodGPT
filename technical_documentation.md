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

The application has a simple client-server architecture. The frontend is a single HTML file that uses Tailwind CSS for styling and JavaScript for interactivity. The backend is a Python application that uses FastAPI to create a web server and LangChain to interact with the LLM.

### Architecture and Workflow Diagram

```mermaid
graph TD
    subgraph User
        A[User Enters Query]
    end

    subgraph Frontend
        B[Web Interface (index.html)]
    end

    subgraph Backend
        C[FastAPI (api.py)]
        subgraph LangChain Agent (main_agent.py)
            D[Start] --> E{Validate Question};
            E --> F[Generate SQL];
            F --> G{Validate SQL};
            G --> H[Execute SQL];
            H --> I{Recommend Viz};
            I --> J[Format Data];
            J --> K[Generate Insight];
            K --> L{Classify Content};
            L --> M[End];
        end
        N[Tools (tools.py)]
        O[LLM Config (llm_config.py)]
        P[Database (analytics.db)]
    end

    A --> B;
    B -- HTTP Request --> C;
    C -- Invokes --> D;
    E -- Uses --> N;
    F -- Uses --> N;
    G -- Uses --> N;
    H -- Uses --> N;
    I -- Uses --> N;
    J -- Uses --> N;
    K -- Uses --> N;
    L -- Uses --> N;
    N -- Interacts with --> P;
    D -- Uses --> O
    C -- Streams Response --> B;
```

## 3. Components

### Frontend

*   **`index.html`:** This is the main HTML file that contains the structure of the application.
*   **CSS:** The application uses Tailwind CSS for styling. The CSS is included in the `<style>` section of the `index.html` file.
*   **JavaScript:** The application uses JavaScript for interactivity. The JavaScript is included in the `<script>` section of the `index.html` file.

### Backend

*   **`main_agent.py`:** This is the main backend file that contains the FastAPI application and the LangChain agent. It uses `langgraph` to define the agent workflow as a state machine.
*   **`tools.py`:** This file contains the tools that the LangChain agent uses to interact with the database and generate the visualizations. It uses the `langchain_core.output_parsers.StrOutputParser` to parse the output of the language model.
*   **`llm_config.py`:** This file contains the configuration for the language model. It uses the `langchain_google_genai` library to interact with the Google Generative AI models.
*   **LangGraph:** A library for building stateful, multi-step applications with LLMs. It is used in `main_agent.py` to define the agent workflow as a state machine.

### Database

*   **`analytics.db`:** This is a SQLite database that contains the data about the flood control projects.

## 5. Technologies Used

### Frontend

*   **HTML:** The standard markup language for creating web pages.
*   **Tailwind CSS:** A utility-first CSS framework for rapid UI development.
*   **JavaScript:** A programming language that enables interactive web pages.
*   **jQuery:** A fast, small, and feature-rich JavaScript library.
*   **DataTables:** A plug-in for the jQuery JavaScript library. It is a highly flexible tool, built upon the foundations of progressive enhancement, that adds advanced interaction controls to any HTML table.
*   **Plotly.js:** A high-level, declarative charting library. Plotly.js is the foundational library for all of Plotly's products.
*   **Lucide:** A community-maintained fork of Feather Icons, an open-source icon set.
*   **Showdown:** A JavaScript Markdown to HTML converter, based on the original works of John Gruber.

### Backend

*   **Python:** A high-level, general-purpose programming language.
*   **FastAPI:** A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **LangChain:** A framework for developing applications powered by language models.
*   **SQLAlchemy:** The Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
*   **Uvicorn:** An ASGI web server implementation for Python.
*   **Cerberus:** A lightweight and extensible data validation library for Python.

### Database

*   **SQLite:** A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

## 6. File Structure

```
. (project root)
├── .dockerignore                  # Specifies which files to ignore when building the Docker image
├── .env                           # Stores environment variables for the application
├── .gitignore                     # Specifies which files to ignore when committing to Git
├── .python-version                # Specifies the Python version to be used for the project
├── api.py                         # Contains the FastAPI application that serves the frontend and the LangChain agent
├── create_all_indexes.py          # A script to create all the necessary indexes for the database
├── deploy.md                      # Contains instructions on how to deploy the application
├── Dockerfile                     # Contains the instructions for building the Docker image
├── formatter.py                   # Contains the DataFormatter class that formats the data for the visualizations
├── gemini.bat                     # A batch script for running the application
├── guardrails.md                  # Contains the documentation for the guardrails
├── index.html                     # The main HTML file for the application
├── LICENSE.txt                    # The license for the project
├── llm_config.py                  # Contains the configuration for the language model
├── main_agent.py                  # Contains the main LangChain agent
├── pyproject.toml                 # Specifies the dependencies for the project
├── README.md                      # The main README file for the project
├── recommendation.md              # Contains the documentation for the recommendation engine
├── requirements.txt               # Specifies the Python dependencies for the project
├── technical_documentation.md     # The technical documentation for the project
├── tools.py                       # Contains the tools that the LangChain agent uses
├── uv.lock                        # A lock file for the uv package manager
├── __pycache__                    # Contains the compiled Python files
├── .git                           # Contains the Git repository
├── .venv                          # Contains the Python virtual environment
├── db
│   └── analytics.db               # The SQLite database that contains the data for the application
└── src_data_loader
    └── analyze_flood_control.ipynb  # A Jupyter notebook for analyzing the flood control data
```

## 7. Backend Script Documentation

### `main_agent.py`

This script contains the main FastAPI application and the LangChain agent. It uses `langgraph` to define the agent workflow as a state machine.

**Modules Used:**

*   `logging`: Used for logging information and errors.
*   `json`: Used for working with JSON data.
*   `dotenv`: Used for loading environment variables from a `.env` file.
*   `typing`: Used for providing type hints.
*   `pandas`: Used for data manipulation and analysis.
*   `langchain.chains`: Used for creating LangChain chains.
*   `langchain.prompts`: Used for creating prompts for the language model.
*   `langgraph.graph`: Used for creating the LangChain agent workflow.
*   `tools`: A custom module that contains the tools that the LangChain agent uses.
*   `formatter`: A custom module that contains the `DataFormatter` class.
*   `llm_config`: A custom module that contains the configuration for the language model.
*   `langchain_community.utilities.SQLDatabase`: Used for interacting with the SQLite database.

**Functions:**

*   `content_classification_node(state: AgentState) -> dict`:
    *   Classifies the content of the insight to ensure that it is appropriate.
*   `insight_node(state: AgentState) -> dict`:
    *   Generates an insight from the data.
*   `validate_question_node(state: AgentState) -> dict`:
    *   Validates the user's question to ensure that it is related to the database and does not contain any harmful keywords.
*   `sql_generation_node(state: AgentState) -> dict`:
    *   Generates a SQL query based on the user's question.
*   `sql_validation_node(state: AgentState) -> dict`:
    *   Validates the SQL query to ensure that it is syntactically correct.
*   `sql_execution_node(state: AgentState) -> dict`:
    *   Executes the SQL query against the database.
*   `visualizer_node(state: AgentState) -> dict`:
    *   Recommends a visualization type based on the query result.
*   `formatter_node(state: AgentState) -> dict`:
    *   Formats the data into a chart-ready JSON object.
*   `main()`:
    *   The main function for testing the application from the command line.

### `tools.py`

This file contains the tools that the LangChain agent uses to interact with the database and generate the visualizations. It uses the `langchain_core.output_parsers.StrOutputParser` to parse the output of the language model.

**Modules Used:**

*   `logging`: Used for logging information and errors.
*   `pandas`: Used for data manipulation and analysis.
*   `json`: Used for working with JSON data.
*   `re`: Used for working with regular expressions.
*   `sqlalchemy`: Used for interacting with the SQLite database.
*   `langchain_community.utilities.SQLDatabase`: Used for interacting with the SQLite database.
*   `langchain_core.prompts.ChatPromptTemplate`: Used for creating prompts for the language model.
*   `langchain_core.output_parsers.StrOutputParser`: Used for parsing the output of the language model.
*   `cerberus`: Used for data validation and sanitization.
*   `llm_config`: A custom module that contains the configuration for the language model.

**Functions:**

*   `sanitize_and_validate_data(df: pd.DataFrame) -> pd.DataFrame`:
    *   Sanitizes and validates the data in a Pandas DataFrame.
*   `is_prompt_injection(question: str) -> bool`:
    *   Classifies a user's question as a prompt injection attempt or not.
*   `is_question_related(question: str, db_schema: str) -> bool`:
    *   Classifies a user's question as related or unrelated to the database schema.
*   `generate_sql_query(question: str, db_schema: str) -> str`:
    *   Takes a user question and schema, and generates a SQL query.
*   `validate_and_correct_sql(sql_query: str, db_schema: str) -> dict`:
    *   Validates a SQL query against the schema and corrects it if needed.
*   `execute_sql_query(sql_query: str) -> dict`:
    *   Executes a validated SQL query and returns the results as a Pandas DataFrame.
*   `recommend_visualization(user_question: str, sql_result_df: pd.DataFrame) -> str`:
    *   Recommends a data visualization based on the user's question and a DataFrame.
*   `generate_insight_from_data(question: str, df: pd.DataFrame) -> str`:
    *   Generates a human-friendly insight from the data.

### `llm_config.py`

This file contains the configuration for the language model. It uses the `langchain_google_genai` library to interact with the Google Generative AI models.

**Modules Used:**

*   `os`: Used for interacting with the operating system.
*   `langchain_google_genai`: Used for interacting with the Google Generative AI models.

**Functions:**

*   `get_llm(model_name: str, temperature: float) -> ChatGoogleGenerativeAI`:
    *   Returns a configured instance of the `ChatGoogleGenerativeAI` class.

### `formatter.py`

This script contains the `DataFormatter` class, which is responsible for formatting data for visualizations.

**Modules Used:**

*   `pandas`: Used for data manipulation and analysis.

**Classes:**

*   `DataFormatter`:
    *   A class for formatting data for visualizations.

**Methods:**

*   `format_for_visualization(df: pd.DataFrame, viz_type: str) -> dict`:
    *   Formats a Pandas DataFrame for a specific visualization type.

### `create_all_indexes.py`

This script is used to create all the necessary indexes for the database. This can improve the performance of the database queries.

**Modules Used:**

*   `sqlite3`: Used for interacting with the SQLite database.

**Functions:**

*   `create_indexes()`:
    *   Creates indexes on the tables in the database.
