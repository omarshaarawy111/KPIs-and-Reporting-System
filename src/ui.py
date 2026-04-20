# Style functions
import streamlit as st

def small_header(text):
    st.markdown(f"<h3 style='text-align: center;'>{text}</h5>", unsafe_allow_html=True)

def centered_metric(label, value):
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; align-items: center; font-size: 24px;font-weight:bold'>
        <div>{value}</div>
        </div>
        """, unsafe_allow_html=True
    )

def sidebar_style():
    st.markdown(
        """
        <style>
            .st-emotion-cache-16txtl3 {
                padding: 3.0rem 1.5rem !important;
                }
        </style>
        """, unsafe_allow_html=True)