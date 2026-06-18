import os
import chromadb
from src.config import Config
from langchain_chroma import Chroma 

def get_vector_store(embeddings=None):
    """Khởi tạo Chroma, tự động xử lý nếu quên truyền tham số embeddings"""
    if embeddings is None:
        from src.database.embeddings import get_embedding_model
        embeddings = get_embedding_model()
        
    return Chroma(
        collection_name="enterprise_rag_db",
        embedding_function=embeddings,
        persist_directory=Config.CHROMA_DIR
    )


def get_all_uploaded_files() -> list[str]:
    """Tự động quét collection hiện có và lấy danh sách các tên file duy nhất"""
    client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
    
    # 1. Tự động lấy danh sách tất cả các collection đang có trong hệ thống
    collections = client.list_collections()
    if not collections:
        print("Không tìm thấy bất kỳ Collection nào trong database.")
        return []
    
    # 2. Chọn collection đầu tiên tìm thấy để truy vấn dữ liệu
    target_collection = collections[0]
    results = target_collection.get(include=["metadatas"])
    metadatas = results.get("metadatas", [])
    
    files = set()
    for meta in metadatas:
        if meta and "source" in meta:
            file_name = os.path.basename(meta["source"])
            files.add(file_name)
            
    return list(files)

def delete_document_by_name(filename: str) -> bool:
    """Xóa sạch TOÀN BỘ dữ liệu thuộc về một file cụ thể ra khỏi Database"""
    try:
        client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
        
        collections = client.list_collections()
        if not collections:
            return False
            
        target_collection = collections[0]
        
        # SỬA TẠI ĐÂY: Thêm limit=None để lấy ra TẤT CẢ các chunks đang có trong DB
        results = target_collection.get(include=["metadatas"], limit=None)
        metadatas = results.get("metadatas", [])
        ids = results.get("ids", [])
        
        ids_to_delete = []
        for idx, meta in enumerate(metadatas):
            if meta and "source" in meta:
                # So sánh tên file gốc sau khi đã loại bỏ đường dẫn thư mục
                if os.path.basename(meta["source"]) == filename:
                    ids_to_delete.append(ids[idx])
        
        if ids_to_delete:
            # Tiến hành xóa hàng loạt theo danh sách ID đã quét sạch
            target_collection.delete(ids=ids_to_delete)
            print(f" Đã xóa thành công {len(ids_to_delete)} đoạn dữ liệu của file {filename}")
            return True
            
        print(f" Không tìm thấy đoạn dữ liệu nào khớp với file {filename}")
        return False
    except Exception as e:
        print(f"Lỗi khi xóa file khỏi ChromaDB: {e}")
        return False
    
def get_file_content_by_name(filename: str) -> str:
    """Lấy toàn bộ nội dung văn bản (page_content) hợp nhất của một file từ DB"""
    try:
        client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
        collections = client.list_collections()
        if not collections:
            return ""
            
        target_collection = collections[0]
        # Quét sạch không giới hạn để lấy toàn bộ text của file
        results = target_collection.get(include=["metadatas", "documents"], limit=None)
        metadatas = results.get("metadatas", [])
        documents = results.get("documents", [])
        
        full_text_list = []
        for idx, meta in enumerate(metadatas):
            if meta and "source" in meta:
                if os.path.basename(meta["source"]) == filename:
                    full_text_list.append(documents[idx])
                    
        # Nối tất cả các đoạn chunk lại thành một văn bản duy nhất
        return "\n\n".join(full_text_list)
    except Exception as e:
        print(f"Lỗi khi lấy nội dung file từ ChromaDB: {e}")
        return ""
