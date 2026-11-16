# SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT

Trợ lý du lịch TP.HCM dựa trên kiến trúc RAG (Retrieval-Augmented Generation) kết hợp:
- Streamlit UI
- Firebase Authentication cho chức năng đăng nhập/đăng ký
- Ollama embeddings + chat model để truy xuất và tổng hợp thông tin
- Cẩm nang du lịch TP.HCM lưu trong file JSON

Dự án này cho phép người dùng đăng nhập bằng email/password, sau đó đặt câu hỏi về các địa điểm, giờ mở cửa, giá vé, khu vực, và nhận câu trả lời dựa trên dữ liệu du lịch nội bộ thay vì đoán mơ hồ.

## Tính năng chính

- Đăng nhập / đăng ký tài khoản bằng Firebase Email/Password
- Giao diện chat thân thiện bằng Streamlit
- Truy xuất top-k tài liệu phù hợp bằng cosine similarity
- Tạo câu trả lời từ model Ollama theo ngữ cảnh đã truy xuất
- Hiển thị nguồn tài liệu (retrieved docs) cho mỗi câu trả lời
- Dữ liệu cẩm nang có thể mở rộng dễ dàng qua `knowledge_base.json`

## Công nghệ sử dụng

- Python 3.10+
- Streamlit
- Firebase REST API
- Ollama
- NumPy
- python-dotenv

## Cấu trúc thư mục

```text
SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT/
├── app.py                 # Giao diện Streamlit chính
├── firebase_client.py     # Xử lý đăng nhập, đăng ký với Firebase
├── rag.py                # Logic embeddings, retrieval và LLM answer
├── knowledge_base.json   # Cẩm nang du lịch TP.HCM
├── .env.example          # Mẫu biến môi trường
├── requirement.txt       # Danh sách dependency
├── README.md             # Tài liệu dự án
└── .venv                 # Môi trường ảo (nếu đã tạo)
```

## Yêu cầu môi trường

Trước khi chạy dự án, hãy đảm bảo bạn đã cài đặt:

- Python 3.10+
- Ollama đã được cài đặt và đang chạy
- Một tài khoản Firebase với Email/Password Authentication bật
- Kết nối từ Ollama ra ngoài nếu cần truy cập qua mạng công cộng (ví dụ: Pinggy / ngrok / tunnel khác)

## Cài đặt

1. Clone repository:

```bash
git clone https://github.com/PTNhan-2538/SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT.git
cd SIGN-IN-TRAVEL-ASSISTANT-WITH-RAG-CHAT
```

2. Tạo môi trường ảo và cài đặt dependency:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirement.txt
```

3. Tạo file `.env` dựa trên `.env.example`:

```bash
copy .env.example .env
```

4. Điền thông tin trong `.env`:

```env
# Ollama & Pinggy Server Configuration
OLLAMA_PUBLIC_URL=https://your-pinggy-url.pinggy.link

# Firebase Web / REST API Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
```

### Giải thích biến môi trường

- `OLLAMA_PUBLIC_URL`: URL công khai của Ollama thông qua tunnel. Dự án sẽ gọi `POST {OLLAMA_PUBLIC_URL}/api/embed` và `POST {OLLAMA_PUBLIC_URL}/api/chat`.
- `FIREBASE_API_KEY`: API key của project Firebase bạn đang dùng.
- `FIREBASE_AUTH_DOMAIN`: domain auth của project Firebase (dùng cho thông tin project, không dùng trực tiếp bởi code hiện tại nhưng nên để đúng cấu hình).

## Chuẩn bị model Ollama

Cài đặt và pull các model cần thiết:

```bash
ollama pull embeddinggemma
ollama pull qwen3:4b
```

Nếu Ollama đang chạy local, hãy đảm bảo API server accessible từ máy chạy ứng dụng. Nếu cần public URL, hãy expose dịch vụ qua tunnel.

## Chạy ứng dụng

Từ thư mục dự án:

```bash
streamlit run app.py
```

Mở trình duyệt tại địa chỉ hiển thị trong terminal, ví dụ:

```text
Local URL: http://localhost:8501
```

## Cách sử dụng

1. Truy cập giao diện đăng nhập.
2. Đăng ký hoặc đăng nhập bằng email và mật khẩu.
3. Sau khi đăng nhập, bạn có thể hỏi các câu hỏi như:
   - Giờ mở cửa Dinh Độc Lập?
   - Chợ Bến Thành bán gì?
   - Có địa điểm trượt tuyết nào ở đây không?
4. Hệ thống sẽ:
   - truy xuất các tài liệu liên quan
   - so sánh độ tương đồng bằng vector
   - sinh câu trả lời bằng Ollama dựa trên ngữ cảnh
   - hiển thị nguồn tài liệu để kiểm tra

## Lưu ý quan trọng

- Hệ thống chỉ trả lời dựa trên `knowledge_base.json` + context được truy xuất, không phải đoán theo kiến thức chung.
- Nếu không tìm thấy thông tin phù hợp trong dữ liệu đã cho, model sẽ trả về câu: `I don't know based on the provided travel guide.`
- Đảm bảo Firebase API key hợp lệ và Ollama đang online trước khi sử dụng.

## Mở rộng dự án

Bạn có thể dễ dàng mở rộng bằng cách:

- thêm nhiều địa điểm vào `knowledge_base.json`
- đổi model embeddings hoặc chat model trong `rag.py`
- tích hợp cơ sở dữ liệu hoặc lưu lịch sử chat dài hạn
- thêm tính năng đánh giá score, filter theo category, hoặc multilingual support

## Giấy phép

Dự án này được cung cấp theo mục đích học tập và phát triển nội bộ trong môi trường cá nhân / nhóm. Nếu bạn muốn sử dụng trong sản phẩm thương mại hoặc công khai, vui lòng kiểm tra lại điều kiện và nguồn dữ liệu du lịch trước khi triển khai.

## Liên hệ / tài liệu tham khảo

- Streamlit: https://streamlit.io/
- Ollama: https://ollama.com/
- Firebase Auth REST API: https://firebase.google.com/docs/reference/rest/auth
