# Movie Recommendation System Using RDF and SPARQL

Aplikasi eksplorasi dan pencarian film berbasis *knowledge graph*. Data film
direpresentasikan dalam format RDF, disimpan di Apache Jena Fuseki, lalu dicari
menggunakan SPARQL melalui antarmuka Streamlit.

## Fitur

- Menampilkan daftar judul film yang dapat dipilih pengguna.
- Mencari detail film menggunakan SPARQL.
- Menampilkan genre, pemeran, sutradara, negara produksi, tanggal rilis,
  anggaran, pendapatan, durasi, dan sinopsis.
- Mengambil poster film dari TMDB API.
- Menyediakan beberapa pertanyaan SPARQL siap pakai.

> [!NOTE]
> Implementasi saat ini lebih tepat disebut aplikasi eksplorasi film berbasis
> RDF dan SPARQL. Proyek belum memiliki rekomendasi personal berbasis machine
> learning, riwayat pengguna, atau collaborative filtering.

## Teknologi

- Python 3.14
- Streamlit
- pandas
- RDFLib
- SPARQLWrapper
- Apache Jena Fuseki
- TMDB API

## Struktur Proyek

```text
.
├── app.py
├── app22.py
├── o_app.py
├── rdf.py
├── generate_movie_list.py
├── requirements.txt
├── output_with_classes_and_properties.ttl
├── Preproccessing.ipynb
├── Project Code.ipynb
└── Datasets/
    ├── Movies_less.csv
    ├── Actors.csv
    ├── Directors.csv
    └── Countries.csv
```

File utama yang dijalankan adalah `app.py`. File `app22.py` dan `o_app.py`
merupakan variasi implementasi sebelumnya.

## Persyaratan

Sebelum menjalankan aplikasi, siapkan:

1. Python 3.14.
2. `pip`.
3. Java 21 atau yang lebih baru.
4. Distribusi biner Apache Jena Fuseki.
5. Koneksi internet untuk mengambil poster dari TMDB.

## Instalasi

### 1. Membuat virtual environment

Linux atau macOS:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika perintah `py` tidak tersedia, gunakan executable Python 3.14 yang
terpasang:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Memasang dependency

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Membuat `movie_list.pkl` (opsional)

`movie_list.pkl` berisi daftar judul yang digunakan untuk mengisi dropdown
Streamlit. Aplikasi otomatis membaca `Datasets/Movies_less.csv` jika file ini
belum tersedia. Untuk membuat cache agar proses pemuatan lebih cepat:

```bash
python generate_movie_list.py
```

Jika berhasil, terminal akan menampilkan lokasi file dan jumlah judul yang
disimpan.

File `.pkl` diabaikan oleh Git karena merupakan artefak lokal yang dapat dibuat
ulang. Jangan mengunduh file pickle dari sumber yang tidak dipercaya karena
proses `pickle.load()` dapat menjalankan kode berbahaya.

### 4. Menyiapkan Apache Jena Fuseki

Fuseki berfungsi sebagai database RDF dan penyedia endpoint SPARQL untuk
aplikasi. `app.py` tidak dapat melakukan pencarian film jika Fuseki belum aktif.

#### 4.1 Memastikan Java 21 tersedia

Apache Jena 6 membutuhkan Java 21 atau versi yang lebih baru. Periksa
instalasinya:

```powershell
java -version
```

Pastikan hasilnya menunjukkan versi `21` atau lebih tinggi.

Jika muncul pesan berikut:

```text
'java' is not recognized as an internal or external command,
operable program or batch file.
```

berarti Java belum terpasang atau belum tersedia melalui `PATH`.

Pada Windows 10/11, pasang Eclipse Temurin JDK 21 menggunakan PowerShell:

```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```

Setelah instalasi selesai:

1. Tutup semua jendela PowerShell atau Command Prompt.
2. Buka PowerShell baru agar perubahan `PATH` terbaca.
3. Jalankan pemeriksaan kembali:

```powershell
java -version
```

Contoh hasil yang benar:

```text
openjdk version "21.x.x"
```

Jika `java` masih tidak dikenali setelah membuka terminal baru, restart Windows,
kemudian jalankan `java -version` kembali.

> [!IMPORTANT]
> Jangan memasang Java 8, 11, atau 17 untuk Jena 6.1.0. Gunakan Java 21 atau
> versi yang lebih baru.

#### 4.2 Mengunduh paket Fuseki yang benar

