import streamlit as st
import numpy as np
import os
from dotenv import load_dotenv
from firebase_client import sign_in, sign_up
from rag import (
    load_knowledge_base,
    get_embeddings_batch,
    retrieve_top_k,
    generate_rag_answer
)

load_dotenv()

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="HCMC Travel Assistant - RAG Chat",
    page_icon="✈️",
    layout="centered"
)

# Khởi tạo session_state cho việc xác thực và lịch sử chat
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- CACHE: Load knowledge base và tạo embeddings 1 lần duy nhất ---
@st.cache_resource
def init_vector_database():
    kb = load_knowledge_base("knowledge_base.json")
    if not kb:
        return kb, np.array([])
    texts = [f"{entry['title']}: {entry['text']}" for entry in kb]
    try:
        vectors = get_embeddings_batch(texts)
        return kb, vectors
    except Exception as e:
        st.error(f"Lỗi khởi tạo vector database từ Ollama: {str(e)}")
        return kb, np.array([])

kb_entries, kb_vectors = init_vector_database()

# ==========================================
# GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ (FIREBASE)
# ==========================================
if not st.session_state.user:
    st.title("🏙️ HCMC Travel Assistant - Đăng Nhập")
    st.markdown("Vui lòng đăng nhập để sử dụng trợ lý du lịch thông minh.")
    
    auth_tab1, auth_tab2 = st.tabs(["Đăng Nhập (Sign In)", "Đăng Ký (Sign Up)"])
    
    with auth_tab1:
        st.subheader("Đăng nhập tài khoản")
        signin_email = st.text_input("Email", key="signin_email")
        signin_password = st.text_input("Mật khẩu", type="password", key="signin_password")
        
        if st.button("Đăng Nhập", type="primary"):
            if not signin_email or not signin_password:
                st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
            else:
                with st.spinner("Đang xác thực..."):
                    result = sign_in(signin_email, signin_password)
                    if result["success"]:
                        st.session_state.user = result["data"]
                        st.success("Đăng nhập thành công!")
                        st.rerun()
                    else:
                        st.error(result["error"])
                        
    with auth_tab2:
        st.subheader("Tạo tài khoản mới")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Mật khẩu (tối thiểu 6 ký tự)", type="password", key="signup_password")
        
        if st.button("Đăng Ký"):
            if not signup_email or not signup_password:
                st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
            else:
                with st.spinner("Đang tạo tài khoản..."):
                    result = sign_up(signup_email, signup_password)
                    if result["success"]:
                        st.success("Đăng ký thành công! Bạn có thể chuyển sang tab Đăng Nhập.")
                    else:
                        st.error(result["error"])

# ==========================================
# GIAO DIỆN CHAT RAG (SAU KHI ĐĂNG NHẬP)
# ==========================================
else:
    user_email = st.session_state.user.get("email", "Người dùng")
    
    # Thanh Sidebar hiển thị thông tin và nút Đăng xuất
    with st.sidebar:
        st.write(f"👤 **Tài khoản:** `{user_email}`")
        st.divider()
        if st.button("Đăng Xuất (Sign Out)", type="secondary"):
            # Xóa session state theo yêu cầu đề bài
            st.session_state.user = None
            st.session_state.chat_history = []
            st.success("Đã đăng xuất thành công!")
            st.rerun()
            
        st.info("💡 **Gợi ý câu hỏi test:**\n- Giờ mở cửa Dinh Độc Lập?\n- Chợ Bến Thành bán gì?\n- Có địa điểm trượt tuyết nào ở đây không?")

    st.title("🇻🇳 Trợ Lý Du Lịch TP.HCM (RAG Chat)")
    st.markdown("Hỏi đáp thông tin về các địa điểm, danh lam thắng cảnh tại TP.HCM dựa trên cẩm nang chuẩn.")

    # Kiểm tra trạng thái cẩm nang
    if not kb_entries or kb_vectors.size == 0:
        st.error("⚠️ Không tìm thấy dữ liệu cẩm nang (`knowledge_base.json`) hoặc chưa kết nối được Ollama server. Vui lòng kiểm tra lại file `.env` và kết nối mạng.")
    else:
        # Hiển thị lịch sử trò chuyện trong phiên làm việc hiện tại
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Nếu có chứa tài liệu truy xuất, hiển thị panel mở rộng
                if "retrieved_docs" in message and message["retrieved_docs"]:
                    with st.expander("📚 Xem các mục cẩm nang được truy xuất (RAG Context)"):
                        for entry, score in message["retrieved_docs"]:
                            st.markdown(f"**[{entry['id']}] {entry['title']}** (Score: `{score:.4f}`)  \n_{entry['text']}_  \n*Nguồn: {entry['source']}*")
                            st.markdown("---")

        # Khung nhập câu hỏi từ người dùng
        if query := st.chat_input("Nhập câu hỏi của bạn về du lịch TP.HCM..."):
            if not query.strip():
                st.warning("Vui lòng không để trống câu hỏi.")
            else:
                # 1. Hiển thị câu hỏi người dùng
                st.session_state.chat_history.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

                # 2. Xử lý RAG: Truy xuất top-k và sinh câu trả lời
                with st.chat_message("assistant"):
                    with st.spinner("Đang tìm kiếm thông tin và tổng hợp câu trả lời..."):
                        try:
                            # Lấy top 2 kết quả phù hợp nhất để giảm thời gian phản hồi
                            top_docs = retrieve_top_k(query, kb_entries, kb_vectors, k=2)
                            
                            # Sinh câu trả lời từ qwen3:4b
                            answer = generate_rag_answer(query, top_docs)
                            
                            st.markdown(answer)
                            
                            # Hiển thị panel tài liệu nguồn
                            if top_docs:
                                with st.expander("📚 Xem các mục cẩm nang được truy xuất (RAG Context)"):
                                    for entry, score in top_docs:
                                        st.markdown(f"**[{entry['id']}] {entry['title']}** (Score: `{score:.4f}`)  \n_{entry['text']}_  \n*Nguồn: {entry['source']}*")
                                        st.markdown("---")
                                        
                            # Lưu vào lịch sử phiên làm việc
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer,
                                "retrieved_docs": top_docs
                            })
                        except Exception as e:
                            err_msg = f"Đã xảy ra lỗi khi xử lý RAG: {str(e)}"
                            st.error(err_msg)
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": err_msg
                            })