import requests
import time
from colorama import init, Fore, Style
import sys
import os
import datetime
import pytz

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

url_claim = 'https://elb.seeddao.org/api/v1/seed/claim'
url_balance = 'https://elb.seeddao.org/api/v1/profile/balance'
url_checkin = 'https://elb.seeddao.org/api/v1/login-bonuses'
url_upgrade_storage = 'https://elb.seeddao.org/api/v1/seed/storage-size/upgrade'
url_upgrade_mining = 'https://elb.seeddao.org/api/v1/seed/mining-speed/upgrade'
url_upgrade_holy = 'https://elb.seeddao.org/api/v1/upgrades/holy-water'
url_get_profile = 'https://elb.seeddao.org/api/v1/profile'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-length': '0',
    'dnt': '1',
    'origin': 'https://cf.seeddao.org',
    'priority': 'u=1, i',
    'referer': 'https://cf.seeddao.org/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'telegram-data': 'tokens',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

def load_credentials():
    try:
        with open('query.txt', 'r') as file:
            tokens = file.read().strip().split('\n')
        return tokens
    except FileNotFoundError:
        print("File query.txt tidak ditemukan")
        return []
    except Exception as e:
        print("Terjadi kesalahan:", str(e))
        return []

def check_worm():
    response = requests.get('https://elb.seeddao.org/api/v1/worms', headers=headers)
    if response.status_code == 200:
        worm_data = response.json().get('data', {})
        next_refresh = worm_data.get('next_refresh')
        is_caught = worm_data.get('is_caught')

        if next_refresh is not None and is_caught is not None:
            next_refresh_dt = datetime.datetime.fromisoformat(next_refresh[:-1] + '+00:00')
            now_utc = datetime.datetime.now(pytz.utc)

            time_diff_seconds = (next_refresh_dt - now_utc).total_seconds()
            hours = int(time_diff_seconds // 3600)
            minutes = int((time_diff_seconds % 3600) // 60)

            print(f"{Fore.GREEN+Style.BRIGHT}[ Worms ]: Berikutnya dalam {hours} jam {minutes} menit - Status: {'Ditangkap' if is_caught else 'Tersedia'}")
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Data worm tidak lengkap")

        return worm_data
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Tidak dapat mengambil data.")
        return None

def catch_worm():
    worm_data = check_worm()
    if worm_data and not worm_data['is_caught']:
        response = requests.post('https://elb.seeddao.org/api/v1/worms/catch', headers=headers)
        if response.status_code == 200:
            print(f"{Fore.GREEN+Style.BRIGHT}[ Worms ]: Berhasil menangkap worm")
        elif response.status_code == 400:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Worm sudah ditangkap")
        elif response.status_code == 404:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Worm tidak ditemukan")    
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Gagal menangkap worm, kode status:", response)
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Worm tidak tersedia atau sudah ditangkap.")

def get_profile():
    response = requests.get(url_get_profile, headers=headers)
    if response.status_code == 200:
        profile_data = response.json()
        name = profile_data['data']['name']
        print(f"{Fore.CYAN+Style.BRIGHT}============== [ {name} ] ==============")
        upgrades = {}
        for upgrade in profile_data['data']['upgrades']:
            upgrade_type = upgrade['upgrade_type']
            upgrade_level = upgrade['upgrade_level']
            if upgrade_type in upgrades:
                if upgrade_level > upgrades[upgrade_type]:
                    upgrades[upgrade_type] = upgrade_level
            else:
                upgrades[upgrade_type] = upgrade_level

        for upgrade_type, level in upgrades.items():
            print(f"{Fore.BLUE+Style.BRIGHT}[ {upgrade_type.capitalize()} Level ]: {level + 1}")
    else:
        print("Tidak dapat mengambil data, kode status:", response.status_code)
        return None 

def check_balance():
    response = requests.get(url_balance, headers=headers)
    if response.status_code == 200:
        balance_data = response.json()
        print(f"{Fore.YELLOW+Style.BRIGHT}[ Saldo ]: {balance_data['data'] / 1000000000}")
        return True  
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Saldo ]: Gagal | {response.status_code}")
        return False

def checkin_daily():
    response = requests.post(url_checkin, headers=headers)
    if response.status_code == 200:
        data = response.json()
        day = data.get('data', {}).get('no', '')
        print(f"{Fore.GREEN+Style.BRIGHT}[ Checkin ]: Check-in berhasil | Hari {day}")
    else:
        data = response.json()
        if data.get('message') == 'already claimed for today':
            print(f"{Fore.RED+Style.BRIGHT}[ Checkin ]: Sudah check-in hari ini")
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Checkin ]: Gagal | {data}")

