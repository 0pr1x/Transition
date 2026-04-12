import os
import base64
import sys

# 授權檔路徑與鹽值保持不變
LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"

def bootstrap():
    # 🌟 動態從 Colab 環境變數抓取目標 Repo 資訊
    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")

    if not user_name or not repo_name:
        print("❌ 啟動失敗：未提供目標儲存庫參數。")
        sys.exit(1)

    if not os.path.exists(LICENSE_PATH):
        print(f"❌ 找不到授權檔，請確認已將 license.key 放入: {LICENSE_PATH}")
        sys.exit(1)
    
    # 讀取並解碼 Base64
    with open(LICENSE_PATH, "r") as f:
        encoded_str = f.read().strip()
    
    try:
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        if not decoded_str.endswith(SALT):
            raise ValueError("無效的授權鹽值")
        real_token = decoded_str.replace(SALT, "")
    except Exception:
        print("❌ 授權檔解析失敗，檔案可能已損毀或被竄改。")
        sys.exit(1)

    # 注入 Token 並執行安裝
    os.environ["GITHUB_TOKEN"] = real_token
    repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
    
    print(f"🔐 授權通過，正在建立安全通道同步 [{repo_name}] 核心引擎...")
    exit_code = os.system(f"pip install -q git+{repo_url} > /dev/null 2>&1")
    
    if exit_code == 0:
        print("✅ 核心引擎載入完成！")
    else:
        print("❌ 核心引擎下載失敗，請檢查 Token 權限或網路。")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
