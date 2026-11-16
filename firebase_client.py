import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "").strip()

ERROR_MESSAGES = {
    "EMAIL_EXISTS": "Email này đã được đăng ký trước đó.",
    "OPERATION_NOT_ALLOWED": "Tính năng đăng nhập bằng Email/Mật khẩu chưa được bật trên Firebase.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Quá nhiều lần thử thất bại. Vui lòng thử lại sau.",
    "EMAIL_NOT_FOUND": "Không tìm thấy tài khoản với email này.",
    "INVALID_PASSWORD": "Mật khẩu không chính xác.",
    "INVALID_LOGIN_CREDENTIALS": "Email hoặc mật khẩu không chính xác.",
    "USER_DISABLED": "Tài khoản này đã bị vô hiệu hóa.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "Mật khẩu quá yếu (cần ít nhất 6 ký tự).",
    "INVALID_EMAIL": "Định dạng email không hợp lệ."
}

def _parse_firebase_error(response_json: dict) -> str:
    """Chuyển đổi mã lỗi từ Firebase REST API sang thông báo thân thiện."""
    raw_msg = response_json.get("error", {}).get("message", "Lỗi xác thực không xác định.")
    for key, friendly_msg in ERROR_MESSAGES.items():
        if key in raw_msg:
            return friendly_msg
    return f"Lỗi Firebase: {raw_msg}"

def sign_up(email: str, password: str) -> dict:
    """
    Đăng ký tài khoản mới với Email và Password.
    Trả về dict: {"success": bool, "data": dict | None, "error": str | None}
    """
    if not FIREBASE_API_KEY:
        return {"success": False, "data": None, "error": "Thiếu FIREBASE_API_KEY trong file .env."}
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        if res.status_code == 200:
            return {"success": True, "data": data, "error": None}
        return {"success": False, "data": None, "error": _parse_firebase_error(data)}
    except requests.exceptions.RequestException as e:
        return {"success": False, "data": None, "error": f"Lỗi kết nối mạng tới Firebase: {str(e)}"}

def sign_in(email: str, password: str) -> dict:
    """
    Đăng nhập bằng Email và Password.
    Trả về dict: {"success": bool, "data": dict | None, "error": str | None}
    """
    if not FIREBASE_API_KEY:
        return {"success": False, "data": None, "error": "Thiếu FIREBASE_API_KEY trong file .env."}
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        if res.status_code == 200:
            return {"success": True, "data": data, "error": None}
        return {"success": False, "data": None, "error": _parse_firebase_error(data)}
    except requests.exceptions.RequestException as e:
        return {"success": False, "data": None, "error": f"Lỗi kết nối mạng tới Firebase: {str(e)}"}