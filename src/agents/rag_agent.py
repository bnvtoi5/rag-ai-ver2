import os
from langchain_groq import ChatGroq
from src.config import Config
from src.database.chroma_client import get_vector_store

def rag_node(state):
    user_msg = state["messages"][-1]["content"]
    vector_store = get_vector_store()
    
    # 1. Đặt mức k=5 là vừa đủ ngữ cảnh cho máy RAM 8GB và tránh lỗi Rate Limit
    docs = vector_store.similarity_search(user_msg, k=5)
    
    # 2. Định dạng lại Context theo cấu trúc nghiêm ngặt để triệt tiêu ảo giác số trang
    context_chunks = []
    for i, d in enumerate(docs):
        file_name = os.path.basename(d.metadata.get("source", "Không rõ file"))
        location = d.metadata.get("location", "Không rõ vị trí")
        
        # Tách biệt hoàn toàn Tên file, Vị trí bắt buộc trích dẫn và Nội dung text
        chunk_content = (
            f"=== ĐOẠN TÀI LIỆU SỐ {i+1} ===\n"
            f"[TÊN TÀI LIỆU]: {file_name}\n"
            f"[THÔNG TIN VỊ TRÍ GỐC]: {location}\n"
            f"[NỘI DUNG VĂN BẢN]:\n{d.page_content}\n"
            f"============================="
        )
        context_chunks.append(chunk_content)
        
    formatted_context = "\n\n".join(context_chunks)
    
    # 3. Đọc dữ liệu từ file prompt txt bên ngoài
    prompt_path = os.path.join("src", "prompts", "rag_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
        
    system_prompt = raw_prompt.format(context=formatted_context, user_msg=user_msg)
    
    # 4. Gọi LLM xử lý với độ sáng tạo bằng 0 để đảm bảo tính kỷ luật thông tin
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=Config.GROQ_API_KEY, temperature=0)
    response = llm.invoke(system_prompt).content
            
    return {"final_answer": response, "next_step": "END"}