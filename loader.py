import os
import base64
import sys
import subprocess

# 授權檔路徑與鹽值 (務必與 Encoder 保持一致)
LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"

def bootstrap():
    # 🌟 修改點：直接從環境變數讀取已在 Colab 前端驗證過的 Email
    current_email = os.environ.get("AUTO_VERIFIED_EMAIL")

    if not current_email:
        print("❌ [Error] 環境變數中缺失身分資訊，請重新啟動。")
        sys.exit(1)
    
    print(f"👤 身分驗證成功 ({current_email})")

    # 檢查 Repo 參數
    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")
    if not user_name or not repo_name:
        print(f"❌ [Error] 啟動參數缺失。")
        sys.exit(1)

    print("🚀 [2/4] 驗證內部授權權限...")
    if not os.path.exists(LICENSE_PATH):
        print(f"❌ [Error] 找不到授權檔，請確認 Drive 已掛載。")
        sys.exit(1)

    # 解析 Token
    try:
        with open(LICENSE_PATH, "r") as f:
            encoded_str = f.read().strip()
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        if not decoded_str.endswith(SALT):
            sys.exit(1)
        real_token = decoded_str.replace(SALT, "")
    except Exception as e:
        print(f"❌ [Error] 授權異常: {e}")
        sys.exit(1)

    print(f"🚀 [3/4] 建立安全通道 [{repo_name}]...")
    os.environ["GITHUB_TOKEN"] = real_token
    repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
    
    try:
        # 安裝私有 Repo
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", f"git+{repo_url}"])
        print(f"🚀 [4/4] 核心引擎加載完成！")
        print(f"🎊 [Final] Whisper 已成功就緒。")
    except Exception as e:
        print(f"\n❌ [Error] 同步失敗，請檢查權限。")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