Untuk pengguna Windows, buka
[Apache Jena Releases](https://jena.apache.org/download/), cari bagian
**Apache Jena Binary Distributions**, lalu bagian **Apache Jena Fuseki**.

Klik nama file berikut:

```text
apache-jena-fuseki-6.1.0.zip
```

Itulah satu-satunya file Jena yang diperlukan oleh project ini.

| File di halaman unduhan | Pilih? | Keterangan |
|---|---:|---|
| `apache-jena-fuseki-6.1.0.zip` | **Ya** | Server Fuseki siap digunakan di Windows |
| `apache-jena-fuseki-6.1.0.tar.gz` | Tidak | Paket Fuseki untuk pengguna yang memilih format `tar.gz`, biasanya Linux/macOS |
| `apache-jena-6.1.0.zip` | Tidak | Library dan command-line tools Jena, bukan server Fuseki |
| `jena-6.1.0-source-release.zip` | Tidak | Source code Apache Jena untuk dikompilasi oleh pengembang |
| `SHA512` atau `PGP` | Tidak | File untuk memverifikasi unduhan, bukan aplikasi |

> [!IMPORTANT]
> Pilih `apache-jena-fuseki-6.1.0.zip`, bukan
> `jena-6.1.0-source-release.zip` dan bukan `apache-jena-6.1.0.zip`.

File berikut adalah pilihan yang salah untuk menjalankan project:

```text
jena-6.1.0-source-release.zip
```

File tersebut berisi source code untuk pengembangan Apache Jena dan harus
dibangun menggunakan Maven. Source code bukan paket yang diperlukan untuk
menjalankan project ini.

Sebagai contoh, folder `C:\jena-6.1.0` dengan isi seperti berikut adalah source
code dan bukan instalasi Fuseki siap jalan:

```text
C:\jena-6.1.0
├── jena-arq
├── jena-core
├── jena-fuseki2
├── pom.xml
└── BUILD.md
```

Walaupun source code tersebut memiliki template `fuseki-server.bat`, paketnya
tidak memiliki `fuseki-server.jar`, sehingga script tidak dapat dijalankan
langsung.

Ekstrak `apache-jena-fuseki-6.1.0.zip`, misalnya ke:

```text
C:\apache-jena-fuseki-6.1.0
```

Folder yang benar harus memiliki file-file berikut pada tingkat paling atas:

```text
C:\apache-jena-fuseki-6.1.0
├── fuseki-server.bat
├── fuseki-server
├── fuseki-server.jar
├── webapp
└── bin
```

Jika `fuseki-server.jar` tidak ada, berarti file yang diunduh atau folder yang
dibuka bukan distribusi biner Fuseki. Kembali ke halaman unduhan dan pilih
`apache-jena-fuseki-6.1.0.zip`.

Setelah berhasil mengekstrak paket yang benar, folder source code lama
`C:\jena-6.1.0` tidak digunakan oleh project dan boleh diabaikan.

#### 4.3 Menjalankan Fuseki

Buka PowerShell, kemudian masuk ke folder distribusi biner:

```powershell
cd C:\apache-jena-fuseki-6.1.0
```

Jalankan server:

Windows PowerShell:

```powershell
.\fuseki-server.bat
```

Linux atau macOS:

```bash
./fuseki-server
```

Jangan tutup terminal tersebut selama aplikasi digunakan. Jika server berhasil
berjalan, buka:

```text
http://localhost:3030
```

Jika muncul pesan bahwa `java` tidak dikenali, kembali ke langkah 4.1. Jika
muncul pesan bahwa `fuseki-server.jar` tidak ditemukan, kembali ke langkah 4.2
dan unduh distribusi biner Fuseki.

#### 4.4 Membuat dataset `movies`

Pada halaman Fuseki:

1. Pilih **Manage datasets**.
2. Klik **Add new dataset** atau **Add one**.
3. Isi **Dataset name** dengan `movies` — gunakan huruf kecil.
4. Pilih **Persistent (TDB2)** agar data tetap tersedia setelah Fuseki
   dimatikan.
5. Klik **Create dataset**.

Nama dataset harus tepat `movies` karena `app.py` menggunakan URL:

```text
http://localhost:3030/movies/sparql
```

#### 4.5 Mengunggah data RDF

1. Pada daftar dataset, pilih dataset **movies**.
2. Buka tab **Upload data** atau **Add data**.
3. Klik **Select files**.
4. Pilih file proyek:
   `output_with_classes_and_properties.ttl`.
5. Pilih **Default graph** jika Fuseki meminta tujuan graph.
6. Klik **Upload**.
7. Tunggu sampai Fuseki menampilkan bahwa proses unggah berhasil.

#### 4.6 Menguji data dan endpoint SPARQL

1. Buka halaman query:

```text
http://localhost:3030/#/dataset/movies/query
```

2. Masukkan query berikut:

```sparql
SELECT (COUNT(*) AS ?total)
WHERE {
  ?subject ?predicate ?object
}
```

3. Klik tombol **Run**.

Konfigurasi berhasil jika query mengembalikan nilai `total` lebih besar dari
`0`. Endpoint yang akan digunakan aplikasi adalah:

```text
http://localhost:3030/movies/sparql
```

#### 4.7 Membuat ulang data RDF

Jika isi CSV berubah, buat ulang file Turtle:

```bash
python rdf.py
```

Setelah itu, hapus data lama dari dataset atau buat ulang dataset `movies`,
kemudian unggah kembali `output_with_classes_and_properties.ttl`. Hindari
mengunggah file yang sama berulang kali tanpa membersihkan dataset agar isi
database tetap mudah dipahami.

## Menjalankan Aplikasi

### Mengatur TMDB API key

Poster bersifat opsional. Tanpa API key, aplikasi tetap berjalan dan
menampilkan gambar placeholder. Untuk menampilkan poster, atur API key TMDB
melalui environment variable.

Windows PowerShell:

```powershell
$env:TMDB_API_KEY = "API_KEY_TMDB_MILIK_ANDA"
```

Linux atau macOS:

```bash
export TMDB_API_KEY="API_KEY_TMDB_MILIK_ANDA"
```

Jangan menulis API key langsung di `app.py` dan jangan melakukan commit API key
ke Git.

Endpoint Fuseki secara default adalah:

```text
http://localhost:3030/movies/sparql
```

Jika Fuseki menggunakan alamat lain, atur `SPARQL_ENDPOINT` sebelum menjalankan
aplikasi:

```powershell
$env:SPARQL_ENDPOINT = "http://localhost:3030/movies/sparql"
```

### Menjalankan Streamlit

Jalankan dari direktori utama proyek:

```bash
streamlit run app.py
```

Aplikasi biasanya tersedia di:

```text
http://localhost:8501
```

## Urutan Menjalankan Proyek

```text
CSV ──> rdf.py ──> file Turtle ──> Apache Jena Fuseki
 │                                      │
 └──> generate_movie_list.py            │ SPARQL
            │                            ▼
            └──> movie_list.pkl ──> Streamlit
```

Ringkasnya:

```bash
python generate_movie_list.py
python rdf.py
streamlit run app.py
```

`rdf.py` hanya perlu dijalankan kembali ketika data CSV berubah. Fuseki harus
tetap aktif selama aplikasi digunakan.

## Troubleshooting

### `FileNotFoundError: movie_list.pkl`

Versi aplikasi terbaru otomatis menggunakan `Datasets/Movies_less.csv` jika
cache belum tersedia. Jika masih menggunakan versi aplikasi lama, perbarui
`app.py` atau buat cache:

```bash
python generate_movie_list.py
```

Pastikan perintah dijalankan dari direktori yang berisi `app.py`.

### Tidak dapat terhubung ke endpoint SPARQL

Pastikan:

- Fuseki sedang berjalan.
- Dataset bernama `movies`.
- File Turtle sudah diunggah.
- `http://localhost:3030/movies/sparql` dapat diakses.

### `'java' is not recognized`

Pasang JDK 21:

```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```

Tutup terminal, buka PowerShell baru, lalu pastikan Java tersedia:

```powershell
java -version
```

Setelah versi Java tampil, jalankan kembali Fuseki:

```powershell
cd C:\apache-jena-fuseki-6.1.0
.\fuseki-server.bat
```

### Poster tidak tampil

Poster berasal dari TMDB API sehingga membutuhkan koneksi internet dan API key
yang masih aktif. Pada PowerShell, atur API key lalu jalankan Streamlit dari
terminal yang sama:

```powershell
$env:TMDB_API_KEY = "API_KEY_TMDB_MILIK_ANDA"
streamlit run app.py
```

### PowerShell menolak aktivasi virtual environment

Aktifkan hanya untuk sesi PowerShell saat ini:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Dataset dan Ontologi

Entitas utama:

- `Movie`
- `Actor`
- `Director`
- `Country`

Relasi dan properti utamanya meliputi:

- `title`, `overview`, `release_date`
- `runtime`, `budget`, `revenue`
- `genre`, `original_language`
- `directedBy`, `hasActor`, `producedIn`

## Catatan Keamanan

- Jangan membuka file `.pkl` dari sumber yang tidak dipercaya.
- Jangan melakukan commit API key.
- Untuk deployment, pindahkan TMDB API key ke `.streamlit/secrets.toml` atau
  environment variable.

## Lisensi

Proyek ini disediakan untuk keperluan pembelajaran dan demonstrasi teknologi
RDF, SPARQL, dan knowledge graph.

## Kontributor

Team Itihaad — University Project
