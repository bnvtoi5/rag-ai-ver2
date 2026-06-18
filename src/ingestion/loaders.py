import os
from langchain_core.documents import Document

def load_documents_from_folder(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return documents

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # 1. XỬ LÝ FILE TXT
        if file.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                # Đọc toàn bộ file thành một chuỗi duy nhất để giữ nguyên index ký tự gốc
                full_text = f.read()  
            
            documents.append(Document(
                page_content=full_text,
                metadata={
                    "source": file_path, 
                    "is_pdf": False,
                    "page": 1  # File TXT mặc định coi như thuộc trang 1
                }
            ))
            
        # 2. XỬ LÝ FILE PDF (Sử dụng PyMuPDF để bóc tách trang chính xác tuyệt đối)
        elif file.endswith('.pdf'):
            import fitz  # Thư viện PyMuPDF
            
            try:
                doc_pdf = fitz.open(file_path)
                for page_num, page in enumerate(doc_pdf):
                    text = page.get_text()
                    
                    # Tạo Document object độc lập cho từng trang một
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "source": file_path,
                            "is_pdf": True,
                            "page": page_num + 1  # fitz đếm từ 0 nên cộng 1 để ra đúng trang thực tế
                        }
                    ))
                doc_pdf.close()
            except Exception as e:
                print(f"Lỗi khi đọc file PDF {file}: {e}")
            
    return documents