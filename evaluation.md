# LLM Evaluation for FloodGPT

This document outlines the evaluation strategy for the FloodGPT agent, explaining the components of the `evaluation.py` script and the importance of the golden dataset.

## The `evaluation.py` Script

The `evaluation.py` script is the automated testing framework for our agent. It is designed to rigorously measure the performance of the agent's core capabilities: generating correct SQL and producing high-quality insights.

The script performs two main types of evaluation:

### 1. SQL Generation Evaluation

This tests the agent's ability to translate a natural language question into a correct SQL query.

*   **How it works:** The script takes a question from the `golden_dataset.csv`, runs it through the agent's SQL generation and validation logic, and then compares the output against the `golden_sql` from the dataset.
*   **Metrics:**
    *   **Exact Match:** A strict check to see if the generated SQL is character-for-character identical to the golden SQL.
    *   **Execution Accuracy:** A more practical and robust check. It executes both the generated SQL and the golden SQL and passes if they both return the exact same data. This is the most important metric for this stage.

### 2. Insight Evaluation with RAGAS

This tests the quality of the natural language insight that the agent generates from the data.

*   **How it works:** After getting the data from the SQL query, the script runs the agent's `generate_insight_from_data` function. It then uses the RAGAS framework to score this insight based on the original question, the data itself (context), and the `ground_truth_answer` from the golden dataset.
*   **Metrics:**
    *   **Faithfulness:** Does the insight stick to the facts in the data? (Detects hallucinations).
    *   **Answer Relevancy:** Is the insight actually relevant to the user's question?
    *   **Answer Correctness:** How factually correct is the insight when compared to the ground truth answer?

### How to Use the Script

1.  **Install Dependencies:** Ensure `ragas` and `datasets` are installed (`pip install ragas datasets`).
2.  **Populate the Golden Dataset:** Add more test cases to `golden_dataset.csv`.
3.  **Run from Terminal:** Execute `python evaluation.py`.
4.  **Review the Output:** The script will print two reports: one for the SQL evaluation and one for the RAGAS insight evaluation, giving you a clear score for the agent's performance.

## The Golden Dataset (`golden_dataset.csv`)

### Why Do We Need a Golden Dataset?

The golden dataset is the **ultimate source of truth** for our project. It's the answer key we use to grade our AI agent's performance. Without it, we are just guessing if our agent is good or not.

1.  **Provides a Benchmark for Accuracy:** It's the only way to know if the SQL your agent generates is *correct*. The "Execution Accuracy" metric is a perfect example: we run the agent's SQL, we run the golden SQL, and we check if the results are identical.
2.  **Enables Objective and Repeatable Evaluation:** It removes subjectivity. Instead of someone saying "I think the agent is better now," you can say "Our execution accuracy improved from 85% to 92% on the golden dataset." This is crucial for tracking progress.
3.  **Tests for Edge Cases and Diversity:** It allows you to purposefully include a wide range of questions—simple ones, complex ones, and tricky ones—to ensure your agent is robust.
4.  **Evaluates Both Halves of the Agent:** It contains both the `golden_sql` (to test the logic) and the `ground_truth_answer` (to test the final generated text).

### How Many Records Make an "Ideal" Golden Dataset?

There is no single magic number. **Diversity and quality are far more important than sheer quantity.**

However, here is a practical guide:

*   **Initial Development (Where you are now):**
    *   **Ideal Size:** **20 - 50 records.**
    *   **Focus:** Cover the most common and important types of questions (e.g., a `SUM`, an `AVG`, a `COUNT`, a `LIMIT`, a `WHERE` clause, etc.).

*   **Pre-Production / Mature System:**
    *   **Ideal Size:** **100 - 500+ records.**
    *   **Focus:** Be more rigorous and cover a much wider range of edge cases and complex queries to build high confidence before deployment.
