#!/bin/bash

# --- Cấu hình cơ bản ---
read -p "Google CRD SSH Code: " CRD_SSH_Code
USERNAME="user"
PASSWORD="root"
PIN="123456"
AUTOSTART=true

# --- Tạo user ---
echo "[*] Creating user..."
sudo useradd -m "$USERNAME"
sudo adduser "$USERNAME" sudo
echo "${USERNAME}:${PASSWORD}" | sudo chpasswd
sudo sed -i 's#/bin/sh#/bin/bash#g' /etc/passwd

# --- Hàm tiện ích ---
install_crd() {
    echo "[*] Installing Chrome Remote Desktop..."
    sudo apt update -y
    wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
    sudo dpkg --install chrome-remote-desktop_current_amd64.deb
    sudo apt install -y --fix-broken
    echo "✅ Chrome Remote Desktop Installed"
}

install_desktop_env() {
    echo "[*] Installing XFCE4 Desktop Environment..."
    export DEBIAN_FRONTEND=noninteractive
    sudo apt install -y xfce4 desktop-base xfce4-terminal
    echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" | sudo tee /etc/chrome-remote-desktop-session >/dev/null
    sudo apt remove -y gnome-terminal
    sudo apt install -y xscreensaver
    sudo apt purge -y light-locker
    sudo apt install --reinstall -y xfce4-screensaver
    sudo systemctl disable lightdm.service
    echo "✅ XFCE4 Installed"
}

install_google_chrome() {
    echo "[*] Installing Google Chrome..."
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg --install google-chrome-stable_current_amd64.deb
    sudo apt install -y --fix-broken
    echo "✅ Google Chrome Installed"
}

install_midori() {
    echo "[*] Installing Midori (lightweight browser)..."
    sudo apt update -y
    sudo apt install -y midori && echo "✅ Midori installed via apt" && return

    echo "[*] Midori not found in apt, trying fallback..."
    TMP_DEB="/tmp/midori-latest.deb"
    wget -O "$TMP_DEB" https://astian.org/midori-browser/download/debian/amd64/midori-latest.deb && \
    sudo dpkg --install "$TMP_DEB" && \
    sudo apt install -y --fix-broken && \
    echo "✅ Midori installed via fallback" || \
    echo "⚠️ Failed to install Midori."
}

install_qbittorrent() {
    echo "[*] Installing Qbittorrent..."
    sudo apt update -y
    sudo apt install -y qbittorrent
    echo "✅ Qbittorrent Installed"
}

change_wallpaper() {
    echo "[*] Changing wallpaper..."
    WALL_URL="https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg"
    WALL_FILE="/tmp/xfce-wall.png"
    wget -q -O "$WALL_FILE" "$WALL_URL"
    DST="/usr/share/backgrounds/xfce/"
    sudo mkdir -p "$DST"
    sudo cp "$WALL_FILE" "$DST"
    sudo chown root:root "${DST}/$(basename "$WALL_FILE")"
    echo "✅ Wallpaper Changed"
}

finish_setup() {
    echo "[*] Finishing setup..."

    if [ "$AUTOSTART" = true ]; then
        AUTOSTART_DIR="/home/${USERNAME}/.config/autostart"
        sudo mkdir -p "$AUTOSTART_DIR"
        LINK="https://www.youtube.com/@LacDev-db2vx"
        DESKTOP_FILE="/tmp/colab_${USERNAME}.desktop"
        cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser ${LINK}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true
EOF
        sudo mv "$DESKTOP_FILE" "${AUTOSTART_DIR}/colab.desktop"
        sudo chmod +x "${AUTOSTART_DIR}/colab.desktop"
        sudo chown -R "${USERNAME}:${USERNAME}" "/home/${USERNAME}/.config"
    fi

    sudo adduser "$USERNAME" chrome-remote-desktop

    echo "[*] Linking CRD Auth Code..."
    sudo su - "$USERNAME" -c "${CRD_SSH_Code} --pin=${PIN}"
    sudo service chrome-remote-desktop start

    echo "===================================================="
    echo "✅ Setup Complete"
    echo "User: ${USERNAME}"
    echo "Pass: ${PASSWORD}"
    echo "PIN: ${PIN}"
    echo "Autostart link: https://www.youtube.com/@LacDev-db2vx"
    echo "===================================================="

    # Giữ tiến trình hoạt động
    while true; do sleep 3600; done
}

# --- Main ---
if [ -z "$CRD_SSH_Code" ]; then
    echo "⚠️ Please enter authcode from the given link"
    exit 1
fi

if [ ${#PIN} -lt 6 ]; then
    echo "⚠️ Enter a PIN with 6 or more digits"
    exit 1
fi

install_crd
install_desktop_env
change_wallpaper
install_google_chrome
install_midori
install_qbittorrent
finish_setup
