import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Analytics Assistant")
st.write("Upload a CSV file, explore the data, and ask AI-powered questions.")

if not api_key:
    st.error("OPENAI_API_KEY is missing. Please add it to your .env file.")
    st.stop()
st.subheader("AI-Powered Chart Generator")

chart_question = st.text_input(
    "Ask AI to create a chart",
    placeholder="Example: Show revenue by campaign"
)

if st.button("Generate AI Chart"):
    if chart_question:
        with st.spinner("Generating chart..."):
            chart_config = generate_ai_chart(chart_question, df)

            if chart_config is None:
                st.error("Could not understand the chart request. Try again with clear column names.")
            else:
                chart_type = chart_config.get("chart_type")
                x_axis = chart_config.get("x_axis")
                y_axis = chart_config.get("y_axis")

                if x_axis not in df.columns:
                    st.error(f"Invalid x-axis column: {x_axis}")
                elif y_axis is not None and y_axis not in df.columns:
                    st.error(f"Invalid y-axis column: {y_axis}")
                else:
                    fig, ax = plt.subplots()

                    if chart_type == "bar":
                        chart_data = (
                            df.groupby(x_axis)[y_axis]
                            .sum()
                            .sort_values(ascending=False)
                            .head(10)
                        )
                        chart_data.plot(kind="bar", ax=ax)
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel(y_axis)
                        ax.set_title(f"{y_axis} by {x_axis}")

                    elif chart_type == "line":
                        df.plot(x=x_axis, y=y_axis, kind="line", ax=ax)
                        ax.set_xlabel(x_axis)
                        ax.set_ylabel(y_axis)
                        ax.set_title(f"{y_axis} over {x_axis}")

                    elif chart_type == "histogram":
                        df[x_axis].plot(kind="hist", ax=ax)
                        ax.set_xlabel(x_axis)
                        ax.set_title(f"Distribution of {x_axis}")

                    else:
                        st.error("Unsupported chart type.")
                        st.stop()

                    st.pyplot(fig)

                    st.write("Chart configuration used:")
                    st.json(chart_config)
    else:
        st.warning("Please enter a chart request.")
client = OpenAI(api_key=api_key)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])


def get_dataframe_summary(df: pd.DataFrame) -> str:
    summary = f"""
Dataset Summary:
Rows: {df.shape[0]}
Columns: {df.shape[1]}

Column Names:
{list(df.columns)}



Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}

First 5 Rows:
{df.head().to_string()}
"""
    return summary


