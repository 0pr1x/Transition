import os
import base64
import sys
import subprocess

# 授權檔路徑與鹽值
LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"

def bootstrap():
    # 1. 嘗試靜默獲取身分
    current_email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()

    # 2. 🌟 核心修正：如果抓不到，主動啟動授權視窗
    if not current_email or "(unset)" in current_email:
        print("🔐 偵測到身分尚未驗證，正在啟動 Google 安全認證...")
        try:
            from google.colab import auth
            auth.authenticate_user()
            current_email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        except Exception as e:
            print(f"❌ 驗證程序啟動失敗: {e}")
            sys.exit(1)

    # 3. 再次檢查是否真的抓到 Email
    if not current_email or "(unset)" in current_email:
        print("⚠️ 仍無法識別身份，請重新執行 Cell 並點選允許授權。")
        sys.exit(1)
    else:
        os.environ["AUTO_VERIFIED_EMAIL"] = current_email
        print(f"🔍 身份識別成功: {current_email}")

    # 4. 動態從環境變數抓取目標 Repo 資訊
    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")

    if not user_name or not repo_name:
        print("❌ 啟動失敗：未提供目標儲存庫參數。")
        sys.exit(1)
        
    # 5. 檢查授權檔
    if not os.path.exists(LICENSE_PATH):
        print(f"❌ 找不到授權檔，請確認已將 license.key 放入: {LICENSE_PATH}")
        sys.exit(1)
        
    # 6. 讀取並解碼 Token
    with open(LICENSE_PATH, "r") as f:
        encoded_str = f.read().strip()
    
    try:
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        if not decoded_str.endswith(SALT):
            raise ValueError("無效的授權Salt")
        real_token = decoded_str.replace(SALT, "")
    except Exception:
        print("❌ 授權檔解析失敗，檔案可能已損毀或被竄開。")
        sys.exit(1)

    # 7. 執行安裝
    os.environ["GITHUB_TOKEN"] = real_token
    repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
    
    print(f"🔐 授權通過，正在建立安全通道同步 [{repo_name}]...")
    exit_code = os.system(f"pip install -q git+{repo_url} > /dev/null 2>&1")
    
    if exit_code == 0:
        print(f"✅ [{repo_name}] 載入完成！")
    else:
        print("❌ 下載失敗，請檢查 Token 權限。")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
