import os
import base64
import sys
import subprocess

LICENSE_PATH = "/content/drive/MyDrive/Whisper_Models/license.key"
SALT = "WTusingOnlyidX2"
_BOOTSTRAP_DONE = False

def bootstrap():
    global _BOOTSTRAP_DONE
    if _BOOTSTRAP_DONE:
        return

    print("🚀 [1/4] 啟動身分安全檢查...")

    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    else:
        print("✅ Drive 已掛載，跳過。")

    import time
    email = ""
    for _ in range(5):
        email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        if email and "(unset)" not in email:
            break
        time.sleep(2)

    if not email or "(unset)" in email:
        try:
            from google.colab import auth
            auth.authenticate_user()
            email = subprocess.getoutput("gcloud config get-value account 2>/dev/null").strip()
        except Exception:
            pass

    if not email or "(unset)" in email:
        print("❌ [Error] 無法識別 Google 帳號身分。")
        sys.exit(1)

    os.environ["AUTO_VERIFIED_EMAIL"] = email
    print(f"👤 已識別帳號: {email}")

    user_name = os.environ.get("TARGET_USER")
    repo_name = os.environ.get("TARGET_REPO")
    if not user_name or not repo_name:
        print(f"❌ [Error] 啟動參數缺失: USER={user_name}, REPO={repo_name}")
        sys.exit(1)

    print("🚀 [2/4] 驗證內部授權權限...")
    if not os.path.exists(LICENSE_PATH):
        print(f"❌ [Error] 找不到授權檔: {LICENSE_PATH}")
        sys.exit(1)

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

    os.environ["GITHUB_TOKEN"] = real_token

    try:
        import whisper_tool
        print("✅ [3/4] 套件已存在，跳過安裝。")
    except ImportError:
        print(f"🚀 [3/4] 建立安全通道 [{repo_name}]...")
        repo_url = f"https://{real_token}@github.com/{user_name}/{repo_name}.git"
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"git+{repo_url}"])
            print(f"🚀 [4/4] 核心引擎加載完成！")
            print(f"🎊 [Final] {repo_name} 已成功就緒。")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ [Error] 同步失敗 (Exit Code: {e.returncode})")
            print(f"💡 請檢查 GitHub Token 是否具備該 Private Repo 的讀取權限。")
            sys.exit(1)

    _BOOTSTRAP_DONE = True

if __name__ == "__main__":
    bootstrap()
