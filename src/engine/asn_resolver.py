import urllib.request
import json
import socket
import re

# Local cache dictionary to prevent redundant internet lookups
_asn_cache = {
    "127.0.0.1": ("AS-LOCAL", "Loopback"),
    "10.0.0.1": ("AS263870", "Webstorage"),
    "192.168.0.22": ("AS-LOCAL", "walker (LAN)"),
    "192.168.0.106": ("AS-LOCAL", "RouterBoard (LAN)"),
    "192.168.0.101": ("AS-LOCAL", "papaimach (LAN)"),
    "192.168.0.104": ("AS-LOCAL", "TP-Link AP (LAN)")
}

def resolve_asn_and_org(ip):
    # Check cache first
    if ip in _asn_cache:
        return _asn_cache[ip]
    
    # Exclude private IP ranges
    if (ip.startswith("10.") or 
        ip.startswith("192.168.") or 
        (ip.startswith("172.") and len(ip.split(".")) > 1 and 16 <= int(ip.split(".")[1]) <= 31)):
        return ("AS-LOCAL", "Rede Local")

    try:
        req = urllib.request.Request(
            f"https://rdap.lacnic.net/rdap/ip/{ip}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        # Follow redirects, set timeout to 2 seconds to not block UI
        with urllib.request.urlopen(req, timeout=2.0) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))
            
            # Extract ASN
            asn = ""
            if "nicbr_autnum" in data:
                asn = f"AS{data['nicbr_autnum']}"
            elif "originAutnums" in data and data["originAutnums"]:
                asn = f"AS{data['originAutnums'][0]}"
            else:
                # Look for aut-num in entities
                for entity in data.get("entities", []):
                    handle = entity.get("handle", "")
                    if "aut-num" in handle.lower() or "as" in handle.lower():
                        # Extract digit using regex
                        m = re.search(r'\d+', handle)
                        if m:
                            asn = f"AS{m.group(0)}"
                            break
            
            # Extract Org Name
            org = ""
            for entity in data.get("entities", []):
                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1:
                    for field in vcard[1]:
                        if field[0] == "fn":
                            org = field[3]
                            break
                if org:
                    break
            
            if not org:
                # Try handle name
                for entity in data.get("entities", []):
                    org = entity.get("handle", "")
                    if org:
                        break
            
            if not asn:
                asn = "AS-UNKNOWN"
            if not org:
                org = "Desconhecido"
                
            res = (asn, org)
            _asn_cache[ip] = res
            return res
    except Exception as e:
        # Fallback to reverse DNS or empty values
        try:
            name, _, _ = socket.gethostbyaddr(ip)
            res = ("AS-UNKNOWN", name)
        except Exception:
            res = ("AS-UNKNOWN", "Roteador")
        _asn_cache[ip] = res
        return res
