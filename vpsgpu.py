import os
import subprocess
import shutil

CRD_SSH_Code = input("Google CRD SSH Code :")
username = "user"
password = "root"

subprocess.run(["sudo", "useradd", "-m", username], check=False)
subprocess.run(["sudo", "adduser", username, "sudo"], check=False)
subprocess.run(f"echo '{username}:{password}' | sudo chpasswd", shell=True, check=False)
subprocess.run(["sudo", "sed", "-i", "s#/bin/sh#/bin/bash#g", "/etc/passwd"], check=False)

Pin = 123456
Autostart = True

class CRDSetup:
    def __init__(self, user):
        subprocess.run(["sudo", "apt", "update", "-y"], check=False)
        self.installGPUDrivers()
        self.enableHardwareAccel()
        self.installCRD()
        self.installDesktopEnvironment()
        self.changewall()
        self.installGoogleChrome()
        self.installMidori()
        self.installQbit()
        self.finish(user)

    # ---------------- GPU BOOST ----------------
    @staticmethod
    def installGPUDrivers():
        print("⚙️ Installing GPU drivers (NVIDIA / Intel / AMD)...")
        subprocess.run(["sudo", "apt", "install", "-y", "mesa-utils", "mesa-vulkan-drivers", "vulkan-tools"], check=False)
        # Auto-detect GPU
        gpu_info = subprocess.run("lspci | grep -i 'vga\\|3d\\|display'", shell=True, capture_output=True, text=True)
        print("🖥️ GPU Detected:", gpu_info.stdout.strip() or "Unknown")
        if "NVIDIA" in gpu_info.stdout:
            subprocess.run(["sudo", "apt", "install", "-y", "nvidia-driver-535"], check=False)
        elif "AMD" in gpu_info.stdout:
            subprocess.run(["sudo", "apt", "install", "-y", "xserver-xorg-video-amdgpu"], check=False)
        elif "Intel" in gpu_info.stdout:
            subprocess.run(["sudo", "apt", "install", "-y", "intel-media-va-driver", "vainfo"], check=False)
        else:
            print("⚠️ Không nhận diện được GPU cụ thể, chỉ cài Mesa renderer.")
        subprocess.run(["sudo", "update-initramfs", "-u"], check=False)
        print("✅ GPU Drivers Installed")

    @staticmethod
    def enableHardwareAccel():
        print("⚙️ Enabling GPU Hardware Acceleration for Chrome & XFCE...")
        chrome_flags = "--enable-gpu --ignore-gpu-blocklist --enable-zero-copy --use-gl=egl --enable-accelerated-video-decode"
        subprocess.run(["sudo", "mkdir", "-p", "/etc/chromium/policies/managed"], check=False)
        policy_path = "/etc/chromium/policies/managed/gpu_accel.json"
        policy_json = f'{{"CommandLineFlagSecurityWarningsEnabled": false, "AdditionalLaunchFlags": "{chrome_flags}"}}'
        with open("/tmp/gpu_accel.json", "w") as f:
            f.write(policy_json)
        subprocess.run(["sudo", "mv", "/tmp/gpu_accel.json", policy_path], check=False)
        # Bật GLX và compositing
        subprocess.run(["sudo", "apt", "install", "-y", "xserver-xorg-video-all", "x11-xserver-utils", "libgl1-mesa-glx"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "xfwm4", "compton"], check=False)
        subprocess.run(["sudo", "systemctl", "restart", "chrome-remote-desktop"], check=False)
        print("✅ GPU Hardware Acceleration Enabled")

    # ----------------------------------------------------------
    @staticmethod
    def installCRD():
        subprocess.run(["sudo", "wget", "-q", "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb"], check=False)
        subprocess.run(["sudo", "dpkg", "--install", "chrome-remote-desktop_current_amd64.deb"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "--fix-broken"], check=False)
        print("✅ Chrome Remote Desktop Installed")

    @staticmethod
    def installDesktopEnvironment():
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        subprocess.run(["sudo", "apt", "install", "-y", "xfce4", "desktop-base", "xfce4-terminal"], check=False)
        session_cmd = 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" | sudo tee /etc/chrome-remote-desktop-session > /dev/null'
        subprocess.run(session_cmd, shell=True, check=False)
        subprocess.run(["sudo", "apt", "remove", "-y", "gnome-terminal"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "xscreensaver"], check=False)
        subprocess.run(["sudo", "apt", "purge", "-y", "light-locker"], check=False)
        subprocess.run(["sudo", "apt", "install", "--reinstall", "-y", "xfce4-screensaver"], check=False)
        subprocess.run(["sudo", "systemctl", "disable", "lightdm.service"], check=False)
        print("✅ XFCE4 Desktop Environment Installed")

    @staticmethod
    def installGoogleChrome():
        subprocess.run(["sudo", "wget", "-q", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], check=False)
        subprocess.run(["sudo", "dpkg", "--install", "google-chrome-stable_current_amd64.deb"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "--fix-broken"], check=False)
        print("✅ Google Chrome Installed")

    @staticmethod
    def installMidori():
        print("⏳ Installing Midori (lightweight browser)...")
        subprocess.run(["sudo", "apt", "update", "-y"], check=False)
        r = subprocess.run(["sudo", "apt", "install", "-y", "midori"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if r.returncode == 0:
            print("✅ Midori installed via apt")
            return
        deb_url = "https://astian.org/midori-browser/download/debian/amd64/midori-latest.deb"
        tmp_deb = "/tmp/midori-latest.deb"
        try:
            subprocess.run(["sudo", "wget", "-O", tmp_deb, deb_url], check=True)
            subprocess.run(["sudo", "dpkg", "--install", tmp_deb], check=False)
            subprocess.run(["sudo", "apt", "install", "-y", "--fix-broken"], check=False)
            print("✅ Midori installed via downloaded .deb (fallback)")
        except Exception:
            print("⚠️ Failed to install Midori via fallback. You can install it manually later.")

    @staticmethod
    def installQbit():
        subprocess.run(["sudo", "apt", "update", "-y"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "qbittorrent"], check=False)
        print("✅ Qbittorrent Installed")

    @staticmethod
    def changewall():
        wallpaper_url = "https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg"
        wallpaper_file = "/tmp/xfce-verticals.png"
        subprocess.run(["wget", "-q", "-O", wallpaper_file, wallpaper_url], check=False)
        dst = "/usr/share/backgrounds/xfce/"
        try:
            subprocess.run(["sudo", "mkdir", "-p", dst], check=False)
            subprocess.run(["sudo", "cp", wallpaper_file, dst], check=False)
            subprocess.run(["sudo", "chown", "root:root", os.path.join(dst, os.path.basename(wallpaper_file))], check=False)
            print("✅ Wallpaper Changed")
        except Exception as e:
            print(f"⚠️ Could not copy wallpaper: {e}")

    @staticmethod
    def finish(user):
        if Autostart:
            autostart_dir = f"/home/{user}/.config/autostart"
            subprocess.run(["sudo", "mkdir", "-p", autostart_dir], check=False)
            link = "https://www.youtube.com/@LacDev-db2vx"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
            tmp_file = f"/tmp/colab_{user}.desktop"
            with open(tmp_file, "w") as f:
                f.write(colab_autostart)
            subprocess.run(["sudo", "mv", tmp_file, f"{autostart_dir}/colab.desktop"], check=False)
            subprocess.run(["sudo", "chmod", "+x", f"{autostart_dir}/colab.desktop"], check=False)
            subprocess.run(["sudo", "chown", "-R", f"{user}:{user}", f"/home/{user}/.config"], check=False)

        subprocess.run(["sudo", "adduser", user, "chrome-remote-desktop"], check=False)

        command = f"{CRD_SSH_Code} --pin={Pin}"
        subprocess.run(["sudo", "su", "-", user, "-c", command], check=False)
        subprocess.run(["sudo", "service", "chrome-remote-desktop", "start"], check=False)

        print("====================================================")
        print("✅ Setup Complete")
        print("User:", username)
        print("Pass:", password)
        print("PIN:", Pin)
        print("====================================================")

        while True:
            pass


try:
    if CRD_SSH_Code == "":
        print("⚠️ Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("⚠️ Enter a pin with 6 or more digits")
    else:
        CRDSetup(username)
except NameError:
    print("⚠️ 'username' variable not found, create a user first")
