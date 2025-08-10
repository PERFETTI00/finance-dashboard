import streamlit as st

def inject_css(primary="#7c3aed"):
    st.markdown(
        f'''
        <style>
        .metric-card {{
            background: rgba(124, 58, 237, 0.08);
            border: 1px solid rgba(124, 58, 237, 0.25);
            border-radius: 16px;
            padding: 18px;
        }}
        .metric-title {{ font-size: 0.85rem; color: #a3a3a3; margin-bottom: 6px; letter-spacing: .02em; }}
        .metric-value {{ font-size: 1.4rem; font-weight: 700; color: #fff; }}
        .pill {{
            padding: 4px 10px; border-radius: 999px;
            border: 1px solid rgba(124,58,237,.35);
            background: rgba(124,58,237,.12); font-size: 0.8rem;
        }}
        a, .st-c a {{ color: {primary} !important; }}
        </style>
        ''', unsafe_allow_html=True,
    )

def metric_card(title: str, value: str):
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
    ''', unsafe_allow_html=True)