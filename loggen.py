import datetime, random

def _ts(base, offset_sec):
    return (base + datetime.timedelta(seconds=offset_sec)).isoformat() + "Z"

def _noise_windows(host, user, t):
    events = []
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "Windows",
        "host": host,
        "user": user,
        "event": "4624",
        "message": "An account was successfully logged on."
    })
    t[1] += random.randint(10, 60)
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "Windows",
        "host": host,
        "user": user,
        "event": "4689",
        "message": "A process has exited."
    })
    t[1] += random.randint(5, 40)
    return events

def _noise_linux(host, user, t):
    events = []
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "Linux",
        "host": host,
        "user": user,
        "event": "CRON",
        "message": "CRON[1234]: (root) CMD (/usr/local/bin/backup.sh)"
    })
    t[1] += random.randint(60, 300)
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "Linux",
        "host": host,
        "user": user,
        "event": "SYSLOG",
        "message": "systemd[1]: Finished Daily apt download activities."
    })
    t[1] += random.randint(30, 180)
    return events

def _noise_web(host, t):
    events = []
    ip = f"192.0.2.{random.randint(10,200)}"
    path = random.choice(["/index.html", "/api/health", "/login", "/static/js/app.js"])
    code = random.choice([200, 200, 200, 302, 404])
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "Web",
        "host": host,
        "user": "-",
        "event": "HTTP",
        "message": f'{ip} - - "GET {path} HTTP/1.1" {code} 1024'
    })
    t[1] += random.randint(1, 15)
    return events

def _noise_cloud(t):
    events = []
    acct = random.choice(["app-role", "lambda-fn", "backup-service"])
    events.append({
        "time": _ts(t[0], t[1]),
        "source": "CloudTrail",
        "host": "aws",
        "user": acct,
        "event": "DescribeInstances",
        "message": "DescribeInstances call completed successfully."
    })
    t[1] += random.randint(60, 300)
    return events

