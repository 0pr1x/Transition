import os
import base64
import sys
import subprocess

LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"

def get_current_email():
    try:
        # 增加 2>/dev/null 屏蔽錯誤輸出，並 strip() 清除換行
        email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        
        # 💡 如果靜默抓取失敗，主動嘗試觸發一次 auth
        if not email or "(unset)" in email:
            from google.colab import auth
            auth.authenticate_user()
            email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        return email
    except:
        return None

def bootstrap():
    print("🚀 [Step 1] 開始身分檢查...")
    current_email = get_current_email()

    if not current_email:
        print("❌ [Error] 無法識別 Google 帳號身分。")
        print("💡 請先在 Colab 執行: from google.colab import auth; auth.authenticate_user()")
        sys.exit(1)
    
    os.environ["AUTO_VERIFIED_EMAIL"] = current_email
    print(f"✅ 身份識別成功: {current_email}")

    print("🚀 [Step 2] 檢查 Repo 參數...")
    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")
    if not user_name or not repo_name:
        print(f"❌ [Error] 參數缺失: USER={user_name}, REPO={repo_name}")
        sys.exit(1)

    print(f"🚀 [Step 3] 檢查授權檔: {LICENSE_PATH}")
    if not os.path.exists(LICENSE_PATH):
        # 額外檢查 Drive 是否真的掛載
        if not os.path.exists("/content/drive/MyDrive"):
            print("❌ [Error] Google Drive 尚未掛載，請先執行 drive.mount()")
        else:
            print(f"❌ [Error] 檔案不存在於 {LICENSE_PATH}，請檢查路徑。")
        sys.exit(1)

    print("🚀 [Step 4] 解析 Token...")
    try:
        with open(LICENSE_PATH, "r") as f:
            encoded_str = f.read().strip()
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        if not decoded_str.endswith(SALT):
            print("❌ [Error] 鹽值校驗失敗 (SALT Mismatch)")
            sys.exit(1)
        real_token = decoded_str.replace(SALT, "")
    except Exception as e:
        print(f"❌ [Error] Token 解析異常: {e}")
        sys.exit(1)

    print(f"🚀 [Step 5] 安裝核心引擎 [{repo_name}]...")
    os.environ["GITHUB_TOKEN"] = real_token
    repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
    
    # 這裡暫時移除 > /dev/null 以便觀察安裝報錯
    exit_code = os.system(f"pip install -q git+{repo_url}")
    
    if exit_code == 0:
        print(f"🎊 [Final] {repo_name} 載入完成！")
    else:
        print(f"❌ [Error] Pip 安裝失敗 (Exit Code: {exit_code})")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
