import hashlib
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# Layer 1: Custom Hash
# =========================
def custom_hash(password):
    """
    Mengubah password menjadi hash SHA-256.
    
    Kenapa pakai ini?
    - Sebagai layer tambahan sebelum masuk ke Werkzeug
    - Tidak menggunakan salt (karena nanti Werkzeug yang handle salt)
    - Harus deterministic (hasil selalu sama untuk input yang sama)
    """

    # Encode password ke bytes lalu hash dengan SHA-256
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# Layer 2: Final Hash (Werkzeug)
# =========================
def hash_password(password):
    """
    Fungsi untuk membuat hash password yang akan disimpan ke database.

    Alur:
    1. Password asli → custom_hash (SHA-256)
    2. Hasilnya → di-hash lagi oleh Werkzeug (lebih aman)

    Output:
    - String hash yang sudah mengandung:
      - algoritma
      - salt
      - iterasi
    """

    # Step 1: Hash custom (layer tambahan)
    first_layer = custom_hash(password)

    # Step 2: Hash dengan Werkzeug (layer utama keamanan)
    final_hash = generate_password_hash(first_layer)

    # Return hasil final untuk disimpan di database
    return final_hash


# =========================
# Verifikasi Password
# =========================
def verify_password(password, stored_hash):
    """
    Fungsi untuk mengecek apakah password yang diinput user benar.

    Parameter:
    - password     : input dari user saat login
    - stored_hash  : hash yang disimpan di database

    Alur:
    1. Password input → custom_hash
    2. Hasilnya → dicek dengan Werkzeug
    """

    # Step 1: Hash input user dengan cara yang sama
    first_layer = custom_hash(password)

    # Step 2: Bandingkan dengan hash di database menggunakan Werkzeug
    # Werkzeug otomatis handle:
    # - salt
    # - iterasi
    # - keamanan perbandingan (anti timing attack)
    return check_password_hash(stored_hash, first_layer)

# =========================
# TEST SINKRONISASI
# =========================

'''password_asli = "rahasia123"

# Hash password
hashed = hash_pass(password_asli)
print("Hash:", hashed)

# Test benar
hasil_benar = verify_pass("rahasia123", hashed)
print("Test benar:", hasil_benar)

# Test salah
hasil_salah = verify_pass("salah123", hashed)
print("Test salah:", hasil_salah)'''