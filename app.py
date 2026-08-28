import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from utils.ai import AIAnalyticsError, ask_ai, generate_chart_config
from utils.analytics import (
    get_category_columns,
    get_column_info,
    get_numeric_columns,
    perform_group_analysis,
)
from utils.data_loader import SAMPLE_DATASETS, load_csv, load_sample_csv
from utils.local_analysis import answer_locally
from utils.quality import calculate_health_score, generate_data_quality_report
from utils.visualization import (
    create_ai_chart,
    create_basic_chart,
    create_correlation_chart,
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Analytics Assistant")
st.write("Upload a CSV file, explore the data, and ask questions in local or AI mode.")

client = OpenAI(api_key=api_key, max_retries=2, timeout=30.0) if api_key else None
if client is None:
    st.info(
        "Running in local analytics mode. Add OPENAI_API_KEY to .env to enable "
        "AI-generated charts and open-ended analysis."
    )

data_source = st.radio(
    "Choose a data source",
    ["Try a sample dataset", "Upload a CSV"],
    horizontal=True,
)
selected_sample = None
uploaded_file = None
if data_source == "Try a sample dataset":
    selected_sample = st.selectbox("Sample dataset", list(SAMPLE_DATASETS))
    st.caption("Sample data is synthetic and safe to explore locally or in a public demo.")
else:
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if selected_sample is not None or uploaded_file is not None:
    try:
        df = (
            load_sample_csv(selected_sample)
            if selected_sample is not None
            else load_csv(uploaded_file)
        )

        st.success(
            f"Loaded sample: {selected_sample}"
            if selected_sample is not None
            else "File uploaded successfully!"
        )

        numeric_columns = get_numeric_columns(df)
        category_columns = get_category_columns(df)

        st.subheader("Dataset Preview")
        st.dataframe(df.head(20), width="stretch")

        st.subheader("Dataset Health Score")

        health_score, health_details = calculate_health_score(df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Health Score", f"{health_score}/100")

        with col2:
            st.metric("Missing %", f"{health_details['missing_percentage']}%")

        with col3:
            st.metric("Duplicate Rows", health_details["duplicate_rows"])

        with col4:
            st.metric("Empty Columns", len(health_details["empty_columns"]))

        if health_score >= 85:
            st.success("Dataset looks healthy overall.")
        elif health_score >= 60:
            st.warning("Dataset is usable but has some quality issues.")
        else:
            st.error("Dataset has significant quality issues and should be cleaned.")

        st.subheader("Basic Dataset Information")

        info_col1, info_col2, info_col3, info_col4 = st.columns(4)

        with info_col1:
            st.metric("Rows", df.shape[0])

        with info_col2:
            st.metric("Columns", df.shape[1])

        with info_col3:
            st.metric("Missing Values", int(df.isnull().sum().sum()))

        with info_col4:
            st.metric("Duplicate Rows", int(df.duplicated().sum()))

        st.subheader("Column Information")
        column_info = get_column_info(df)
        st.dataframe(column_info, width="stretch")

        st.subheader("Data Quality Recommendations")
        quality_report = generate_data_quality_report(df)

        for item in quality_report:
            if "No major" in item:
                st.success(item)
            else:
                st.warning(item)

        st.subheader("Descriptive Statistics")

        if numeric_columns:
            st.dataframe(df[numeric_columns].describe(), width="stretch")
        else:
            st.info("No numeric columns found for descriptive statistics.")

        st.subheader("Quick Analysis")

        if numeric_columns and category_columns:
            selected_category = st.selectbox("Group by category", category_columns)

            selected_metric = st.selectbox("Select metric", numeric_columns)

            aggregation = st.selectbox(
                "Select aggregation",
                ["sum", "average", "count", "min", "max"],
            )

            result = perform_group_analysis(
                df=df,
                category_col=selected_category,
                metric_col=selected_metric,
                aggregation=aggregation,
            )

            st.dataframe(result, width="stretch")

            st.bar_chart(result.set_index(selected_category))

            csv_data = result.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Analysis Result as CSV",
                data=csv_data,
                file_name="analysis_result.csv",
                mime="text/csv",
            )

        else:
            st.info("Need at least one text column and one numeric column for quick analysis.")

        st.subheader("Charts")

        if numeric_columns:
            chart_type = st.selectbox(
                "Select chart type",
                ["Bar Chart", "Line Chart", "Histogram"],
            )

            selected_column = st.selectbox(
                "Select numeric column",
                numeric_columns,
                key="chart_column",
            )

            fig = create_basic_chart(df, chart_type, selected_column)
            st.pyplot(fig)

        else:
            st.info("No numeric columns available for charts.")

        st.subheader("Correlation Analysis")

        if len(numeric_columns) >= 2:
            correlation = df[numeric_columns].corr()

            st.dataframe(correlation, width="stretch")

            fig = create_correlation_chart(correlation)
            st.pyplot(fig)

        else:
            st.info("Need at least two numeric columns for correlation analysis.")

        st.subheader("AI-Powered Chart Generator")

        st.info(
            """
            Example chart requests:

            - Show revenue by campaign
            - Plot clicks by channel
            - Create a histogram of spend
            - Show impressions by campaign
            """
        )

        chart_question = st.text_input(
            "Ask AI to create a chart",
            placeholder="Example: Show revenue by campaign",
            disabled=client is None,
        )

        if st.button("Generate AI Chart", disabled=client is None):
            if not chart_question:
                st.warning("Please enter a chart request.")
            else:
                with st.spinner("Generating chart..."):
                    try:
                        chart_config = generate_chart_config(chart_question, df, client)
                        fig, error = create_ai_chart(chart_config, df)
                        if error:
                            st.error(error)
                            st.json(chart_config)
                        else:
                            st.pyplot(fig)
                            st.write("Chart configuration used:")
                            st.json(chart_config)
                    except AIAnalyticsError as error:
                        st.error(str(error))

        if client is None:
            st.caption("Set OPENAI_API_KEY to enable AI-generated chart configuration.")

        st.subheader("Ask About Your Data")

        st.info(
            """
            Local mode supports questions such as:

            - Summarize this dataset.
            - What data quality issues are there?
            - What is the total revenue?
            - Show top campaign by revenue.
            - Show the strongest correlation.

            With an API key, open-ended AI analysis is also available.
            """
        )

        question = st.chat_input("Ask a question about your dataset")

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"), st.spinner("Analyzing your data..."):
                try:
                    answer = (
                        ask_ai(question, df, client)
                        if client is not None
                        else answer_locally(question, df)
                    )
                    st.markdown(answer)
                except AIAnalyticsError as error:
                    st.error(str(error))

    except Exception as error:  # noqa: BLE001 - UI boundary must remain recoverable
        st.error(f"Something went wrong: {error}")

else:
    st.info("Upload a CSV file to get started.")
