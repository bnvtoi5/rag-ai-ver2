import streamlit as sn # Đổi tên alias tùy ý hoặc dùng import streamlit as st
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import Config

@st.cache_resource
def get_embedding_model():
    """Tải và lưu cache mô hình embedding để tránh tải lại nhiều lần làm tràn RAM"""
    print("⏳ Đang khởi tạo mô hình Embedding (Chỉ chạy 1 lần duy nhất)...")
    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )
