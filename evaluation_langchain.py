
import pandas as pd
import logging
from langsmith import Client
from langsmith.evaluation import run_on_dataset, EvaluationResult
from langsmith.schemas import Example, Run

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Import actual agent components ---
from main_agent import db
from tools import generate_sql_query, execute_sql_query, generate_insight_from_data, validate_and_correct_sql

# --- 1. Initialize LangSmith Client ---
client = Client()
DATASET_NAME = "FloodGPT Golden Dataset"

# --- 2. Load Golden Dataset and Upload to LangSmith ---
logging.info(f"Loading golden dataset from golden_dataset.csv")
try:
    golden_df = pd.read_csv("golden_dataset.csv")
except FileNotFoundError:
    logging.error("golden_dataset.csv not found. Please create it first.")
    exit()

# Check if dataset already exists
try:
    dataset = client.read_dataset(dataset_name=DATASET_NAME)
    logging.info(f"Found existing dataset '{DATASET_NAME}' in LangSmith.")
except Exception:
    logging.info(f"Dataset '{DATASET_NAME}' not found. Creating a new one.")
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Golden dataset for evaluating the FloodGPT Text-to-SQL agent.",
    )
    # Create examples from the dataframe
    examples = [
        Example(
            inputs={"question": row["question"]},
            outputs={"golden_sql": row["golden_sql"], "ground_truth_answer": row["ground_truth_answer"]}
        )
        for _, row in golden_df.iterrows()
    ]
    client.create_examples(inputs=[e.inputs for e in examples], outputs=[e.outputs for e in examples], dataset_id=dataset.id)
    logging.info(f"Successfully created dataset '{DATASET_NAME}' with {len(examples)} examples.")

# --- 3. Define the Agent Logic to be Tested ---
# This function wraps the core logic of your agent.
def agent_pipeline(inputs: dict):
    question = inputs["question"]
    db_schema = db.get_table_info()

    # 1. Generate and Validate SQL
    generated_sql_raw = generate_sql_query(question, db_schema)
    validation_result = validate_and_correct_sql(generated_sql_raw, db_schema)
    validated_sql = validation_result.get("corrected_query", generated_sql_raw) if not validation_result.get("valid") else generated_sql_raw

    # 2. Execute SQL
    execution_result = execute_sql_query(validated_sql)
    if "error" in execution_result:
        return {"error": execution_result["error"], "generated_sql": validated_sql}
    
    sql_dataframe = execution_result["sql_dataframe"]

    # 3. Generate Insight
    insight = generate_insight_from_data(question, sql_dataframe)

    return {
        "generated_sql": validated_sql,
        "sql_dataframe_str": sql_dataframe.to_string(), # Return string for logging
        "insight": insight
    }

# --- 4. Define Custom Evaluators ---

def sql_execution_accuracy_evaluator(run: Run, example: Example) -> EvaluationResult:
    """
    A custom evaluator to check if the generated SQL produces the exact same
    result as the golden SQL.
    """
    try:
        # Get the generated SQL from the agent's output
        generated_sql = run.outputs.get("generated_sql")
        if not generated_sql:
            return EvaluationResult(key="execution_accuracy", score=0, comment="Generated SQL not found in outputs.")

        # Get the golden SQL from the dataset example
        golden_sql = example.outputs["golden_sql"]

        # Execute both queries
        generated_result = execute_sql_query(generated_sql)["sql_dataframe"]
        golden_result = execute_sql_query(golden_sql)["sql_dataframe"]

        # Compare the results
        score = 1 if generated_result.equals(golden_result) else 0
        comment = f"Execution accuracy: {score}. Generated SQL and Golden SQL results match." if score == 1 else f"Execution accuracy: {score}. Results mismatch."

    except Exception as e:
        score = 0
        comment = f"Error during evaluation: {str(e)}"

    return EvaluationResult(key="execution_accuracy", score=score, comment=comment)

# --- 5. Run the Evaluation on LangSmith ---

logging.info(f"Starting evaluation run on dataset '{DATASET_NAME}'.")

# Note: LangSmith also has built-in AI evaluators. 
# You can add them here, e.g., using `from langsmith.evaluation.evaluators import LabeledScoreStringEvalChain`
# For simplicity, we are focusing on the custom SQL evaluator first.

experiment_results = run_on_dataset(
    client=client,
    dataset_name=DATASET_NAME,
    llm_or_chain_factory=agent_pipeline,
    evaluation={
        "custom_evaluators": [sql_execution_accuracy_evaluator],
    },
    project_name=f"FloodGPT Eval - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
)

logging.info("Evaluation complete. Results are available in your LangSmith project.")
logging.info(f"Project URL: {experiment_results['project_url']}")
