import os
import requests
import time
import hashlib

def solve_challenge(challenge, target_bits):
    # Logika mining (Proof of Work) sederhana
    # Kamu bisa menyesuaikan ini dengan algoritma rpow2
    nonce = 0
    target = 2**(256 - target_bits)
    while True:
        text = challenge + str(nonce)
        h = hashlib.sha256(text.encode()).hexdigest()
        if int(h, 16) < target:
            return nonce
        nonce += 1

def start_mining():
    # Ambil cookie dari environment variable
    cookie = os.getenv('RPOW_COOKIE')
    
    if not cookie:
        print("Error: RPOW_COOKIE tidak ditemukan! Jalankan 'export RPOW_COOKIE=...' dulu.")
        return

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (RPOW-Miner-Python)'
    }

    print("--- RPOW2 Miner Started ---")
    
    while True:
        try:
            # 1. Ambil Challenge
            response = requests.post('https://api.rpow2.com/challenge', headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"Mengerjakan challenge: {data['challenge'][:15]}...")
                
                # 2. Selesaikan (Contoh logika)
                # solution = solve_challenge(data['challenge'], 25) 
                
                # 3. Kirim Hasil
                # requests.post('https://api.rpow2.com/solution', headers=headers, json={'solution': solution})
                
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_mining()
