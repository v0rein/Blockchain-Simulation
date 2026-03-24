# Dokumentasi Blockchain dengan Flask API

## Daftar Isi

- [Dokumentasi Blockchain dengan Flask API](#dokumentasi-blockchain-dengan-flask-api)
  - [Daftar Isi](#daftar-isi)
  - [Pendahuluan](#pendahuluan)
  - [Arsitektur Sistem](#arsitektur-sistem)
  - [Penjelasan Source Code](#penjelasan-source-code)
    - [`wallet.py` — Manajemen Kunci \& Digital Signature](#walletpy--manajemen-kunci--digital-signature)
    - [`blockchain.py` — Inti Blockchain](#blockchainpy--inti-blockchain)
    - [`server.py` — Flask REST API](#serverpy--flask-rest-api)
    - [`run.bat` — Peluncur Multi-Node](#runbat--peluncur-multi-node)
  - [Cara Menjalankan Project](#cara-menjalankan-project)
    - [Prasyarat](#prasyarat)
    - [Langkah-langkah](#langkah-langkah)
  - [Daftar API Endpoints](#daftar-api-endpoints)
  - [Pengujian dengan Postman](#pengujian-dengan-postman)
    - [1. Membuat Wallet Baru](#1-membuat-wallet-baru)
    - [2. Menandatangani Transaksi (Digital Signature)](#2-menandatangani-transaksi-digital-signature)
    - [3. Menambahkan Transaksi](#3-menambahkan-transaksi)
    - [4. Melihat Transaksi Pending](#4-melihat-transaksi-pending)
    - [5. Proses Mining \& Reward Miner](#5-proses-mining--reward-miner)
    - [6. Melihat Blockchain (Chain)](#6-melihat-blockchain-chain)
    - [7. Validasi Digital Signature (Transaksi Invalid)](#7-validasi-digital-signature-transaksi-invalid)
    - [8. Registrasi Node](#8-registrasi-node)
    - [9. Sinkronisasi Antar-Node (Consensus)](#9-sinkronisasi-antar-node-consensus)
  - [Struktur File Project](#struktur-file-project)
  - [Alur Kerja Sistem](#alur-kerja-sistem)
  - [Teknologi yang Digunakan](#teknologi-yang-digunakan)

---

## Pendahuluan

Project ini mengimplementasikan sebuah **Blockchain sederhana** menggunakan **Python** dan **Flask** sebagai REST API. Sistem ini mensimulasikan jaringan blockchain dengan fitur:

- **Digital Signature** menggunakan algoritma ECDSA (Elliptic Curve Digital Signature Algorithm) dengan kurva SECP256k1
- **Mining** dengan mekanisme Proof of Work (PoW)
- **Reward Miner** sebesar 50 koin untuk setiap blok yang berhasil ditambang
- **Multi-Node** — minimal 3 node yang berjalan secara bersamaan
- **Consensus Algorithm** — sinkronisasi antar-node menggunakan aturan rantai terpanjang (longest chain rule)

---

## Arsitektur Sistem

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Node 5000  │◄───►│   Node 5001  │◄───►│   Node 5002  │
│  (Flask API) │     │  (Flask API) │     │  (Flask API) │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Blockchain  │     │  Blockchain  │     │  Blockchain  │
│   Instance   │     │   Instance   │     │   Instance   │
└──────────────┘     └──────────────┘     └──────────────┘
```

Setiap node memiliki:

- Instance **Blockchain** sendiri
- **Wallet** sendiri untuk menerima mining reward
- **Flask API** yang berjalan di port berbeda
- Kemampuan untuk **sinkronisasi** dengan node lain

---

## Penjelasan Source Code

### `wallet.py` — Manajemen Kunci & Digital Signature

```python
# Menggunakan library ecdsa dengan kurva SECP256k1 (sama seperti Bitcoin)
class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)  # Kunci privat
        self.public_key = self.private_key.get_verifying_key()   # Kunci publik
```

| Fungsi                  | Deskripsi                                                                |
| ----------------------- | ------------------------------------------------------------------------ |
| `__init__()`            | Generate pasangan kunci privat & publik menggunakan ECDSA SECP256k1      |
| `get_private_key_hex()` | Mendapatkan private key dalam format hexadecimal                         |
| `get_public_key_hex()`  | Mendapatkan public key dalam format hexadecimal                          |
| `sign_transaction()`    | Menandatangani data transaksi menggunakan private key (static method)    |
| `verify_signature()`    | Memverifikasi keabsahan signature menggunakan public key (static method) |

### `blockchain.py` — Inti Blockchain

**Class `Transaction`:**

- Menyimpan data transaksi (sender, receiver, amount, signature)
- Method `is_valid()` memverifikasi digital signature. Transaksi dari `MINING_REWARD` dianggap valid tanpa signature

**Class `Block`:**

- Menyimpan data blok (index, timestamp, transactions, previous_hash, nonce, hash)
- Method `mine_block(difficulty)` menjalankan Proof of Work — mencari `nonce` hingga hash diawali `difficulty` jumlah angka nol

**Class `Blockchain`:**

| Atribut         | Nilai | Deskripsi                                       |
| --------------- | ----- | ----------------------------------------------- |
| `difficulty`    | 4     | Hash blok harus diawali 4 angka nol (`0000...`) |
| `mining_reward` | 50    | Reward yang diberikan kepada miner per blok     |

| Method                        | Deskripsi                                                                     |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `create_block()`              | Membuat blok baru dan menjalankan mining (PoW)                                |
| `mine_pending_transactions()` | Membuat reward transaction + mine blok baru                                   |
| `add_transaction()`           | Menambahkan transaksi setelah verifikasi digital signature                    |
| `register_node()`             | Mendaftarkan node tetangga                                                    |
| `resolve_conflicts()`         | Algoritma konsensus — mengganti chain jika ada chain valid yang lebih panjang |
| `is_chain_valid()`            | Memvalidasi integritas seluruh rantai blok                                    |

### `server.py` — Flask REST API

Menyediakan endpoint API untuk berinteraksi dengan blockchain. Setiap node yang dijalankan otomatis membuat wallet sendiri untuk menerima mining reward.

### `run.bat` — Peluncur Multi-Node

Script batch untuk menjalankan 3 node di port 5000, 5001, dan 5002 secara bersamaan, masing-masing di jendela terminal terpisah.

---

## Cara Menjalankan Project

### Prasyarat

- Python 3.8+
- pip (Python package manager)
- Postman (untuk pengujian API)

### Langkah-langkah

1. **Buat Virtual Environment & Install Dependencies**

   ```bash
   cd "d:\SEMESTER 6\Teknologi Blockchain\Flask"
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Jalankan 3 Node Sekaligus**

   Double-click file `run.bat`, atau jalankan manual di 3 terminal terpisah:

   ```bash
   # Terminal 1
   python server.py -p 5000

   # Terminal 2
   python server.py -p 5001

   # Terminal 3
   python server.py -p 5002
   ```

3. **Buka Postman** dan mulai pengujian menggunakan panduan di bawah ini.

---

## Daftar API Endpoints

| Method | Endpoint            | Deskripsi                                               |
| ------ | ------------------- | ------------------------------------------------------- |
| `GET`  | `/wallet/new`       | Membuat wallet baru (public key + private key)          |
| `POST` | `/wallet/sign`      | Menandatangani transaksi menggunakan private key        |
| `POST` | `/transactions/new` | Menambahkan transaksi baru (harus sudah ditandatangani) |
| `GET`  | `/pending`          | Melihat transaksi yang menunggu mining                  |
| `GET`  | `/mine`             | Menambang blok baru (+ reward untuk miner)              |
| `GET`  | `/chain`            | Melihat seluruh blockchain                              |
| `POST` | `/nodes/register`   | Mendaftarkan node tetangga                              |
| `GET`  | `/nodes/resolve`    | Sinkronisasi blockchain (consensus algorithm)           |

---

## Pengujian dengan Postman

> **Catatan:** Pastikan ketiga node sudah berjalan sebelum memulai pengujian.
> Screenshot pengguna ditambahkan di bawah setiap langkah.

### 1. Membuat Wallet Baru

Membuat pasangan kunci (private key & public key) yang digunakan untuk menandatangani transaksi.

- **Method:** `GET`
- **URL:** `http://localhost:5000/wallet/new`

**Contoh Response:**

```json
{
  "private_key": "a1b2c3d4e5f6...abcdef1234567890",
  "public_key": "f0e1d2c3b4a5...1234567890abcdef"
}
```

> ⚠️ **Simpan kedua kunci ini!** Private key digunakan untuk sign transaksi, public key sebagai identitas pengirim.

**Screenshot:**
![Wallet](/images/Wallet1.png)
![Wallet](/images/Wallet2.png)
![Wallet](/images/Wallet3.png)

---

### 2. Menandatangani Transaksi (Digital Signature)

Menggunakan private key untuk membuat digital signature pada data transaksi.

- **Method:** `POST`
- **URL:** `http://localhost:5000/wallet/sign`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "private_key": "<PRIVATE_KEY_DARI_LANGKAH_1>",
  "sender": "<PUBLIC_KEY_DARI_LANGKAH_1>",
  "receiver": "<PUBLIC_KEY_PENERIMA>",
  "amount": 10
}
```

> **Tips:** Untuk `receiver`, Anda bisa membuat wallet kedua via `/wallet/new` atau gunakan public key dari node lain.

**Contoh Response:**

```json
{
  "sender": "f0e1d2c3b4a5...1234567890abcdef",
  "receiver": "a9b8c7d6e5f4...abcdef12345678",
  "amount": 10,
  "signature": "304502210...abcdef",
  "message": "Transaction signed successfully"
}
```

**Screenshot:**

![Signature](/images/Signature.png)

---

### 3. Menambahkan Transaksi

Mengirimkan transaksi yang sudah ditandatangani ke blockchain.

- **Method:** `POST`
- **URL:** `http://localhost:5000/transactions/new`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "sender": "<PUBLIC_KEY_PENGIRIM>",
  "receiver": "<PUBLIC_KEY_PENERIMA>",
  "amount": 10,
  "signature": "<SIGNATURE_DARI_LANGKAH_2>"
}
```

> **Penting:** Nilai `sender`, `receiver`, dan `amount` harus **sama persis** dengan yang digunakan saat menandatangani di langkah 2.

**Contoh Response:**

```json
{
  "message": "Transaction will be added to Block 2"
}
```

**Screenshot:**

![Transaction](/images/Transaction.png)

---

### 4. Melihat Transaksi Pending

Melihat daftar transaksi yang menunggu untuk dimasukkan ke dalam blok berikutnya.

- **Method:** `GET`
- **URL:** `http://localhost:5000/pending`

**Contoh Response:**

```json
{
  "pending_transactions": [
    {
      "sender": "f0e1d2c3b4a5...",
      "receiver": "a9b8c7d6e5f4...",
      "amount": 10,
      "signature": "304502210..."
    }
  ],
  "count": 1
}
```

**Screenshot:**

![Pending](/images/Pending.png)

---

### 5. Proses Mining & Reward Miner

Mining memproses seluruh transaksi pending menjadi blok baru. Miner otomatis mendapatkan **reward sebesar 50 koin**.

- **Method:** `GET`
- **URL:** `http://localhost:5000/mine`

**Contoh Response:**

```json
{
  "message": "New Block Forged",
  "index": 2,
  "transactions": [
    {
      "sender": "f0e1d2c3b4a5...",
      "receiver": "a9b8c7d6e5f4...",
      "amount": 10,
      "signature": "304502210..."
    },
    {
      "sender": "MINING_REWARD",
      "receiver": "<PUBLIC_KEY_NODE_MINER>",
      "amount": 50
    }
  ],
  "nonce": 54321,
  "previous_hash": "0000abcd1234...",
  "hash": "0000ef567890..."
}
```

**Perhatikan:**

- ✅ Transaksi user ada di dalam blok
- ✅ Transaksi reward dari `MINING_REWARD` dengan amount **50** otomatis ditambahkan
- ✅ Hash blok diawali dengan `0000` (sesuai difficulty = 4)

**Screenshot:**

![Mine](/images/Mine.png)

---

### 6. Melihat Blockchain (Chain)

Menampilkan seluruh rantai blok yang ada di node.

- **Method:** `GET`
- **URL:** `http://localhost:5000/chain`

**Contoh Response:**

```json
{
  "chain": [
    {
      "index": 1,
      "timestamp": 1711324800.0,
      "transactions": [],
      "nonce": 100,
      "previous_hash": "1",
      "hash": "abc123..."
    },
    {
      "index": 2,
      "timestamp": 1711324900.0,
      "transactions": [
        {
          "sender": "f0e1d2c3...",
          "receiver": "a9b8c7d6...",
          "amount": 10,
          "signature": "304502210..."
        },
        {
          "sender": "MINING_REWARD",
          "receiver": "<NODE_PUBLIC_KEY>",
          "amount": 50
        }
      ],
      "nonce": 54321,
      "previous_hash": "0000abcd...",
      "hash": "0000ef56..."
    }
  ],
  "length": 2
}
```

**Screenshot:**

![Chain](/images/Chain.png)

---

### 7. Validasi Digital Signature (Transaksi Invalid)

Menguji bahwa sistem **menolak transaksi dengan signature yang tidak valid**.

- **Method:** `POST`
- **URL:** `http://localhost:5000/transactions/new`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "sender": "<PUBLIC_KEY_PENGIRIM>",
  "receiver": "<PUBLIC_KEY_PENERIMA>",
  "amount": 10,
  "signature": "ini_signature_palsu_yang_tidak_valid"
}
```

**Contoh Response (Error 400):**

```json
{
  "error": "Invalid Transaction Signature!"
}
```

**Ini membuktikan bahwa:**

- ✅ Setiap transaksi **harus** memiliki digital signature yang valid
- ✅ Transaksi dengan signature palsu/tidak sesuai **ditolak** oleh sistem
- ✅ Hanya pemilik private key yang bisa membuat transaksi atas nama public key-nya

**Screenshot:**

![Invalid Transaction](/images/InvalidTransaction.png)

---

### 8. Registrasi Node

Mendaftarkan node-node tetangga agar bisa saling berkomunikasi dan sinkronisasi.

**Pada Node 5000 — daftarkan Node 5001 dan 5002:**

- **Method:** `POST`
- **URL:** `http://localhost:5000/nodes/register`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
  "nodes": ["http://localhost:5001", "http://localhost:5002"]
}
```

**Contoh Response:**

```json
{
  "message": "New nodes have been added",
  "total_nodes": ["localhost:5001", "localhost:5002"]
}
```

**Pada Node 5001 — daftarkan Node 5000 dan 5002:**

- **URL:** `http://localhost:5001/nodes/register`
- **Body:**

```json
{
  "nodes": ["http://localhost:5000", "http://localhost:5002"]
}
```

**Pada Node 5002 — daftarkan Node 5000 dan 5001:**

- **URL:** `http://localhost:5002/nodes/register`
- **Body:**

```json
{
  "nodes": ["http://localhost:5000", "http://localhost:5001"]
}
```

**Screenshot:**

![Register](/images/Register1.png)
![Register](/images/Register2.png)
![Register](/images/Register3.png)

---

### 9. Sinkronisasi Antar-Node (Consensus)

Setelah node terdaftar, kita dapat mensinkronisasi blockchain antar node. Algoritma konsensus menggunakan **longest chain rule** — node akan mengadopsi chain terpanjang yang valid dari jaringan.

**Skenario Pengujian:**

1. **Mine beberapa blok di Node 5000** (sehingga chain-nya lebih panjang):
   - `GET http://localhost:5000/mine` — (ulangi 2-3 kali)

2. **Cek chain di Node 5001** (masih pendek, hanya genesis block):
   - `GET http://localhost:5001/chain`

3. **Jalankan consensus di Node 5001:**
   - **Method:** `GET`
   - **URL:** `http://localhost:5001/nodes/resolve`

**Contoh Response (chain diganti):**

```json
{
  "message": "Our chain was replaced",
  "new_chain": [
    { "index": 1, "...": "..." },
    { "index": 2, "...": "..." },
    { "index": 3, "...": "..." }
  ]
}
```

**Contoh Response (chain sudah authoritative):**

```json
{
    "message": "Our chain is authoritative",
    "chain": [...]
}
```

**Ini membuktikan bahwa:**

- ✅ Node bisa saling berkomunikasi
- ✅ Consensus algorithm berjalan — node mengadopsi chain terpanjang
- ✅ Chain yang diadopsi divalidasi integritasnya (hash & PoW)

**Screenshot:**

![Replace](/images/Replace.png)
![Resolve](/images/Resolve.png)

---

## Struktur File Project

```
Flask/
├── blockchain.py       # Class Transaction, Block, Blockchain
├── wallet.py           # Class Wallet (ECDSA key pair, sign, verify)
├── server.py           # Flask REST API (endpoints)
├── run.bat             # Script untuk menjalankan 3 node
├── requirements.txt    # Dependencies (flask, requests, ecdsa)
├── DOKUMENTASI.md      # Dokumentasi ini
└── .venv/              # Virtual environment Python
```

---

## Alur Kerja Sistem

```
Sender                       Blockchain Network                    Miner
  │                                │                                │
  │ 1. Buat Wallet                 │                                │
  │    (GET /wallet/new)           │                                │
  │                                │                                │
  │ 2. Sign Transaksi             │                                │
  │    (POST /wallet/sign)         │                                │
  │                                │                                │
  │ 3. Kirim Transaksi ──────────►│                                │
  │    (POST /transactions/new)    │ Verifikasi Digital Signature   │
  │                                │ ✅ Valid → Masuk Pending Pool  │
  │                                │ ❌ Invalid → Ditolak           │
  │                                │                                │
  │                                │ 4. Mining ◄────────────────────│
  │                                │    (GET /mine)                 │
  │                                │    - Proses Proof of Work      │
  │                                │    - Tambah Reward (50 koin)   │
  │                                │    - Buat Blok Baru            │
  │                                │                                │
  │                                │ 5. Sinkronisasi Antar-Node     │
  │                                │    (GET /nodes/resolve)        │
  │                                │    - Longest Chain Rule        │
  └────────────────────────────────┴────────────────────────────────┘
```

---

## Teknologi yang Digunakan

| Teknologi             | Kegunaan                                                 |
| --------------------- | -------------------------------------------------------- |
| **Python 3**          | Bahasa pemrograman utama                                 |
| **Flask**             | Web framework untuk REST API                             |
| **ecdsa**             | Library untuk Elliptic Curve Digital Signature Algorithm |
| **requests**          | HTTP client untuk komunikasi antar-node                  |
| **hashlib (SHA-256)** | Hashing untuk Proof of Work dan integritas blok          |
| **Postman**           | Tool pengujian API                                       |