def answer_with_pandas(question: str, df: pd.DataFrame):
    question_lower = question.lower()

    numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    category_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not numeric_columns:
        return None

    # Find metric column mentioned in question
    selected_metric = None
    for col in numeric_columns:
        if col.lower() in question_lower:
            selected_metric = col
            break

    # If no metric is mentioned, use first numeric column
    if selected_metric is None:
        selected_metric = numeric_columns[0]

    # Find category column mentioned in question
    selected_category = None
    for col in category_columns:
        if col.lower() in question_lower:
            selected_category = col
            break

    # Top / highest analysis
    if any(word in question_lower for word in ["highest", "top", "most", "largest"]):
        if selected_category:
            result = (
                df.groupby(selected_category)[selected_metric]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            return result

        result = df[selected_metric].sort_values(ascending=False).head(10).reset_index()
        return result

    # Average analysis
    if "average" in question_lower or "mean" in question_lower:
        if selected_category:
            result = (
                df.groupby(selected_category)[selected_metric]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            return result

        return pd.DataFrame({
            "Metric": [selected_metric],
            "Average": [df[selected_metric].mean()]
        })

    # Sum / total analysis
    if "total" in question_lower or "sum" in question_lower:
        if selected_category:
            result = (
                df.groupby(selected_category)[selected_metric]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            return result

        return pd.DataFrame({
            "Metric": [selected_metric],
            "Total": [df[selected_metric].sum()]
        })

    return None
def generate_ai_chart(question: str, df: pd.DataFrame):
    columns = list(df.columns)

    prompt = f"""
You are a data visualization assistant.

The user wants to create a chart from a dataset.

Available columns:
{columns}

User request:
{question}

Return ONLY valid JSON in this format:

{{
  "chart_type": "bar",
  "x_axis": "column_name",
  "y_axis": "column_name"
}}

Rules:
- chart_type must be one of: bar, line, histogram
- Use only column names from the dataset.
- For histogram, x_axis should be a numeric column and y_axis should be null.
- Do not include explanation.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        chart_config = json.loads(response.output_text)
        return chart_config
    except json.JSONDecodeError:
        return None

def generate_data_quality_report(df: pd.DataFrame):
    recommendations = []

    # Missing values
    missing = df.isnull().sum()

    for col, count in missing.items():
        if count > 0:
            recommendations.append(
                f"'{col}' has {count} missing values."
            )

    # Duplicate rows
    duplicates = df.duplicated().sum()

    if duplicates > 0:
        recommendations.append(
            f"The dataset contains {duplicates} duplicate rows."
        )

    # Numeric columns
    numeric_columns = df.select_dtypes(include="number").columns

    for col in numeric_columns:

        if (df[col] < 0).any():
            recommendations.append(
                f"'{col}' contains negative values."
            )

    # Object columns
    object_columns = df.select_dtypes(include="object").columns

    for col in object_columns:

        unique = df[col].nunique()

        if unique > len(df) * 0.8:
            recommendations.append(
                f"'{col}' has very high cardinality."
            )

        try:
            pd.to_datetime(df[col])
            recommendations.append(
                f"'{col}' appears to be a date column."
            )
        except:
            pass

    if len(recommendations) == 0:
        recommendations.append(
            "No major data quality issues detected."
        )

    return recommendations

def generate_chart_config(question: str, df: pd.DataFrame):
    columns = list(df.columns)

    prompt = f"""
You are a data visualization assistant.

Available dataset columns:
{columns}

User request:
{question}

Return ONLY valid JSON in this exact format:

{{
  "chart_type": "bar",
  "x_axis": "column_name",
  "y_axis": "column_name",
  "aggregation": "sum"
}}

Rules:
- chart_type must be one of: bar, line, histogram
- aggregation must be one of: sum, average, count, none
- Use only columns from the available dataset columns.
- For histogram, y_axis must be null and aggregation must be none.
- Do not include markdown.
- Do not include explanation.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError:
        return None
    
def ask_ai(question: str, df: pd.DataFrame) -> str:
    summary = get_dataframe_summary(df)

    prompt = f"""
You are an expert data analyst.

Use the dataset summary below to answer the user's question.
Be clear, practical, and concise.

Important:
- You only have access to the dataset summary and first 5 rows.
- Do not claim you calculated totals unless the value is visible in the summary.
- If the question requires full-dataset calculation, say Pandas analysis is needed.

{summary}

User question:
{question}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.error("The uploaded CSV file is empty.")
            st.stop()

        st.success("File uploaded successfully!")

        numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        category_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

        st.subheader("Dataset Preview")
        st.dataframe(df.head(20), use_container_width=True)

        st.subheader("Basic Dataset Information")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Rows", df.shape[0])

        with col2:
            st.metric("Columns", df.shape[1])

        with col3:
            st.metric("Missing Values", int(df.isnull().sum().sum()))

        with col4:
            st.metric("Duplicate Rows", int(df.duplicated().sum()))

        st.subheader("Column Information")

        column_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isnull().sum().values,
            "Missing %": (df.isnull().mean() * 100).round(2).values
        })



        st.dataframe(column_info, use_container_width=True)
        st.subheader("Data Quality Recommendations")

        quality_report = generate_data_quality_report(df)

        for item in quality_report:
            if "No major" in item:
                st.success(item)
            else:
                st.warning(item)

            st.subheader("Descriptive Statistics")

        if numeric_columns:
            st.dataframe(df[numeric_columns].describe(), use_container_width=True)
        else:
            st.info("No numeric columns found for descriptive statistics.")

        st.subheader("Quick Analysis")

        if numeric_columns and category_columns:
            selected_category = st.selectbox(
                "Group by category",
                category_columns
            )

            selected_metric = st.selectbox(
                "Select metric",
                numeric_columns
            )

            aggregation = st.selectbox(
                "Select aggregation",
                ["sum", "average", "count", "min", "max"]
            )

            if aggregation == "sum":
                result = df.groupby(selected_category)[selected_metric].sum()
            elif aggregation == "average":
                result = df.groupby(selected_category)[selected_metric].mean()
            elif aggregation == "count":
                result = df.groupby(selected_category)[selected_metric].count()
            elif aggregation == "min":
                result = df.groupby(selected_category)[selected_metric].min()
            else:
                result = df.groupby(selected_category)[selected_metric].max()

            result = result.sort_values(ascending=False).reset_index()

            st.dataframe(result, use_container_width=True)

            st.bar_chart(result.set_index(selected_category))

            csv_data = result.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Analysis Result as CSV",
                data=csv_data,
                file_name="analysis_result.csv",
                mime="text/csv"
            )

        else:
            st.info("Need at least one text column and one numeric column for quick analysis.")

        st.subheader("Charts")

        if numeric_columns:
            chart_type = st.selectbox(
                "Select chart type",
                ["Bar Chart", "Line Chart", "Histogram"]
            )

            selected_column = st.selectbox(
                "Select numeric column",
                numeric_columns,
                key="chart_column"
            )

            fig, ax = plt.subplots()

            if chart_type == "Bar Chart":
                df[selected_column].plot(kind="bar", ax=ax)
                ax.set_xlabel("Row Number")
                ax.set_ylabel(selected_column)

            elif chart_type == "Line Chart":
                df[selected_column].plot(kind="line", ax=ax)
                ax.set_xlabel("Row Number")
                ax.set_ylabel(selected_column)

            elif chart_type == "Histogram":
                df[selected_column].plot(kind="hist", ax=ax)
                ax.set_xlabel(selected_column)

            ax.set_title(f"{chart_type} of {selected_column}")
            st.pyplot(fig)

        else:
            st.info("No numeric columns available for charts.")

        st.subheader("Correlation Analysis")

        if len(numeric_columns) >= 2:
            correlation = df[numeric_columns].corr()

            st.dataframe(correlation, use_container_width=True)

            fig, ax = plt.subplots()
            cax = ax.matshow(correlation)
            fig.colorbar(cax)

            ax.set_xticks(range(len(correlation.columns)))
            ax.set_yticks(range(len(correlation.columns)))
            ax.set_xticklabels(correlation.columns, rotation=90)
            ax.set_yticklabels(correlation.columns)

            st.pyplot(fig)

        else:
            st.info("Need at least two numeric columns for correlation analysis.")

        st.subheader("Ask AI About Your Data")

        question = st.chat_input("Example: What cleaning steps would you recommend?")

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing your data..."):

                    pandas_result = answer_with_pandas(question, df)

                    if pandas_result is not None:
                        st.write("Here is the calculated result from your dataset:")
                        st.dataframe(pandas_result, use_container_width=True)

                        if len(pandas_result.columns) >= 2:
                            st.bar_chart(pandas_result.set_index(pandas_result.columns[0]))

                        explanation_prompt = f"""
        You are a senior data analyst.

        The user asked:
        {question}

        The app calculated this result using Pandas:
        {pandas_result.to_string(index=False)}

        Explain the result clearly and briefly for a business user.
        Mention that the result is based on the uploaded dataset.
        """

                        response = client.responses.create(
                            model="gpt-4.1-mini",
                            input=explanation_prompt
                        )

                        st.markdown(response.output_text)

                    else:
                        answer = ask_ai(question, df)
                        st.markdown(answer)

    except Exception as e:
        st.error(f"Something went wrong while reading the file: {e}")

else:
    st.info("Upload a CSV file to get started.")
