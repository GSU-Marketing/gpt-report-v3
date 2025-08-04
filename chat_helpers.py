import streamlit as st
import pandas as pd
from openai import OpenAI
import tiktoken

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

@st.cache_data(show_spinner="🤖 Asking GPT...", show_time=True)
def ask_gpt(prompt: str, system_prompt: str, temperature: float = 0.4):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        st.warning("⚠️ GPT error: API limit reached or input too large.")
        st.info("ℹ️ Details have been logged.")
        return None

def summarize_funnel_metrics(df):
    stages = ["Inquiry", "Applicant", "Enrolled"]
    counts = {stage: len(df[df["Person Status"] == stage]) for stage in stages}
    return "\n".join([f"{stage}: {count}" for stage, count in counts.items()])

def get_compressed_csv(df: pd.DataFrame, important_cols=None, max_tokens=8000):
    if important_cols is None:
        important_cols = ["Person Status", "Applications Applied Program", "Applications Applied Term", "Ping Timestamp"]
    df_small = df[important_cols].copy()
    encoder = tiktoken.encoding_for_model("gpt-4")

    for n in range(300, 10, -10):
        csv = df_small.head(n).to_csv(index=False)
        tokens = len(encoder.encode(csv))
        if tokens < max_tokens:
            return csv
    return df_small.head(10).to_csv(index=False)
