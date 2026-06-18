from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def split_docs(documents: List, chunk_size: int = 1200, chunk_overlap: int = 150) -> List:
    """
    Hàm băm nhỏ tài liệu nâng cấp:
    Sử dụng bản đồ hóa ký tự (Character Map) cho file TXT và phân tách trang độc lập cho PDF,
    loại bỏ hoàn toàn lỗi lệch dòng hoặc lệch trang cá biệt ở vùng ranh giới.
    """
    # Cấu hình bộ băm: add_start_index=True bắt buộc để ghim vị trí ký tự gốc của chunk (cho TXT)
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True 
    )
    
    final_chunks = []
    
    for doc in documents:
        # Trường hợp 1: Nếu là file PDF (Tính toán chính xác theo từng trang độc lập)
        if doc.metadata.get("is_pdf", False):
            # Bộ băm dữ liệu sẽ băm nhỏ dựa trên text của CHÍNH TRANG ĐÓ
            chunks = text_splitter.split_documents([doc])
            for chunk in chunks:
                # Lấy trực tiếp số trang đã được loaders.py định danh chuẩn (1-based index)
                page_num = chunk.metadata.get("page", 1) 
                chunk.metadata["location"] = f"Vị trí: Trang {page_num}"
                final_chunks.append(chunk)
            continue
            
        # Trường hợp 2: Nếu là file TXT (Tính toán khoảng dòng chính xác tuyệt đối)
        orig_text = doc.page_content
        lines = orig_text.split('\n')
        
        # Tạo bản đồ dòng: ghi nhận vị trí ký tự đầu và kết thúc của từng dòng trong văn bản gốc
        line_map = []
        current_idx = 0
        for i, line in enumerate(lines):
            start_idx = current_idx
            end_idx = current_idx + len(line)
            line_map.append((start_idx, end_idx, i + 1))  # Dòng hiển thị bắt đầu từ 1
            current_idx = end_idx + 1  # Cộng 1 để tính ký tự xuống dòng '\n'
            
        # Tiến hành băm tài liệu gốc thành các chunk bằng thư viện
        chunks = text_splitter.split_documents([doc])
        
        for chunk in chunks:
            # Lấy vị trí ký tự bắt đầu thực tế của chunk trong tài liệu gốc
            chunk_start_char = chunk.metadata.get("start_index", 0)
            # Tính vị trí ký tự kết thúc của chunk
            chunk_end_char = chunk_start_char + len(chunk.page_content)
            
            chunk_start_line = 1
            chunk_end_line = 1
            
            # Tra cứu vị trí ký tự đầu thuộc dòng nào trong bản đồ
            for start_idx, end_idx, line_num in line_map:
                if start_idx <= chunk_start_char <= end_idx:
                    chunk_start_line = line_num
                    break
                    
            # Tra cứu vị trí ký tự cuối thuộc dòng nào trong bản đồ
            for start_idx, end_idx, line_num in line_map:
                if start_idx <= max(start_idx, chunk_end_char - 1) <= end_idx:
                    chunk_end_line = line_num
                    break
            
            # ĐỒNG BỘ ĐỊNH DẠNG: Đổi "Dòng số:" thành "Vị trí: Dòng" để LLM trích xuất chính xác
            if chunk_start_line == chunk_end_line:
                chunk.metadata["location"] = f"Vị trí: Dòng {chunk_start_line}"
            else:
                chunk.metadata["location"] = f"Vị trí: Dòng {chunk_start_line}-{chunk_end_line}"
                
            # Xóa trường dữ liệu nháp start_index của LangChain để database gọn sạch
            if "start_index" in chunk.metadata:
                del chunk.metadata["start_index"]
                
            final_chunks.append(chunk)
            
    return final_chunks