def generate_logs(scenario):
    sid = scenario.get("id")
    hosts = scenario.get("hosts", ["host-1","host-2","host-3"])
    users = scenario.get("users", ["alice","bob","charlie"])
    difficulty = scenario.get("difficulty","medium")

    if difficulty == "easy":
        target = random.randint(80, 150)
    elif difficulty == "hard":
        target = random.randint(400, 600)
    else:
        target = random.randint(200, 350)

    base_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    t = [base_time, 0]

    logs = []

    # 1) Background noise
    while len(logs) < int(target * 0.4):
        h = random.choice(hosts)
        u = random.choice(users)
        logs.extend(_noise_windows(h, u, t))
        logs.extend(_noise_linux(h, u, t))
        logs.extend(_noise_web(h, t))
        if "cloud" in sid or "cloud" in scenario.get("category",""):
            logs.extend(_noise_cloud(t))

    def add(ev):
        logs.append(ev)

    # 2) Attack chains
    if sid.startswith("ransomware"):
        patient = hosts[0]
        user = users[0]
        add({"time": _ts(base_time, 60),"source": "Mail","host": "mail","user": user,
             "event": "EMAIL_OPEN","message": "Opened invoice_2025.xlsm from external sender."})
        add({"time": _ts(base_time, 120),"source": "Windows","host": patient,"user": user,
             "event": "4688","message": "Process created: powershell.exe -nop -w hidden -enc ..."})
        add({"time": _ts(base_time, 180),"source": "Windows","host": patient,"user": user,
             "event": "4688","message": "Process created: evilcrypt.exe"})
        for i in range(50):
            add({"time": _ts(base_time, 200 + i*3),"source": "FS","host": patient,"user": user,
                 "event": "FILE_MOD","message": f"Modified \\fileserver\\Dept\\doc_{i}.docx"})
        add({"time": _ts(base_time, 200 + 50*3),"source": "DNS","host": patient,"user": "-",
             "event": "QUERY","message": "Query rare-domain.com"})
    elif sid == "phishing_bec":
        exec_user = users[1]
        add({"time": _ts(base_time, 60),"source": "Mail","host": "mail","user": exec_user,
             "event": "EMAIL_OPEN","message": "Opened 'Urgent Invoice' from billing@fake-invoice.biz"})
        add({"time": _ts(base_time, 90),"source": "Web","host": hosts[1],"user": exec_user,
             "event": "HTTP","message": 'Visited http://phish.example/login "200"'})
        add({"time": _ts(base_time, 120),"source": "Auth","host": "idp","user": exec_user,
             "event": "LOGIN","message": "Successful login from 203.0.113.50 (new country)"})
        add({"time": _ts(base_time, 150),"source": "Mail","host": "mail","user": exec_user,
             "event": "RULE","message": "Outlook rule added: move all to Archive and mark read"})
        for i in range(20):
            add({"time": _ts(base_time, 200 + i*5),"source": "Mail","host": "mail","user": exec_user,
                 "event": "FORWARD","message": f"Forwarded payroll_{i}.xlsx to external address"})
    elif sid == "ssh_bruteforce":
        jump = hosts[1]
        attacker_ip = "203.0.113.77"
        for i in range(50):
            add({"time": _ts(base_time, 30 + i*3),"source": "SSH","host": jump,"user": "invalid",
                 "event": "FAIL","message": f"Failed password for invalid user test from {attacker_ip} port {52000+i} ssh2"})
        add({"time": _ts(base_time, 30 + 50*3),"source": "SSH","host": jump,"user": "charlie",
             "event": "SUCCESS","message": f"Accepted password for charlie from {attacker_ip} port 53001 ssh2"})
        add({"time": _ts(base_time, 30 + 50*3 + 60),"source": "SSH","host": jump,"user": "charlie",
             "event": "CMD","message": "Executed: ssh host-3"})
    elif sid == "cloud_abuse":
        add({"time": _ts(base_time, 60),"source": "CloudTrail","host": "aws","user": "legacy-admin",
             "event": "ConsoleLogin","message": "Console login from 198.51.100.99; MFA not present."})
        add({"time": _ts(base_time, 120),"source": "CloudTrail","host": "aws","user": "legacy-admin",
             "event": "CreateAccessKey","message": "New access key created for legacy-admin"})
        for i in range(10):
            add({"time": _ts(base_time, 180 + i*20),"source": "CloudTrail","host": "aws","user": "legacy-admin",
                 "event": "GetObject","message": f"Downloaded s3://corp-data/hr/comp_{i}.xlsx"})
        add({"time": _ts(base_time, 180 + 10*20),"source": "CloudTrail","host": "aws","user": "legacy-admin",
             "event": "AttachUserPolicy","message": "Attached AdministratorAccess policy"})
    elif sid == "sqli_exfil":
        web = hosts[0]
        attacker_ip = "192.0.2.50"
        for i in range(30):
            payload = random.choice([
                "/login?user=admin%27--",
                "/search?q=1%27 OR 1=1--",
                "/product?id=5 UNION SELECT username,password FROM users--"
            ])
            code = random.choice([500, 500, 200])
            size = random.choice([1024, 2048, 8192, 16384])
            add({"time": _ts(base_time, 30 + i*4),"source": "Web","host": web,"user": "-",
                 "event": "HTTP","message": f'{attacker_ip} - - "GET {payload} HTTP/1.1" {code} {size}'})
    elif sid == "insider_exfil":
        host = hosts[2]
        user = "hr-user"
        add({"time": _ts(base_time, 60),"source": "DLP","host": host,"user": user,
             "event": "COPY","message": "Copied HR_Compensation_2025.xlsx to USB device VID_0951&PID_1666"})
        add({"time": _ts(base_time, 120),"source": "DLP","host": host,"user": user,
             "event": "UPLOAD","message": "Uploaded HR_Employees_All.csv to https://www.dropbox.com/home"})
        for i in range(10):
            add({"time": _ts(base_time, 180 + i*10),"source": "DLP","host": host,"user": user,
                 "event": "ACCESS","message": f"Opened HR file HR_Employee_Record_{i}.xlsx"})

    # 3) More noise until target
    while len(logs) < target:
        h = random.choice(hosts)
        u = random.choice(users)
        src = random.choice(["win","lin","web","cloud"])
        if src == "win":
            logs.extend(_noise_windows(h, u, t))
        elif src == "lin":
            logs.extend(_noise_linux(h, u, t))
        elif src == "web":
            logs.extend(_noise_web(h, t))
        else:
            logs.extend(_noise_cloud(t))

    logs = logs[:target]
    logs.sort(key=lambda x: x.get("time",""))
    return logs
