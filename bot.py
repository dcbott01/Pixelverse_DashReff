import imaplib
import email
from email.header import decode_header
from email import policy
from email.parser import BytesParser
import requests
import time
import re
from colorama import Fore, Style, init
from faker import Faker
import random
import string

# Inisialisasi colorama dan Faker
init(autoreset=True)
fake = Faker()

# Masukkan Email Outlook disini
email_username = "email@outlook.com"
email_password = "password"

# Fungsi untuk koneksi ke IMAP dan login
def imap_connect(username, password):
    server = imaplib.IMAP4_SSL("imap-mail.outlook.com")
    server.login(username, password)
    return server

# Fungsi untuk mencari email berdasarkan subjek
def find_email_by_subject(server, subject):
    server.select("inbox")
    status, message_ids = server.search(None, 'ALL')
    ids = message_ids[0].split()
    
    for id in reversed(ids):
        status, msg_data = server.fetch(id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                decoded_subject = decode_header(msg["Subject"])[0][0]
                if isinstance(decoded_subject, bytes):
                    decoded_subject = decoded_subject.decode()
                if subject in decoded_subject:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                return part.get_payload(decode=True).decode()
                    else:
                        return msg.get_payload(decode=True).decode()
    return None

# Fungsi untuk mengekstrak OTP dari body email
def get_otp_from_email(body):
    match = re.search(r'Here is your Pixelverse OTP: (\d+)', body)
    return match.group(1) if match else None

# Fungsi untuk meminta OTP
def request_otp(email):
    response = requests.post('https://api.pixelverse.xyz/api/otp/request', json={'email': email})
    return response.status_code == 200

# Fungsi untuk verifikasi OTP
def verify_otp(email, otp):
    response = requests.post('https://api.pixelverse.xyz/api/auth/otp', json={'email': email, 'otpCode': otp})
    if response.status_code in [200, 201]:
        refresh_token = response.cookies.get('refresh-token')
        data = response.json()
        data['refresh_token'] = refresh_token
        if 'tokens' in data and 'access' in data['tokens']:
            data['access_token'] = data['tokens']['access']
            return data
        else:
            print(f"Respon tidak mengandung tokens['access'] untuk {email}. Respon: {data}")
    else:
        print(f"Verifikasi OTP gagal. Status: {response.status_code}, Respon: {response.text}")
    return None

# Fungsi untuk mengatur referral
def apply_referral(referral_code, access_token):
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.put(f'https://api.pixelverse.xyz/api/referrals/set-referer/{referral_code}', headers=headers)
    return response.status_code, response.json() if response.content else None

# Fungsi untuk memperbarui username dan biografi
def update_profile(access_token):
    url = "https://api.pixelverse.xyz/api/users/@me"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    payload = {
        "updateProfileOptions": {
            "username": fake.user_name(),
            "biography": fake.sentence()
        }
    }
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(Fore.GREEN + Style.BRIGHT + "Profil berhasil diperbarui.")
    else:
        print(Fore.RED + Style.BRIGHT + f"Gagal memperbarui profil. Status: {response.status_code}, Respon: {response.text}")
    return response.status_code == 200

# Fungsi untuk membeli pet
def purchase_pet(access_token, pet_id):
    url = f"https://api.pixelverse.xyz/api/pets/{pet_id}/buy"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.post(url, headers=headers)
    if response.status_code in [200, 201]:
        print(Fore.GREEN + Style.BRIGHT + "Pet berhasil dibeli!")
        return response.status_code, response.json()
    else:
        print(Fore.RED + Style.BRIGHT + f"Gagal membeli pet. Status: {response.status_code}, Respon: {response.text}")
    return None, None

# Fungsi untuk memilih pet
def select_pet(access_token, pet_data):
    pet_id = pet_data['id']
    url = f"https://api.pixelverse.xyz/api/pets/user-pets/{pet_id}/select"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(Fore.GREEN + Style.BRIGHT + "Pet berhasil dipilih!")
        return True
    elif response.status_code == 201:
        print(Fore.GREEN + Style.BRIGHT + "Pet sudah dipilih sebelumnya.")
        return True
    elif response.status_code == 400 and response.json().get('message') == "You have already selected this pet":
        print(Fore.GREEN + Style.BRIGHT + "Pet berhasil dipilih!")
        return True
    else:
        print(Fore.RED + Style.BRIGHT + f"Gagal memilih pet. Status: {response.status_code}, Respon: {response.text}")
    return False

# Fungsi untuk klaim daily reward
def claim_reward(access_token):
    url = "https://api.pixelverse.xyz/api/daily-reward/complete"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code in [200, 201]:
            print(Fore.GREEN + Style.BRIGHT + "Daily reward berhasil diklaim!")
            return True
        else:
            print(Fore.RED + Style.BRIGHT + f"Gagal klaim daily reward. Status: {response.status_code}, Respon: {response.text}")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Gagal klaim daily reward: {str(e)}")
    return False

# Fungsi untuk menghasilkan email dengan tambahan karakter acak
def create_random_email(base_email):
    email_name, domain = base_email.split('@')
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
    return f"{email_name}+{random_suffix}@{domain}"

# Fungsi untuk generate beberapa email
def generate_email_list(base_email, count):
    emails = [create_random_email(base_email) for _ in range(count)]
    with open('data.txt', 'w') as file:
        file.write('\n'.join(emails))
    print(Fore.GREEN + Style.BRIGHT + f"{count} email berhasil di-generate dan disimpan di data.txt.")

# Fungsi utama untuk referral
def main():
    # Menu pilihan
    print("Bot by Nazara. Pilih opsi:")
    print("1. Generate email")
    print("2. Lanjutkan referral")
    choice = int(input("Masukkan pilihan (1/2): "))

    if choice == 1:
        count = int(input("Masukkan jumlah email yang akan di-generate: "))
        generate_email_list(email_username, count)

        if input("Lanjutkan ke referral? (Y/N): ").strip().upper() == 'Y':
            choice = 2
        else:
            print(Fore.GREEN + Style.BRIGHT + "Proses dihentikan.")
            return

    if choice == 2:
        # Baca daftar email dari file
        with open('data.txt', 'r') as file:
            emails = [line.strip() for line in file]

        # Baca referral code dari file
        with open('reff.txt', 'r') as file:
            referral_code = file.read().strip()

        # Koneksi ke IMAP
        server = imap_connect(email_username, email_password)

        # Proses setiap email
        successful_emails = []
        for index, email in enumerate(emails, start=1):
            if len(successful_emails) >= len(emails):
                break
            print(Fore.CYAN + Style.BRIGHT + f"Proses email ke-{index}: {email}")
            if request_otp(email):
                print(Fore.YELLOW + Style.BRIGHT + f"OTP diminta untuk {email}. Tunggu beberapa detik...")
                time.sleep(10)

                otp_body = find_email_by_subject(server, "Pixelverse Authorization")

                if otp_body:
                    otp_code = get_otp_from_email(otp_body)
                    if otp_code:
                        print(Fore.GREEN + Style.BRIGHT + f"OTP diterima: {otp_code}")
                        auth_data = verify_otp(email, otp_code)

                        if auth_data and 'access_token' in auth_data:
                            access_token = auth_data['access_token']
                            print(Fore.GREEN + Style.BRIGHT + "Token akses diterima")
                            status_code, response_json = apply_referral(referral_code, access_token)
                            if status_code in [200, 201]:
                                print(Fore.GREEN + Style.BRIGHT + "Referral berhasil diterapkan.")
                                if update_profile(access_token):
                                    pet_id = "27977f52-997c-45ce-9564-a2f585135ff5"
                                    pet_status, pet_data = purchase_pet(access_token, pet_id)
                                    if pet_status in [200, 201]:
                                        if select_pet(access_token, pet_data):
                                            if claim_reward(access_token):
                                                print(Fore.BLUE + Style.BRIGHT + f"Referral ke-{index} berhasil")
                                                successful_emails.append(email)
                            else:
                                print(Fore.RED + Style.BRIGHT + f"Referral gagal untuk {email}. Status: {status_code}, Respon: {response_json}")
                        else:
                            print(Fore.RED + Style.BRIGHT + f"Verifikasi OTP gagal untuk {email}. Tidak ada access_token dalam respon.")
                    else:
                        print(Fore.RED + Style.BRIGHT + f"Tidak dapat mengekstrak OTP untuk {email}.")
                else:
                    print(Fore.RED + Style.BRIGHT + f"Tidak dapat menemukan email OTP untuk {email}.")
            else:
                print(Fore.RED + Style.BRIGHT + f"Permintaan OTP gagal untuk {email}.")

        # Simpan email yang gagal
        failed_emails = [email for email in emails if email not in successful_emails]
        with open('data.txt', 'w') as file:
            file.write('\n'.join(failed_emails))

        # Logout dari IMAP
        server.logout()
    else:
        print(Fore.RED + Style.BRIGHT + "Pilihan tidak valid.")

# Jalankan fungsi utama
if __name__ == "__main__":
    main()
