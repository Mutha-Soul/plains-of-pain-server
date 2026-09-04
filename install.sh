#!/usr/bin/env bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run this installer as root."
  exit 1
fi

echo "[+] Installing system dependencies for Debian 13..."
dpkg --add-architecture i386
apt update -y
apt install -y curl wget tar bzip2 gzip unzip python3 python3-pip python3-psutil \
  lib32gcc-s1 lib32stdc++6 libc6-i386 libstdc++6:i386 lib32z1 python3-flask python3-waitress conntrack

# KCP UDP kernel buffer optimization
echo "[+] Applying KCP UDP kernel optimizations..."
cat << 'SYSCTL_EOF' > /etc/sysctl.d/99-kcp-tuning.conf
net.core.rmem_max=26214400
net.core.rmem_default=26214400
net.core.wmem_max=26214400
net.core.wmem_default=26214400
SYSCTL_EOF
sysctl --system >/dev/null 2>&1 || true

# Setup steam user
if ! id -u steam >/dev/null 2>&1; then
    echo "[+] Creating steam system user..."
    useradd -m -s /bin/bash steam
fi

# Install SteamCMD
echo "[+] Setting up SteamCMD..."
mkdir -p /home/steam/SteamCMD
cd /home/steam/SteamCMD
if [ ! -f "steamcmd.sh" ]; then
    curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -
fi
chown -R steam:steam /home/steam/SteamCMD

# Deploy CLI tool
echo "[+] Deploying pop CLI..."
cp bin/pop /usr/local/bin/pop
chmod +x /usr/local/bin/pop

# Deploy Web Panel
echo "[+] Deploying Web Dashboard to /opt/pop-web..."
mkdir -p /opt/pop-web
cp -r web/* /opt/pop-web/
chown -R root:root /opt/pop-web

# Deploy Systemd Services
echo "[+] Installing systemd services..."
cp systemd/pop-server.service /etc/systemd/system/pop-server.service
cp systemd/pop-web.service /etc/systemd/system/pop-web.service
systemctl daemon-reload

systemctl enable pop-server.service
systemctl enable pop-web.service
systemctl restart pop-web.service

echo ""
echo "=========================================================="
echo " Plains of Pain Server & Panel installed successfully!"
echo " Web Control Panel: http://YOUR_SERVER_IP:8080"
echo " Run 'pop update' to install the dedicated game server."
echo "=========================================================="
