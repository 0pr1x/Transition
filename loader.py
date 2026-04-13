import os
import base64
import sys
import subprocess

# 授權檔路徑與鹽值 (務必與 Encoder 保持一致)
LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"

def get_current_email():
    """獲取當前 Colab 使用者 Email，若無則啟動授權視窗"""
    try:
        # 嘗試靜默抓取
        email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        
        # 若抓不到，主動嘗試觸發 auth
        if not email or "(unset)" in email:
            from google.colab import auth
            auth.authenticate_user()
            email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        return email
    except Exception:
        return None

def bootstrap():
    print("🚀 [1/4] 啟動身分安全檢查...")
    
    from google.colab import auth, drive
    auth.authenticate_user()
    
    # 檢查是否已掛載再決定要不要 mount
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    else:
        print("✅ Drive 已掛載，跳過。")
    
    import subprocess
    email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
    if not email or "(unset)" in email:
        print("❌ [Error] 無法識別 Google 帳號身分。")
        sys.exit(1)
    
    os.environ["AUTO_VERIFIED_EMAIL"] = email
    print(f"👤 已識別帳號: {email}")
    

    # 檢查 Repo 參數
    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")
    if not user_name or not repo_name:
        print(f"❌ [Error] 啟動參數缺失: USER={user_name}, REPO={repo_name}")
        sys.exit(1)

    print("🚀 [2/4] 驗證內部授權權限...")
    if not os.path.exists(LICENSE_PATH):
        if not os.path.exists("/content/drive/MyDrive"):
            print("❌ [Error] Google Drive 尚未掛載，請先執行 drive.mount()")
        else:
            print(f"❌ [Error] 找不到授權檔: {LICENSE_PATH}")
        sys.exit(1)

    # 解析 Token
    try:
        with open(LICENSE_PATH, "r") as f:
            encoded_str = f.read().strip()
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        
        if not decoded_str.endswith(SALT):
            print("❌ [Error] 授權密鑰校驗失敗 (SALT Mismatch)")
            sys.exit(1)
        
        real_token = decoded_str.replace(SALT, "")
    except Exception as e:
        print(f"❌ [Error] 授權檔解析異常: {e}")
        sys.exit(1)

    print(f"🚀 [3/4] 建立安全通道 [{repo_name}]...")
    os.environ["GITHUB_TOKEN"] = real_token
    # 構建帶有 Token 的 Git URL
    repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
    
    # 使用 subprocess 安裝，以便在出錯時能看到具體原因
    # 這裡移除 -q (quiet) 標籤，讓使用者看到安裝進度
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"git+{repo_url}"])
        print(f"🚀 [4/4] 核心引擎加載完成！")
        print(f"🎊 [Final] {repo_name} 已成功就緒。")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ [Error] 同步失敗 (Exit Code: {e.returncode})")
        print(f"💡 請檢查 GitHub Token 是否具備該 Private Repo 的讀取權限。")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
