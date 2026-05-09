import os
import requests
import time
import hashlib
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def solve_pow(challenge, difficulty):
    # Logika mining asli: mencari hash yang sesuai target
    nonce = 0
    target = 2**(256 - difficulty)
    while True:
        text = f"{challenge}{nonce}"
        h = hashlib.sha256(text.encode()).hexdigest()
        if int(h, 16) < target:
            return nonce, h
        nonce += 1
        # Agar tidak hang, beri laporan berkala ke dashboard
        if nonce % 100000 == 0:
            return None, nonce 

def start_mining():
    cookie = os.getenv('RPOW_COOKIE')
    headers = {'Cookie': cookie, 'Content-Type': 'application/json'}
    
    hashes_total = 0
    mined_run = 0
    start_time = time.time()
    last_token = "None"

    while True:
        try:
            # 1. Ambil Challenge
            res = requests.post('https://api.rpow2.com/challenge', headers=headers)
            if res.status_code == 200:
                data = res.json()
                challenge = data['challenge']
                difficulty = 25 # Sesuai target di web kamu
                
                # 2. Proses Mining (Looping sampai ketemu)
                found = False
                while not found:
                    elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    rate = hashes_total / (time.time() - start_time) / 1000000 if (time.time() - start_time) > 0 else 0
                    
                    # Update Dashboard
                    sys.stdout.write("\033[H")
                    print(f"+-------------------------------------------------------+")
                    print(f"|  STATUS: MINING | RATE: {rate:.2f} MH/s | ELAPSED: {elapsed}")
                    print(f"|  HASHES: {hashes_total:,} | MINED: {mined_run}")
                    print(f"|  CHALLENGE: {challenge[:20]}...")
                    print(f"+-------------------------------------------------------+")

                    nonce_res, h_or_n = solve_pow(challenge, difficulty)
                    
                    if nonce_res is not None:
                        # 3. Ketemu Solution! Kirim ke Server
                        sol_res = requests.post('https://api.rpow2.com/solution', 
                                             headers=headers, 
                                             json={'challenge': challenge, 'nonce': nonce_res})
                        if sol_res.status_code == 200:
                            mined_run += 1
                            last_token = h_or_n
                            found = True
                        hashes_total += nonce_res
                    else:
                        hashes_total += h_or_n # Tambah hitungan hash meski belum ketemu
            else:
                print(f"Error Server: {res.status_code}. Re-checking...")
                time.sleep(5)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    start_mining()
