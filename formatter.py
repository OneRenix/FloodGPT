import logging
import pandas as pd
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class DataFormatter:
    """
    A class to format a Pandas DataFrame into structured JSON for various chart types.
    """
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initializes the formatter with a LangChain LLM instance.
        """
        self.llm = llm

    def _get_chart_options(self, question: str, columns: list) -> dict:
        """Uses the LLM to generate a professional title for the chart."""
        try:
            prompt = ChatPromptTemplate.from_template(
                "Based on the user's question '{q}' and the data columns '{cols}', "
                "suggest a concise and professional chart 'title'. "
                "Respond with a valid JSON object containing only the 'title' key."
            )
            chain = prompt | self.llm
            options_str = chain.invoke({"q": question, "cols": columns}).content
            # Clean up potential markdown formatting from the LLM
            clean_options_str = options_str.strip().replace('`json', '').replace('`', '')
            return json.loads(clean_options_str)
        except Exception as e:
            logging.warning(f"Could not generate LLM chart options, falling back to default. Error: {e}")
            return {"title": question}

    def _format_bar_data(self, df: pd.DataFrame, question: str, chart_type: str) -> dict:
        """Formats DataFrame for bar or horizontal_bar charts."""
        label_cols = df.select_dtypes(include=['object', 'category']).columns
        data_cols = df.select_dtypes(include=['number']).columns

        if not label_cols.any() or not data_cols.any():
            raise ValueError("Bar chart data must have at least one text/object column and one numeric column.")

        labels = df[label_cols[0]].astype(str).tolist()
        values = [{"data": df[col].tolist(), "label": str(col)} for col in data_cols]
        
        return {
            "type": chart_type,
            "data": {"labels": labels, "values": values},
            "options": self._get_chart_options(question, df.columns.tolist())
        }

    def _format_line_data(self, df: pd.DataFrame, question: str) -> dict:
        """Formats DataFrame for line charts."""
        x_col = df.columns[0]
        y_cols = df.select_dtypes(include=['number']).columns
        if not y_cols.any():
            raise ValueError("Line chart data must have at least one numeric y-axis column.")
        
        labels = df[x_col].astype(str).tolist()
        values = [{"data": df[col].tolist(), "label": str(col)} for col in y_cols]

        return {
            "type": "line",
            "data": {"labels": labels, "values": values},
            "options": self._get_chart_options(question, df.columns.tolist())
        }
        
    def _format_pie_data(self, df: pd.DataFrame, question: str) -> dict:
        """Formats DataFrame for pie charts."""
        label_cols = df.select_dtypes(include=['object', 'category']).columns
        data_cols = df.select_dtypes(include=['number']).columns
        if not label_cols.any() or len(data_cols) != 1:
            raise ValueError("Pie chart data must have exactly one text/object column and one numeric column.")
        labels_col, data_col = label_cols[0], data_cols[0]
        labels = df[labels_col].astype(str).tolist()
        values = [{"data": df[data_col].tolist(), "label": data_col}]
        return {
            "type": "pie",
            "data": {"labels": labels, "values": values},
            "options": self._get_chart_options(question, df.columns.tolist())
        }

    def _format_scatter_data(self, df: pd.DataFrame, question: str) -> dict:
        """Formats DataFrame for scatter plots."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) < 2:
            raise ValueError("Scatter plot data must have at least two numeric columns.")
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        
        labels = df[x_col].astype(str).tolist()
        values = [{
            "label": f"{x_col} vs {y_col}",
            "data": df[[x_col, y_col]].to_dict('records')
        }]

        return {
            "type": "scatter",
            "data": {"labels": labels, "values": values},
            "options": self._get_chart_options(question, df.columns.tolist())
        }

    def format_data_for_visualization(self, state: dict) -> dict:
        """
        Main method to format a DataFrame for the chosen visualization type.
        This is the primary entry point to be called by the LangGraph node.
        """
        chart_type = state.get('visualization', 'none')
        df = state.get('sql_dataframe')
        question = state.get('question', '')

        if chart_type == "none" or df is None or df.empty:
            return {"error": "No data available to format."}

        try:
            # Convert NumPy types to standard Python types for JSON serialization
            for col in df.select_dtypes(include=['int64', 'int32']).columns:
                df[col] = df[col].astype(int)
            for col in df.select_dtypes(include=['float64', 'float32']).columns:
                df[col] = df[col].astype(float)
            
            # Route to the correct formatting function
            if chart_type in ["bar", "horizontal_bar"]:
                formatted_data = self._format_bar_data(df, question, chart_type)
            elif chart_type == "line":
                formatted_data = self._format_line_data(df, question)
            elif chart_type == "pie":
                formatted_data = self._format_pie_data(df, question)
            elif chart_type == "scatter":
                formatted_data = self._format_scatter_data(df, question)
            else:
                raise ValueError(f"Unknown or unhandled chart type: {chart_type}")
            
            return formatted_data
            
        except Exception as e:
            logging.error(f"Failed to format data due to error: {e}")
            return {"error": f"Failed to format data. Details: {str(e)}"}