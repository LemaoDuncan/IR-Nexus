import random, uuid, datetime

TEMPLATES = {
    "ransomware_v1": {
        "id": "ransomware_v1",
        "name": "Ransomware on File Server",
        "description": "Files encrypted on a fileshare, suspicious process, possible beaconing.",
        "category": "endpoint",
        "indicators": ["suspicious-process", "mass-file-mod", "dns-beacon"],
        "brief": "Users report encrypted files and ransom notes on a shared drive.",
        "playbook": {
            "goals": [
                "Find patient zero host and account.",
                "Contain encryption activity.",
                "Identify initial infection vector."
            ],
            "key_actions": [
                "Isolate affected hosts.",
                "Kill ransomware process.",
                "Block C2 domain/IP."
            ]
        },
        "rubric": {"detection": 25, "containment": 25, "eradication": 20, "recovery": 15, "reporting": 15}
    },
    "phishing_bec": {
        "id": "phishing_bec",
        "name": "Phishing / BEC",
        "description": "Mailbox rule abuse and external forwarding.",
        "category": "identity",
        "indicators": ["phish-email", "suspicious-login", "mailbox-rule"],
        "brief": "Finance reports suspicious invoices being sent from an executive mailbox.",
        "playbook": {
            "goals": [
                "Confirm account compromise.",
                "Remove malicious mailbox rules.",
                "Review mail logs for exfil."
            ],
            "key_actions": [
                "Reset password and revoke sessions.",
                "Remove inbox/forward rules.",
                "Search for similar activity in other VIPs."
            ]
        },
        "rubric": {"detection": 25, "containment": 25, "eradication": 15, "recovery": 10, "reporting": 25}
    },
    "ssh_bruteforce": {
        "id": "ssh_bruteforce",
        "name": "SSH Brute Force and Lateral Move",
        "description": "SSH brute force followed by successful login and lateral activity.",
        "category": "network",
        "indicators": ["failed-auth", "suspicious-ssh"],
        "brief": "SOC notices a spike in SSH failures from a single external IP.",
        "playbook": {
            "goals": [
                "Identify attacker IP and target host.",
                "Confirm compromise and lateral activity.",
                "Contain affected systems."
            ],
            "key_actions": [
                "Block attacker IP at firewall.",
                "Isolate jump host.",
                "Reset affected credentials."
            ]
        },
        "rubric": {"detection": 25, "containment": 25, "eradication": 15, "recovery": 10, "reporting": 25}
    },
    "cloud_abuse": {
        "id": "cloud_abuse",
        "name": "Cloud Credential Abuse",
        "description": "Stolen cloud key used for S3 downloads and IAM changes.",
        "category": "cloud",
        "indicators": ["suspicious-api", "s3-download", "iam-changes"],
        "brief": "Cloud monitoring flags unusual API calls and S3 access patterns.",
        "playbook": {
            "goals": [
                "Identify abused IAM principal.",
                "List resources accessed.",
                "Remove persistence and rogue keys."
            ],
            "key_actions": [
                "Disable compromised keys.",
                "Review CloudTrail logs.",
                "Remove suspicious IAM policies/users."
            ]
        },
        "rubric": {"detection": 25, "containment": 25, "eradication": 20, "recovery": 10, "reporting": 20}
    },
    "sqli_exfil": {
        "id": "sqli_exfil",
        "name": "SQL Injection and Data Leak",
        "description": "Web app exploited to dump database via HTTP.",
        "category": "app",
        "indicators": ["sqli", "db-errors", "exfil-http"],
        "brief": "Web logs show SQL errors near login and large HTTP responses.",
        "playbook": {
            "goals": [
                "Confirm SQLi pattern.",
                "Assess possible data leakage.",
                "Coordinate patch or WAF rules."
            ],
            "key_actions": [
                "Block attacker IP/user-agent.",
                "Capture relevant HTTP logs.",
                "Work with devs to patch query."
            ]
        },
        "rubric": {"detection": 25, "containment": 20, "eradication": 20, "recovery": 10, "reporting": 25}
    },
    "insider_exfil": {
        "id": "insider_exfil",
        "name": "Insider Data Exfiltration",
        "description": "Internal user downloading sensitive data and using USB/cloud storage.",
        "category": "insider",
        "indicators": ["unusual-access", "usb-activity", "cloud-upload"],
        "brief": "DLP alerts show HR user copying files to USB and cloud drive.",
        "playbook": {
            "goals": [
                "Confirm malicious vs sanctioned activity.",
                "Quantify data accessed and exfiltrated.",
                "Coordinate with HR/legal."
            ],
            "key_actions": [
                "Review DLP and access logs.",
                "Engage HR/legal with factual summary.",
                "Suspend or restrict account if needed."
            ]
        },
        "rubric": {"detection": 20, "containment": 20, "eradication": 15, "recovery": 10, "reporting": 35}
    }
}

def list_scenarios():
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "category": t["category"]
        }
        for t in TEMPLATES.values()
    ]

def generate_scenario(name, difficulty="medium"):
    if name not in TEMPLATES:
        name = "ransomware_v1"
    base = dict(TEMPLATES[name])
    base["instance_id"] = str(uuid.uuid4())
    base["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    base["hosts"] = [f"host-{i}" for i in range(1, 5)]
    base["users"] = ["alice", "bob", "charlie", "dana"]
    base["ips"] = ["10.0.0.10", "10.0.0.11", "10.0.0.12", "10.0.0.13"]
    base["difficulty"] = difficulty
    return base
