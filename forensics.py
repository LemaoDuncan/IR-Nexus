def base_artifacts():
    return {
        "process_list": [
            {"pid": 412, "name": "explorer.exe", "user": "alice"},
            {"pid": 733, "name": "svchost.exe", "user": "SYSTEM"}
        ],
        "netstat": [
            {"proto": "TCP", "local": "10.0.0.10:49832", "remote": "52.34.22.10:443", "state": "ESTABLISHED"}
        ]
    }

def ransomware_artifacts():
    a = base_artifacts()
    a["process_list"].append({"pid": 999, "name": "evilcrypt.exe", "user": "alice", "note": "suspected ransomware"})
    a["registry"] = [
        {"path": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
         "value": "evilcrypt", "data": "C:\\ProgramData\\evilcrypt.exe"}
    ]
    return a

def phishing_artifacts():
    a = base_artifacts()
    a["mailbox_rules"] = [
        {"name": "Move all to Archive", "condition": "all messages", "action": "move to Archive"}
    ]
    a["recent_emails"] = [
        {"subject": "Invoice overdue", "from": "billing@fake-invoice.biz"},
        {"subject": "Password reset", "from": "it-support@corp.example"}
    ]
    return a

def ssh_artifacts():
    a = base_artifacts()
    a["auth_log"] = [
        "Failed password for invalid user test from 203.0.113.77 port 52212 ssh2",
        "Accepted password for charlie from 203.0.113.77 port 52301 ssh2"
    ]
    a["bash_history"] = ["whoami", "ls /home", "ssh host-3"]
    return a

def cloud_artifacts():
    return {
        "cloudtrail": [
            {"event": "CreateAccessKey", "user": "legacy-admin", "ip": "198.51.100.99"},
            {"event": "GetObject", "resource": "s3://corp-data/hr/compensation.xlsx", "ip": "198.51.100.99"}
        ],
        "iam_changes": [
            {"change": "Attached AdministratorAccess to user legacy-admin"}
        ]
    }

def sqli_artifacts():
    return {
        "web_logs": [
            '192.0.2.50 - - "GET /login?user=admin%27-- HTTP/1.1" 500 -',
            '192.0.2.50 - - "GET /search?q=1%27 OR 1=1-- HTTP/1.1" 200 10240'
        ],
        "db_logs": [
            "ERROR: syntax error at or near "OR"",
            "SELECT * FROM customers WHERE id = '1' OR 1=1--"
        ]
    }

def insider_artifacts():
    return {
        "dlp_events": [
            {"user": "hr-user", "file": "HR_Compensation_2025.xlsx", "dest": "USB", "action": "copied"},
            {"user": "hr-user", "file": "HR_Employees_All.csv", "dest": "dropbox.com", "action": "uploaded"}
        ],
        "endpoint_logs": [
            "USB device VID_0951&PID_1666 mounted as E:\\",
            "Browser visited https://www.dropbox.com/home"
        ]
    }

def get_artifacts_for_scenario(scenario):
    sid = scenario.get("id")
    if sid and sid.startswith("ransomware"):
        return ransomware_artifacts()
    if sid == "phishing_bec":
        return phishing_artifacts()
    if sid == "ssh_bruteforce":
        return ssh_artifacts()
    if sid == "cloud_abuse":
        return cloud_artifacts()
    if sid == "sqli_exfil":
        return sqli_artifacts()
    if sid == "insider_exfil":
        return insider_artifacts()
    return base_artifacts()
