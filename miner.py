import os
import requests
import time
import hashlib
import sys

def clear_screen():
    # Membersihkan terminal (works on Windows & Linux)
    os.system('cls' if os.name == 'nt' else 'clear')

def start_mining():
    cookie = os.getenv('RPOW_COOKIE')
    if not cookie:
        print("Error: RPOW_COOKIE belum di-export!")
        return

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Statistik awal
    hashes_current = 0
    mined_run = 0
    start_time = time.time()
    status = "WAITING"
    last_token = "None"

    clear_screen()
    
    while True:
        try:
            status = "FETCHING"
            # Tampilan seperti di screenshot web kamu
            elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
            rate = hashes_current / (time.time() - start_time) / 1000000 if (time.time() - start_time) > 0 else 0
            
            # Print Dashboard (ANSI Escape untuk stay at top)
            sys.stdout.write("\033[H") # Pindah kursor ke atas
            print(f"+-------------------------------------------------------+")
            print(f"|          RPOW2 - Headless Miner (AssetFinger)         |")
            print(f"+-------------------------------------------------------+")
            print(f"  TARGET         : 25 trailing zero bits")
            print(f"  HASHES (cur)   : {hashes_current:,}")
            print(f"  RATE           : {rate:.2f} MH/s")
            print(f"  ELAPSED        : {elapsed}")
            print(f"  STATUS         : {status}")
            print(f"  MINED THIS RUN : {mined_run}")
            print(f"  LAST TOKEN     : {last_token[:30]}...")
            print(f"+-------------------------------------------------------+")

            # Ambil Challenge
            response = requests.post('https://api.rpow2.com/challenge', headers=headers, timeout=10)
            
            if response.status_code == 200:
                status = "MINING"
                data = response.json()
                challenge = data.get('challenge')
                
                # Simulasi proses hashing (Ganti dengan logika solver asli RPOW2 kamu)
                # Di sini kita naikkan hash count untuk visualisasi status
                hashes_current += 1000000 
                
                # Jika berhasil submit (Simulasi):
                # mined_run += 1
                # last_token = "abc..."
                
            elif response.status_code == 401:
                status = "COOKIE EXPIRED"
            else:
                status = f"ERROR {response.status_code}"

        except Exception as e:
            status = f"EXCEPTION: {str(e)[:20]}"
        
        time.sleep(1) # Jeda agar tidak terkena rate limit API

if __name__ == "__main__":
    start_mining()
