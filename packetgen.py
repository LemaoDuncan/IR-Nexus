import datetime, random

def _ts(base, offset):
    return (base + datetime.timedelta(seconds=offset)).isoformat() + "Z"

def generate_packets(scenario):
    sid = scenario.get("id")
    ips = scenario.get("ips", ["10.0.0.10","10.0.0.11"])
    difficulty = scenario.get("difficulty","medium")

    if difficulty == "easy":
        target = random.randint(80, 150)
    elif difficulty == "hard":
        target = random.randint(350, 600)
    else:
        target = random.randint(200, 350)

    base_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    packets = []

    def add(pkt):
        packets.append(pkt)

    # background traffic
    for i in range(int(target * 0.6)):
        src = random.choice(ips)
        dst = f"192.0.2.{random.randint(10,200)}"
        proto = random.choice(["TCP","UDP","HTTP","DNS"])
        pkt = {
            "time": _ts(base_time, i*3),
            "src_ip": src,
            "dst_ip": dst,
            "proto": proto,
            "length": random.randint(64, 1500),
            "info": "benign traffic"
        }
        add(pkt)

    # scenario-specific network traces
    if sid.startswith("ransomware"):
        for i in range(10):
            add({
                "time": _ts(base_time, 60 + i*60),
                "src_ip": ips[0],
                "dst_ip": "198.51.100.45",
                "proto": "DNS",
                "length": 120,
                "info": f"Query rare-domain.com type A (beacon {i})"
            })
    elif sid == "phishing_bec":
        for i in range(15):
            add({
                "time": _ts(base_time, 90 + i*30),
                "src_ip": "10.0.0.25",
                "dst_ip": "198.51.100.200",
                "proto": "SMTP",
                "length": random.randint(400,2000),
                "info": "Suspicious outbound email with attachment"
            })
    elif sid == "ssh_bruteforce":
        attacker_ip = "203.0.113.77"
        jump = ips[1] if len(ips) > 1 else ips[0]
        for i in range(60):
            add({
                "time": _ts(base_time, 30 + i*5),
                "src_ip": attacker_ip,
                "dst_ip": jump,
                "proto": "TCP",
                "length": 74,
                "info": "SSH tcp-syn"
            })
    elif sid == "cloud_abuse":
        for i in range(20):
            add({
                "time": _ts(base_time, 60 + i*60),
                "src_ip": "198.51.100.99",
                "dst_ip": "52.95.245.0",
                "proto": "HTTPS",
                "length": random.randint(800,4000),
                "info": "AWS S3 GetObject"
            })
    elif sid == "sqli_exfil":
        attacker_ip = "192.0.2.50"
        web = ips[0]
        for i in range(25):
            add({
                "time": _ts(base_time, 45 + i*10),
                "src_ip": attacker_ip,
                "dst_ip": web,
                "proto": "HTTP",
                "length": random.randint(2000,16000),
                "info": "SQLi-style HTTP request/response"
            })
    elif sid == "insider_exfil":
        host = ips[-1]
        add({
            "time": _ts(base_time, 120),
            "src_ip": host,
            "dst_ip": "162.125.4.1",
            "proto": "HTTPS",
            "length": random.randint(3000,10000),
            "info": "Upload to cloud storage provider"
        })

    packets = packets[:target]
    packets.sort(key=lambda p: p.get("time",""))
    return packets
