import subprocess
import psutil
import json
import shutil
import os
from flask import Flask, render_template_string, request, Response, send_from_directory, jsonify, make_response, redirect

app = Flask(__name__)

USER = "admin"
PASSWORD = "ChangeMeNow123!"

INSTALL_DIR = "/home/steam/Steam/steamapps/common/PlainsOfPainServer"
CONFIG_PATH = f"{INSTALL_DIR}/configs/my_server.json"
LOG_PATH = f"{INSTALL_DIR}/server.log"
WORLD_DIR = f"{INSTALL_DIR}/data/custom"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>Plains of Pain Control Panel</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0;
            padding: 30px 20px;
            background: linear-gradient(rgba(18, 14, 8, 0.65), rgba(12, 10, 6, 0.88)), url('/background.jpg') no-repeat center bottom fixed;
            background-size: cover;
            color: #d8cfbe; 
            min-height: 100vh;
            box-sizing: border-box;
        }
        .card { 
            max-width: 860px; 
            margin: auto; 
            background: rgba(18, 16, 12, 0.90); 
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 26px; 
            border-radius: 12px; 
            border: 2px solid #e5a93c;
            box-shadow: 0 0 25px rgba(229, 169, 60, 0.25), 0 12px 40px rgba(0, 0, 0, 0.9); 
        }
        h1 { 
            margin-top: 0; 
            color: #f5b338; 
            font-size: 24px; 
            letter-spacing: 1px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(245, 179, 56, 0.35);
        }
        h3 { 
            margin-top: 20px; 
            margin-bottom: 8px; 
            color: #e5a93c; 
            font-size: 15px; 
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .status { 
            padding: 12px 16px; 
            background: rgba(32, 26, 16, 0.9); 
            border-radius: 6px; 
            font-weight: bold; 
            margin-bottom: 20px; 
            border-left: 4px solid #f5b338;
            color: #f7dfa5;
        }
        .metrics { margin-bottom: 24px; }
        .metric-row { display: flex; align-items: center; margin-bottom: 12px; font-weight: 600; font-size: 14px; }
        .metric-label { width: 90px; text-align: right; padding-right: 14px; color: #ebd5ad; letter-spacing: 0.5px; }
        .bar-container { 
            flex-grow: 1; 
            height: 26px; 
            background: rgba(15, 13, 10, 0.9); 
            border-radius: 6px; 
            position: relative; 
            overflow: hidden; 
            border: 1px solid rgba(229, 169, 60, 0.25); 
        }
        .bar-fill { height: 100%; border-radius: 5px; transition: width 0.4s ease; }
        .bar-fill.cpu { background: linear-gradient(90deg, #3d6880, #5c93b3); }
        .bar-fill.mem { background: linear-gradient(90deg, #606c38, #8f9e58); }
        .bar-text { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); font-size: 12px; color: #fff; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }

        .button-group { margin-bottom: 20px; display: flex; gap: 8px; flex-wrap: wrap; }
        button { 
            border: 1px solid rgba(255, 255, 255, 0.15); 
            padding: 10px 18px; 
            font-weight: 700; 
            font-size: 13px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border-radius: 6px; 
            cursor: pointer; 
            transition: all 0.2s; 
        }
        button:hover { transform: translateY(-1px); filter: brightness(1.15); }
        
        button.start { background: #d48b17; color: #161105; border-color: #f5a623; }
        button.stop { background: #82221b; color: #fce8e6; border-color: #a83228; }
        button.restart { background: #b86214; color: #fff2e0; border-color: #d9781e; }
        button.action-btn { background: #403e3a; color: #f0e6d2; border-color: #595650; }
        button.cache-btn { background: #614624; color: #ffe6bf; border-color: #7d5a2d; }
        button.danger-btn { background: #8f341d; color: #ffe5dd; border-color: #ab4429; }
        button.wipe-btn { background: #a81c1c; color: #ffffff; border-color: #d32f2f; box-shadow: 0 0 10px rgba(168, 28, 28, 0.4); }
        button.save-btn { background: #4e6328; color: #f2f7e4; border-color: #698536; }
        button.exec-btn { background: #e5a93c; color: #161105; border-color: #f5b338; }

        details {
            margin-top: 15px;
            background: rgba(26, 22, 16, 0.7);
            border-radius: 6px;
            padding: 10px 14px;
            border: 1px solid rgba(229, 169, 60, 0.25);
        }
        summary {
            cursor: pointer;
            font-weight: 600;
            color: #e5a93c;
            outline: none;
            text-transform: uppercase;
            font-size: 13px;
            letter-spacing: 0.5px;
        }

        .terminal-window {
            margin-top: 10px;
            background: #0a0907;
            border: 1px solid rgba(229, 169, 60, 0.35);
            border-radius: 6px;
            padding: 12px;
            font-family: 'Consolas', 'Fira Code', monospace;
        }
        .terminal-output {
            height: 250px;
            overflow-y: auto;
            color: #f2c75c;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
            margin-bottom: 10px;
        }
        .terminal-input-row { display: flex; gap: 8px; }
        .terminal-input {
            flex-grow: 1;
            background: rgba(18, 16, 12, 0.95);
            color: #fff;
            border: 1px solid rgba(229, 169, 60, 0.4);
            border-radius: 4px;
            padding: 8px 12px;
            font-family: 'Consolas', 'Fira Code', monospace;
            font-size: 13px;
            outline: none;
        }
        .terminal-input:focus { border-color: #f5b338; }

        textarea.config-box {
            width: 100%;
            height: 220px;
            background: rgba(12, 10, 8, 0.95);
            color: #f2c75c;
            border: 1px solid rgba(229, 169, 60, 0.35);
            border-radius: 6px;
            padding: 12px;
            font-family: 'Consolas', 'Fira Code', monospace;
            font-size: 13px;
            box-sizing: border-box;
            resize: vertical;
            outline: none;
        }
        pre { 
            background: rgba(10, 9, 7, 0.95); 
            color: #a3c47a; 
            padding: 14px; 
            border-radius: 6px; 
            height: 240px; 
            overflow-y: scroll; 
            font-size: 13px; 
            border: 1px solid rgba(229, 169, 60, 0.25); 
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Plains of Pain Server</h1>
        <div class="status" id="server-status">{{ status }}</div>

        <div class="metrics">
            <div class="metric-row">
                <div class="metric-label">CPU:</div>
                <div class="bar-container">
                    <div class="bar-fill cpu" id="cpu-fill" style="width: {{ cpu_pct }}%;"></div>
                    <div class="bar-text" id="cpu-text">{{ cpu_pct }}%</div>
                </div>
            </div>
            <div class="metric-row">
                <div class="metric-label">Memory:</div>
                <div class="bar-container">
                    <div class="bar-fill mem" id="mem-fill" style="width: {{ mem_pct }}%;"></div>
                    <div class="bar-text" id="mem-text">{{ mem_pct }}% ({{ mem_used }})</div>
                </div>
            </div>
        </div>

        <form method="POST" action="/" class="button-group">
            <button name="action" value="start" class="start" type="submit">Start</button>
            <button name="action" value="stop" class="stop" type="submit">Stop</button>
            <button name="action" value="restart" class="restart" type="submit">Restart</button>
            <button name="action" value="update" class="action-btn" type="submit">Update</button>
            <button name="action" value="clear_cache" class="cache-btn" type="submit">Clear Cache</button>
            <button name="action" value="reinstall" class="danger-btn" type="submit" onclick="return confirm('Validate/reinstall server files via SteamCMD?');">Reinstall</button>
            <button name="action" value="wipe_world" class="wipe-btn" type="submit" onclick="return confirm('⚠️ WARNING: This will PERMANENTLY delete all world save data and generate a fresh map. Are you sure?');">Wipe World</button>
        </form>

        <details>
            <summary>💻 Expand Interactive System Shell</summary>
            <div class="terminal-window">
                <div id="term-out" class="terminal-output">[Terminal Initialized. Type any shell command (e.g. pop status, df -h, ls -la)]\n</div>
                <form onsubmit="runShellCmd(event);" class="terminal-input-row">
                    <input type="text" id="term-in" class="terminal-input" placeholder="Type bash command here..." autocomplete="off">
                    <button type="submit" class="exec-btn">Run</button>
                </form>
            </div>
        </details>

        <details>
            <summary>⚙️ Edit Server Configuration (configs/my_server.json)</summary>
            <form method="POST" action="/" style="margin-top: 12px;">
                <textarea name="config_content" class="config-box" spellcheck="false">{{ config_data }}</textarea>
                <div style="margin-top: 10px;">
                    <button name="action" value="save_config" class="save-btn" type="submit">Save & Restart Server</button>
                </div>
            </form>
        </details>

        <h3>Live Server Log (Last 30 Lines)</h3>
        <pre id="server-logs">{{ logs }}</pre>

        <div style="margin-top: 25px; padding-top: 14px; border-top: 1px solid rgba(229, 169, 60, 0.2); text-align: center; font-size: 11px; color: #8c8273; line-height: 1.8;">
            <em>Plains of Pain</em> &copy; Cobra Byte Digital. All rights reserved.<br>
            Crafted by <a href="https://www.twitch.tv/mutha_soul" target="_blank" style="color: #f5b338; text-decoration: none; font-weight: 700;">Mutha Soul</a>
            &bull; Co-Engineered with <strong>GoBot (Gemini)</strong>
            &bull; September 2026<br>
            <a href="https://www.twitch.tv/mutha_soul" target="_blank" style="color: #9146ff; text-decoration: none; margin: 0 6px; font-weight: 600;">[ Twitch ]</a>
            <a href="https://discord.com/channels/1100571874322305104/1545430461235601459" target="_blank" style="color: #5865f2; text-decoration: none; margin: 0 6px; font-weight: 600;">[ Discord ]</a>
            <a href="https://github.com/Mutha-Soul" target="_blank" style="color: #a3c47a; text-decoration: none; margin: 0 6px; font-weight: 600;">[ GitHub ]</a>
        </div>
    </div>

    <script>
        async function runShellCmd(e) {
            e.preventDefault();
            const inp = document.getElementById('term-in');
            const out = document.getElementById('term-out');
            const cmd = inp.value.trim();
            if (!cmd) return;

            out.textContent += '$ ' + cmd + '\\n';
            out.scrollTop = out.scrollHeight;
            inp.value = '';

            try {
                const res = await fetch('/api/terminal', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await res.json();
                out.textContent += data.output + '\\n';
                out.scrollTop = out.scrollHeight;
            } catch(err) {
                out.textContent += '[Error communicating with terminal server]\\n';
            }
        }

        async function updateTelemetry() {
            try {
                const res = await fetch('/api/stats');
                if (!res.ok) return;
                const data = await res.json();

                document.getElementById('server-status').textContent = data.status;
                document.getElementById('cpu-fill').style.width = data.cpu_pct + '%';
                document.getElementById('cpu-text').textContent = data.cpu_pct + '%';
                document.getElementById('mem-fill').style.width = data.mem_pct + '%';
                document.getElementById('mem-text').textContent = data.mem_pct + '% (' + data.mem_used + ')';

                const logBox = document.getElementById('server-logs');
                const wasAtBottom = logBox.scrollHeight - logBox.clientHeight <= logBox.scrollTop + 30;
                logBox.textContent = data.logs;
                if (wasAtBottom) {
                    logBox.scrollTop = logBox.scrollHeight;
                }
            } catch (err) {}
        }

        setInterval(updateTelemetry, 3000);
    </script>
</body>
</html>
"""

def check_auth(username, password):
    return username == USER and password == PASSWORD

def authenticate():
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def clear_steam_cache():
    try:
        subprocess.run(["/usr/local/bin/pop", "stop"])
        for cd in ["/home/steam/.steam/steam/appcache", "/home/steam/.steam/root/appcache", "/home/steam/Steam/appcache"]:
            if os.path.exists(cd):
                shutil.rmtree(cd)
        subprocess.run(["chown", "-R", "steam:steam", "/home/steam"])
        subprocess.run(["/usr/local/bin/pop", "start"])
        return True
    except Exception:
        return False

def wipe_world_data():
    try:
        subprocess.run(["/usr/local/bin/pop", "stop"])
        if os.path.exists(WORLD_DIR):
            shutil.rmtree(WORLD_DIR)
        os.makedirs(WORLD_DIR, exist_ok=True)
        subprocess.run(["chown", "-R", "steam:steam", WORLD_DIR])
        subprocess.run(["/usr/local/bin/pop", "start"])
        return True
    except Exception:
        return False

def read_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        return f"// Error: {str(e)}"

def write_config(content):
    try:
        parsed = json.loads(content)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(parsed, f, indent=2)
        subprocess.run(["chown", "steam:steam", CONFIG_PATH])
        return True
    except Exception:
        return False

def get_stats():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "PlainsOfPain.x86_64"]).decode().split()[-1])
        p = psutil.Process(pid)
        cpu_pct = round(p.cpu_percent(interval=0.1), 1)
        mem_pct = round(p.memory_percent(), 1)
        mem_str = f"{round(p.memory_info().rss / (1024*1024), 1)} MB"
    except Exception:
        cpu_pct, mem_pct, mem_str = 0.0, 0.0, "0 MB"
    return cpu_pct, mem_pct, mem_str

@app.route("/background.jpg")
def background():
    return send_from_directory("/opt/pop-web", "background.jpg")

@app.route("/api/terminal", methods=["POST"])
def api_terminal():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    cmd = (request.get_json() or {}).get("command", "").strip()
    if not cmd:
        return jsonify({"output": ""})

    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15, text=True)
        out = res.stdout
    except Exception as e:
        out = f"Error: {e}"

    return jsonify({"output": out.rstrip()})

@app.route("/api/stats")
def api_stats():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    cpu, mem, mem_s = get_stats()
    return jsonify({
        "status": subprocess.getoutput("/usr/local/bin/pop status"),
        "logs": subprocess.getoutput(f"tail -n 30 {LOG_PATH}"),
        "cpu_pct": cpu,
        "mem_pct": mem,
        "mem_used": mem_s
    })

@app.route("/", methods=["GET", "POST"])
def dashboard():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    if request.method == "POST":
        action = request.form.get("action")
        if action in ["start", "stop", "restart", "update", "reinstall"]:
            subprocess.run(["/usr/local/bin/pop", action])
        elif action == "clear_cache":
            clear_steam_cache()
        elif action == "wipe_world":
            wipe_world_data()
        elif action == "save_config":
            raw_json = request.form.get("config_content", "")
            if write_config(raw_json):
                subprocess.run(["/usr/local/bin/pop", "restart"])
        return redirect("/")

    cpu, mem, mem_s = get_stats()
    rendered = render_template_string(
        HTML_TEMPLATE, 
        status=subprocess.getoutput("/usr/local/bin/pop status"), 
        logs=subprocess.getoutput(f"tail -n 30 {LOG_PATH}"),
        cpu_pct=cpu,
        mem_pct=mem,
        mem_used=mem_s,
        config_data=read_config()
    )
    
    resp = make_response(rendered)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
