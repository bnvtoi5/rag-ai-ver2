import os
import streamlit as st
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# THÊM ĐOẠN NÀY: Tự động cấu hình Token Hugging Face từ .env nếu có
# Hoặc điền trực tiếp mã token vào đây nếu không dùng file .env: os.environ["HF_TOKEN"] = "hf_xxx"
if os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# THÊM ĐOẠN NÀY: Ép Hugging Face ưu tiên đọc mô hình từ ổ đĩa local sau lần tải đầu tiên, 
# tránh gửi quá nhiều request lên Hub dẫn đến bị chặn IP / Timeout khi nạp file hàng loạt.
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1" 

class Config:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHROMA_DIR = "./chroma_db"
    RAW_DATA_DIR = "./data/raw"
    
    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("LỖI: Chưa cấu hình GROQ_API_KEY trong file .env!")
