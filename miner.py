import os
import cloudscraper
import time
import hashlib
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def solve_pow(challenge_id, nonce_prefix, difficulty):
    nonce = 0
    target = 2**(256 - difficulty)
    while True:
        text = f"{nonce_prefix}{nonce}"
        h = hashlib.sha256(text.encode()).hexdigest()
        if int(h, 16) < target:
            return nonce, h
        nonce += 1
        # Memberikan jeda kontrol ke sistem setiap 100rb hash
        if nonce % 100000 == 0:
            return None, nonce 

def start_mining():
    cookie = os.getenv('RPOW_COOKIE')
    if not cookie:
        print("[-] Error: RPOW_COOKIE belum di-set!")
        return

    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Referer': 'https://rpow2.com/',
        'Origin': 'https://rpow2.com',
        'Accept': 'application/json'
    }
    
    hashes_total = 0
    mined_run = 0
    start_time = time.time()

    clear_screen()

    while True:
        try:
            # Jeda minimal sesuai aturan server (2 detik)
            time.sleep(2.2)
            
            # 1. Ambil Challenge baru
            res = scraper.post('https://api.rpow2.com/challenge', headers=headers, json={}, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                c_id = data.get('challenge_id')
                prefix = data.get('nonce_prefix')
                diff = data.get('difficulty_bits', 25)

                if c_id and prefix:
                    found = False
                    while not found:
                        elapsed_sec = time.time() - start_time
                        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_sec))
                        rate = (hashes_total / elapsed_sec / 1000000) if elapsed_sec > 0 else 0
                        
                        sys.stdout.write("\033[H")
                        print(f"+-------------------------------------------------------+")
                        print(f"|  STATUS: MINING (ACTIVE)     | RATE: {rate:.2f} MH/s")
                        print(f"|  HASHES: {hashes_total:,} | MINED: {mined_run}")
                        print(f"|  ID: {c_id[:8]}... | ELAPSED: {elapsed_str}")
                        print(f"+-------------------------------------------------------+")

                        nonce_res, h_result = solve_pow(c_id, prefix, diff)
                        
                        if nonce_res is not None:
                            # TAMPILKAN STATUS SUBMITTING
                            print(f"|  >> SUBMITTING SOLUTION...                            |")
                            
                            sol_res = scraper.post(
                                'https://api.rpow2.com/solution', 
                                headers=headers, 
                                json={'challenge_id': c_id, 'nonce': nonce_res},
                                timeout=15
                            )
                            
                            if sol_res.status_code == 200:
                                mined_run += 1
                                print(f"|  >> SUCCESS: TOKEN MINED!                             |")
                                time.sleep(1) # Jeda visual biar terlihat di terminal
                                found = True
                            else:
                                print(f"|  >> FAILED: {sol_res.status_code} - REJECTED                 |")
                                time.sleep(2)
                                found = True # Cari challenge baru jika ditolak
                                
                            hashes_total += nonce_res
                        else:
                            hashes_total += h_result
                else:
                    print(f"[-] Format JSON berubah atau Akses Ditolak: {data}")
                    time.sleep(5)
            else:
                print(f"[-] Error {res.status_code}: {res.text[:50]}")
                time.sleep(5)
                
        except Exception as e:
            print(f"[-] Gangguan Koneksi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_mining()
