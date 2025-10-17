import pandas as pd
from datasets import Dataset
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Import actual agent components ---
# Note: This assumes the script is run from the project root.
from main_agent import db
from tools import generate_sql_query, execute_sql_query, generate_insight_from_data, validate_and_correct_sql

# --- 1. Golden Dataset ---
# Load the golden dataset from a CSV file.
try:
    golden_dataset_df = pd.read_csv("golden_dataset.csv")
    golden_dataset_data = golden_dataset_df.to_dict(orient="records")
except FileNotFoundError:
    logging.error("golden_dataset.csv not found. Please create it and ensure it has 'question', 'golden_sql', and 'ground_truth_answer' columns.")
    exit()

# --- 2. SQL Generation and Execution Evaluation ---

logging.info("--- Starting SQL Evaluation ---")

results = []
db_schema = db.get_table_info()

for item in golden_dataset_data:
    question = item['question']
    golden_sql = item['golden_sql']
    
    # --- Agent Simulation ---
    # 1. Generate SQL
    generated_sql_raw = generate_sql_query(question, db_schema)
    
    # 2. Validate SQL
    validation_result = validate_and_correct_sql(generated_sql_raw, db_schema)
    if validation_result.get("valid"):
        generated_sql = generated_sql_raw
    else:
        generated_sql = validation_result.get("corrected_query", generated_sql_raw)

    # --- Comparison ---
    exact_match = (generated_sql == golden_sql)
    
    # --- Execution Accuracy ---
    try:
        # Execute generated SQL
        generated_result = execute_sql_query(generated_sql)
        if "error" in generated_result:
            raise Exception(generated_result["error"])
        generated_result_df = generated_result["sql_dataframe"]

        # Execute golden SQL
        golden_result = execute_sql_query(golden_sql)
        if "error" in golden_result:
            raise Exception(f"Error in golden SQL: {golden_result['error']}")
        golden_result_df = golden_result["sql_dataframe"]
        
        # Compare results
        execution_accuracy = generated_result_df.equals(golden_result_df)

    except Exception as e:
        logging.error(f"Error executing SQL for question: '{question}'. Error: {e}")
        execution_accuracy = False

    results.append({
        'question': question,
        'golden_sql': golden_sql,
        'generated_sql': generated_sql,
        'exact_match': exact_match,
        'execution_accuracy': execution_accuracy
    })

# --- Print SQL Evaluation Report ---
sql_eval_df = pd.DataFrame(results)
print("\n--- SQL Generation Evaluation Report ---")
print(sql_eval_df.to_string())

exact_match_rate = sql_eval_df['exact_match'].mean()
execution_accuracy_rate = sql_eval_df['execution_accuracy'].mean()

print(f"\nExact Match Rate: {exact_match_rate:.2f}")
print(f"Execution Accuracy Rate: {execution_accuracy_rate:.2f}")


# --- 3. Insight Evaluation with RAGAS ---

logging.info("--- Starting Insight Evaluation with RAGAS ---")

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        answer_correctness,
    )
    from llm_config import get_llm

    # Configure the LLM for RAGAS - replace with your desired model
    ragas_llm = get_llm(model_name="gemini-1.5-flash", temperature=0)


    # --- Generate Agent Outputs ---
    evaluation_data = []
    for item in golden_dataset_data:
        question = item['question']
        ground_truth = item['ground_truth_answer']
        
        # Simulate running the agent to get the context (dataframe) and answer (insight)
        sql_query = generate_sql_query(question, db_schema)
        validation_result = validate_and_correct_sql(sql_query, db_schema)
        validated_sql = validation_result.get("corrected_query", sql_query) if not validation_result.get("valid") else sql_query

        result = execute_sql_query(validated_sql)
        if "error" in result:
            logging.warning(f"Skipping RAGAS for question '{question}' due to SQL execution error.")
            continue
            
        context_df = result["sql_dataframe"]
        answer = generate_insight_from_data(question, context_df)
        
        evaluation_data.append({
            'question': question,
            'answer': answer,
            'contexts': [context_df.to_string()], # RAGAS expects contexts as a list of strings
            'ground_truth': ground_truth
        })

    if evaluation_data:
        # --- Create Hugging Face Dataset for RAGAS ---
        ragas_dataset = Dataset.from_list(evaluation_data)

        # --- Run RAGAS Evaluation ---
        result = evaluate(
            ragas_dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                answer_correctness,
            ],
            llm=ragas_llm,
        )

        # --- Print RAGAS Evaluation Report ---
        ragas_df = result.to_pandas()
        print("\n--- RAGAS Insight Evaluation Report ---")
        print(ragas_df.to_string())
    else:
        print("\nNo data to evaluate with RAGAS.")

except ImportError:
    logging.warning("RAGAS not installed. Skipping insight evaluation.")
    print("\nPlease install RAGAS to run the insight evaluation: pip install ragas")
except Exception as e:
    logging.error(f"An error occurred during RAGAS evaluation: {e}")