def upgrade_storage(confirm):
    if confirm.lower() == 'y':
        response = requests.post(url_upgrade_storage, headers=headers)
        if response.status_code == 200:
            return '[ Upgrade storage ]: Berhasil'
        else:
            return '[ Upgrade storage ]: Saldo tidak cukup'
    else:
        return None

def upgrade_mining(confirm):
    if confirm.lower() == 'y':
        response = requests.post(url_upgrade_mining, headers=headers)
        if response.status_code == 200:
            return '[ Upgrade mining ]: Berhasil'
        else:
            return '[ Upgrade mining ]: Saldo tidak cukup'
    else:
        return None

def upgrade_holy(confirm):
    if confirm.lower() == 'y':
        response = requests.post(url_upgrade_holy, headers=headers)
        if response.status_code == 200:
            return '[ Upgrade holy ]: Berhasil'
        else:
            return '[ Upgrade holy ]: Kondisi tidak memenuhi syarat'
    else:
        return None

def get_tasks():
    response = requests.get('https://elb.seeddao.org/api/v1/tasks/progresses', headers=headers)
    tasks = response.json()['data']
    for task in tasks:
        if task['task_user'] is None or not task['task_user']['completed']:
            complete_task(task['id'], task['name'])

def complete_task(task_id, task_name):
    response = requests.post(f'https://elb.seeddao.org/api/v1/tasks/{task_id}', headers=headers)
    if response.status_code == 200:
        print(f"{Fore.GREEN+Style.BRIGHT}[ Tugas ]: Tugas {task_name} telah selesai.")
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Tugas ]: Tidak dapat menyelesaikan tugas {task_name}, kode status: {response.status_code}")

def main():
    tokens = load_credentials()
    
    confirm_storage = input("Apakah Anda ingin otomatis upgrade storage? (y/n): ")
    confirm_mining = input("Apakah Anda ingin otomatis upgrade mining? (y/n): ")
    confirm_holy = input("Apakah Anda ingin otomatis upgrade holy? (y/n): ")
    confirm_task = input("Apakah Anda ingin otomatis menyelesaikan tugas? (y/n): ")
    
    while True:
        hasil_upgrade_storage = upgrade_storage(confirm_storage)
        hasil_upgrade_mining = upgrade_mining(confirm_mining)
        hasil_upgrade_holy = upgrade_holy(confirm_holy)
        
        for index, token in enumerate(tokens):
            headers['telegram-data'] = token
            info = get_profile()
            if info:
                print(f"Memproses akun {info['data']['name']}")
                
            if hasil_upgrade_storage:
                print(hasil_upgrade_storage)
                time.sleep(1)
            if hasil_upgrade_mining:
                print(hasil_upgrade_mining)
                time.sleep(1)
            if hasil_upgrade_holy:
                print(hasil_upgrade_holy)
                time.sleep(1)

            if check_balance():
                response = requests.post(url_claim, headers=headers)
                if response.status_code == 200:
                    print(f"{Fore.GREEN+Style.BRIGHT}[ Klaim ]: Klaim berhasil")
                elif response.status_code == 400:
                    response_data = response.json()
                    print(f"{Fore.RED+Style.BRIGHT}[ Klaim ]: Belum saatnya klaim")
                else:
                    print("Terjadi kesalahan, kode status:", response.status_code)

                checkin_daily()
                catch_worm()
                if confirm_task.lower() == 'y':
                    get_tasks()
        
        for i in range(7200, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN+Style.BRIGHT}============ Akun telah diproses, menunggu {i} detik sebelum melanjutkan putaran berikutnya ============")
            sys.stdout.flush()
            time.sleep(1)
        print()
        clear_console()

if __name__ == "__main__":
    main()
