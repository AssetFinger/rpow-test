import os
import time
import hashlib
import sys
import json
import signal
import urllib.request
import urllib.error

# --- FITUR DARI SCRIPT BARU: HTTP HELPER STDLIB ---
# Menghilangkan ketergantungan pada cloudscraper agar lebih ringan di Cloud Phone
def http_request(method, path, cookie, body=None):
    url = f"https://api.rpow2.com{path}"
    headers = {
        "Cookie": cookie,
        "Origin": "https://rpow2.com",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return 0, None

# --- FITUR DARI SCRIPT BARU: SUMMARY & SIGNAL HANDLING ---
minted_count = 0
start_time = time.time()

def stop_summary(*_):
    elapsed = time.time() - start_time
    print("\n" + "="*30)
    print("       MINING SUMMARY")
    print("="*30)
    print(f"Total Mined : {minted_count}")
    print(f"Elapsed Time: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    if elapsed > 0:
        rate = (minted_count / elapsed) * 3600
        print(f"Avg Speed   : {rate:.2f} tokens/hour")
    print("="*30)
    sys.exit(0)

# Menangkap sinyal CTRL+C (SIGINT) untuk menampilkan summary
signal.signal(signal.SIGINT, stop_summary)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def solve_pow(prefix, difficulty):
    nonce = 0
    target = 2**(256 - difficulty)
    while True:
        # Optimasi: Menggunakan f-string yang lebih cepat untuk pembuatan preimage
        text = f"{prefix}{nonce}"
        h = hashlib.sha256(text.encode()).hexdigest()
        if int(h, 16) < target:
            return nonce
        nonce += 1
        # Berikan kontrol balik ke loop setiap 500rb hash agar tidak hang
        if nonce % 500000 == 0:
            return None

def start_mining():
    global minted_count
    cookie = os.getenv('RPOW_COOKIE')
    if not cookie:
        print("[-] Error: RPOW_COOKIE belum di-set!")
        return

    clear_screen()
    print("[+] Mining Started... (Press CTRL+C to see summary)")

    while True:
        try:
            # 1. Get Challenge menggunakan HTTP Helper baru
            status, ch = http_request("POST", "/challenge", cookie)
            
            if status == 200 and ch:
                cid = ch.get("challenge_id")
                prefix = ch.get("nonce_prefix")
                diff = ch.get("difficulty_bits", 25)

                if cid and prefix:
                    found = False
                    while not found:
                        # Update tampilan sederhana
                        sys.stdout.write(f"\r[*] Solving ID: {cid[:8]}... | Mined: {minted_count} ")
                        sys.stdout.flush()

                        nonce_res = solve_pow(prefix, diff)
                        
                        if nonce_res is not None:
                            # 2. Mint/Submit Solution
                            print(f"\n[!] Solution Found! Nonce: {nonce_res}. Submitting...")
                            m_status, m_res = http_request("POST", "/mint", cookie, 
                                                         {"challenge_id": cid, "solution_nonce": str(nonce_res)})
                            
                            if m_status == 200:
                                minted_count += 1
                                print("[✓] SUCCESS: Token Added to Balance!")
                            else:
                                print(f"[×] FAILED: Server returned status {m_status}")
                            
                            found = True
                            time.sleep(2) # Jeda anti-spam
                else:
                    time.sleep(5)
            else:
                print(f"\n[-] API Error ({status}). Retrying in 5s...")
                time.sleep(5)
                
        except Exception as e:
            print(f"\n[-] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_mining()
