import os
import subprocess
import shutil

CRD_SSH_Code = input("Google CRD SSH Code :")
username = "user"
password = "root"

# Tạo user (chạy khi đang ở root)
os.system(f"useradd -m {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | chpasswd")
os.system("sed -i 's/\\/bin\\/sh/\\/bin\\/bash/g' /etc/passwd")

Pin = 123456
Autostart = True

class CRDSetup:
    def __init__(self, user):
        os.system("apt update -y")
        self.installCRD()
        self.installDesktopEnvironment()
        self.changewall()
        self.installGoogleChrome()
        self.installMidori()
        self.installQbit()
        self.finish(user)

    @staticmethod
    def installCRD():
        subprocess.run(["wget", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "chrome-remote-desktop_current_amd64.deb"])
        subprocess.run(["apt", "install", "-y", "--fix-broken"])
        print("✅ Chrome Remote Desktop Installed")

    @staticmethod
    def installDesktopEnvironment():
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        os.system("apt install -y xfce4 desktop-base xfce4-terminal")
        os.system('bash -c \'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session\'')
        os.system("apt remove -y gnome-terminal")
        os.system("apt install -y xscreensaver")
        os.system("apt purge -y light-locker")
        os.system("apt install --reinstall -y xfce4-screensaver")
        os.system("systemctl disable lightdm.service || true")
        print("✅ XFCE4 Desktop Environment Installed")

    @staticmethod
    def installGoogleChrome():
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"])
        subprocess.run(["apt", "install", "-y", "--fix-broken"])
        print("✅ Google Chrome Installed")

    @staticmethod
    def installMidori():
        """
        Cố gắng cài bằng apt nếu có, nếu không sẽ tải .deb từ trang chính (fallback).
        Giữ nhẹ và phù hợp cho VPS có tài nguyên hạn chế.
        """
        print("⏳ Installing Midori (lightweight browser)...")
        # Try apt install first
        r = subprocess.run(["apt", "update", "-y"])
        r = subprocess.run(["apt", "install", "-y", "midori"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            print("✅ Midori installed via apt")
            return

        # Fallback: try download .deb from upstream (Astian/Midori)
        deb_url = "https://astian.org/midori-browser/download/debian/amd64/midori-latest.deb"
        tmp_deb = "/tmp/midori-latest.deb"
        try:
            subprocess.run(["wget", "-O", tmp_deb, deb_url], check=True)
            subprocess.run(["dpkg", "--install", tmp_deb], check=False)
            subprocess.run(["apt", "install", "-y", "--fix-broken"], check=False)
            print("✅ Midori installed via downloaded .deb (fallback)")
        except Exception:
            print("⚠️ Failed to install Midori via fallback. You can install it manually later.")

    @staticmethod
    def installQbit():
        subprocess.run(["apt", "update", "-y"])
        subprocess.run(["apt", "install", "-y", "qbittorrent"])
        print("✅ Qbittorrent Installed")

    @staticmethod
    def changewall():
        wallpaper_url = "https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg"
        wallpaper_file = "xfce-verticals.png"
        os.system(f"curl -s -L -k -o {wallpaper_file} {wallpaper_url}")
        current_dir = os.getcwd()
        src = os.path.join(current_dir, wallpaper_file)
        dst = "/usr/share/backgrounds/xfce/"
        try:
            os.makedirs(dst, exist_ok=True)
            shutil.copy(src, dst)
            print("✅ Wallpaper Changed")
        except Exception as e:
            print(f"⚠️ Could not copy wallpaper: {e}")

    @staticmethod
    def finish(user):
        if Autostart:
            os.makedirs(f"/home/{user}/.config/autostart", exist_ok=True)
            link = "https://www.youtube.com/@LacDev-db2vx"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
            with open(f"/home/{user}/.config/autostart/colab.desktop", "w") as f:
                f.write(colab_autostart)
            os.system(f"chmod +x /home/{user}/.config/autostart/colab.desktop")
            os.system(f"chown -R {user}:{user} /home/{user}/.config")

        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRD_SSH_Code} --pin={Pin}"
        os.system(f"su - {user} -c '{command}'")
        os.system("service chrome-remote-desktop start || true")

        print("====================================================")
        print("✅ Setup Complete")
        print("User: {}".format(username))
        print("Pass: {}".format(password))
        print("PIN: {}".format(Pin))
        print("Autostart link: https://www.youtube.com/@LacDev-db2vx")
        print("====================================================")

        while True:
            pass

# === Main Execution ===
try:
    if CRD_SSH_Code == "":
        print("⚠️ Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("⚠️ Enter a pin with 6 or more digits")
    else:
        CRDSetup(username)
except NameError:
    print("⚠️ 'username' variable not found, create a user first")
