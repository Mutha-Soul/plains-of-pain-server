# Plains of Pain Dedicated Server & Web Management Bundle

A turnkey deployment toolkit, CLI management tool, and lightweight web dashboard for running high-performance **Plains of Pain** dedicated servers on Linux.

* **Upstream Game Spec**: Cobra Byte Digital Linux Setup (v0.8.20 / Aug 30, 2026)
* **Author**: Mutha Soul ([Twitch](https://www.twitch.tv/mutha_soul) | [Discord](https://discord.com/channels/1100571874322305104/1545430461235601459) | [GitHub](https://github.com/Mutha-Soul))
* **Co-Engineered With**: GoBot (Gemini)
* **License**: MIT

---

# Plains of Pain Dedicated Server & Web Management Bundle

![Dashboard Preview](assets/dashboard-preview.png)

A turnkey deployment toolkit, CLI management tool, and lightweight web dashboard for running high-performance **Plains of Pain** dedicated servers on Linux.

---

## 🖥️ Operating System Support

* **Target OS**: **Debian 13 (Trixie)** — Fully tested and optimized.
* **Compatible Distributions**: Debian 12 (Bookworm), Ubuntu 24.04 LTS, Ubuntu 22.04 LTS.
* **Architecture**: x86_64 (64-bit) with 32-bit multiarch enabled for SteamCMD.

---

## ⚙️ Hardware & Network Requirements

Based on official performance specifications from Cobra Byte Digital[cite: 2]:

| Player Capacity | Recommended CPU | Recommended RAM | Free Disk Space |
| :--- | :--- | :--- | :--- |
| **10 Players** | 2 vCPUs[cite: 2] | 4 GB[cite: 2] | 500 MB+ (SSD)[cite: 2] |
| **50 Players** | 4–6 vCPUs[cite: 2] | 8 GB[cite: 2] | 1 GB+ (SSD) |
| **100 Players** | 8–12 vCPUs[cite: 2] | 16 GB[cite: 2] | 2 GB+ (SSD) |
| **200 Players** | 16 vCPUs[cite: 2] | 32 GB[cite: 2] | 5 GB+ (SSD) |

* **Bandwidth**: 50–250 kbps upstream per connected player[cite: 2].
* **UDP 7777**: Game transport port (KCP)[cite: 2].
* **UDP 27016**: Steam query port (Server list indexing)[cite: 2].
* **TCP 8080**: Web dashboard port (HTTP).

---

## 🚀 Quick Start

Run as root on a fresh Debian 13 server:

```bash
git clone [https://github.com/Mutha-Soul/plains-of-pain-server.git](https://github.com/Mutha-Soul/plains-of-pain-server.git)
cd plains-of-pain-server
chmod +x install.sh
./install.sh
pop update

Access the web control panel at http://YOUR_SERVER_IP:8080 (Default credentials: admin / ChangeMeNow123!).

🛠️ CLI Management (pop)
pop start — Starts the game server service.

pop stop — Gracefully stops the game server.

pop restart — Restarts the server.

pop status — Displays real-time Systemd service telemetry.

pop update — Updates or validates game files via SteamCMD (AppID: 2227360)[cite: 2].

pop clean — Purges stale SteamCMD appcache locks.

pop wipe — Permanently purges custom world save data to generate a fresh map.

🔍 Pre-Flight Diagnostics (Run Before Asking For Help)
If you run into issues, run this one-line command in your VPS terminal:

Bash
echo "=== POP DIAGNOSTICS ===" && \
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)" && \
echo "Panel Service: $(systemctl is-active pop-web.service)" && \
echo "Server Service: $(systemctl is-active pop-server.service)" && \
echo "Listening Ports:" && ss -ulpn '( sport = :7777 or sport = :27016 )' && \
echo "KCP Buffers:" && sysctl net.core.rmem_max net.core.wmem_max && \
echo "Recent Server Log:" && tail -n 15 /home/steam/Steam/steamapps/common/PlainsOfPainServer/server.log
🗺️ Future Roadmap
Live Player Session Table: Real-time connected player tracking.

In-Game Moderation & RCON: Kick, ban, and server announcements from the web dashboard.

Automated Map Backups: One-click world saves and restores.

🆘 Where to Get Help
Panel or Installer Issues: Ask on Mutha Soul Discord or open a GitHub Issue.

Linux / VPS Hosting Issues: Use Debian community forums or contact your server provider.

In-Game Bugs: Report to Cobra Byte Digital on Steam.
