# Smart Citation & Reference Agent (SCRA)

SCRA (Smart Citation & Reference Agent) is a tool for automating the generation of citations and bibliographies. It is available in two forms: a command-line interface (CLI) for direct usage, and an HTTP API server for integration into multi-agent systems. The tool accepts various forms of reference input, validates metadata, detects the source type, and produces formatted citations in IEEE or APA style. It uses the CrossRef API to retrieve metadata for DOIs and titles, and applies rule-based logic for source detection and citation formatting.

---

## Daftar Isi

- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Cara Penggunaan (CLI)](#cara-penggunaan-cli)
- [API Server](#api-server)
- [Jenis Input](#jenis-input)
- [Alur Kerja Agent](#alur-kerja-agent)
- [Style Sitasi](#style-sitasi)
- [Format Output](#format-output)
- [Keterbatasan](#keterbatasan)

---

## Persyaratan Sistem

SCRA berjalan pada Python 3.8 atau yang lebih baru. Terdapat dua mode penggunaan dengan persyaratan yang berbeda.

**Mode CLI (Command Line):** Tidak memerlukan pustaka eksternal. Seluruh fungsionalitas CLI dibangun di atas modul standar Python (`urllib`, `json`, `re`, `argparse`, `datetime`).

**Mode API Server:** Memerlukan FastAPI dan uvicorn. Instalasi dapat dilakukan melalui `pip install -r requirements-api.txt`.

Sistem operasi yang didukung mencakup Windows, macOS, dan Linux.

---

## Instalasi

SCRA tidak memerlukan proses instalasi khusus. Cukup unduh atau salin seluruh direktori proyek ke sistem Anda.

Masuk ke direktori proyek dan pastikan Python tersedia di lingkungan Anda.

```
cd scra
python --version
```

Tidak ada perintah `pip install` yang diperlukan.

---

## Cara Penggunaan (CLI)

SCRA menyediakan antarmuka CLI yang dijalankan melalui terminal. Berikut adalah bentuk umum perintah:

```
python main.py [input] [--style ieee|apa] [--output text|json] [--file FILE] [--interactive]
```

Jika tidak ada argumen yang diberikan, SCRA akan menampilkan pesan bantuan yang berisi daftar opsi yang tersedia.

### Mode Dasar

Penggunaan paling sederhana adalah dengan memberikan satu referensi sebagai argumen posisi.

```
python main.py "10.1038/nature14236"
```

SCRA akan mendeteksi jenis input secara otomatis, mengambil metadata melalui CrossRef API, dan menghasilkan sitasi dalam format IEEE.

### Mode File

Apabila Anda memiliki banyak referensi, Anda dapat menyimpannya dalam sebuah file JSON dan memberikannya ke SCRA melalui opsi `--file`.

```
python main.py --file daftar-referensi.json --style apa
```

Format file JSON dapat berupa larik (array) yang berisi campuran string (DOI, URL, judul) dan objek metadata.

```json
[
    "10.1038/nature14236",
    {"title": "Deep Learning", "author": "Ian Goodfellow", "year": 2016, "publisher": "MIT Press"},
    "https://github.com/microsoft/vscode"
]
```

### Mode Interaktif

Opsi `--interactive` menjalankan SCRA dalam mode dialog. Pengguna dapat memasukkan referensi satu per satu secara berulang hingga mengetik `exit` atau `quit`.

```
python main.py --interactive --style apa
```

Setelah masuk ke mode interaktif, SCRA akan menampilkan prompt `>>>`. Setiap referensi yang dimasukkan akan langsung diproses dan hasilnya ditampilkan sebelum prompt berikutnya muncul.

---

## API Server

SCRA juga tersedia dalam bentuk HTTP API server yang dapat diintegrasikan ke dalam sistem Multi-Agent. Server ini dibangun menggunakan FastAPI dan telah di-deploy di alamat berikut.

```
Production : https://smart-citation-agent-production.up.railway.app
Dokumentasi : https://smart-citation-agent-production.up.railway.app/docs
```

### Endpoint

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/health` | Memeriksa status kesehatan server |
| `POST` | `/process` | Memproses referensi dan menghasilkan sitasi |

### Format Request

Server menerima JSON dengan struktur sebagai berikut.

```json
{
    "task_id": "req-12345-abc",
    "agent_type": "citation_reference",
    "payload": {
        "url": "",
        "keyword": "ieee",
        "raw_text": "10.1038/nature14236"
    }
}
```

### Format Response

Response sukses dikembalikan dalam format berikut.

```json
{
    "status": "success",
    "task_id": "req-12345-abc",
    "data": {
        "result": "[1] V. Mnih et al., ...",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

Dokumentasi API yang lebih lengkap tersedia di `API_DOKUMENTASI.md`.

### Menjalankan Server Secara Lokal

```
pip install -r requirements-api.txt
python agent_server.py
```

Server akan berjalan pada `http://127.0.0.1:8000`.

---

## Jenis Input

SCRA mampu mengenali lima jenis input secara otomatis tanpa perlu penanda khusus. Deteksi dilakukan berdasarkan pola string yang diberikan.

### DOI

DOI (Digital Object Identifier) adalah identifier permanen yang digunakan untuk dokumen akademik. SCRA mengenali DOI melalui pola `10.xxxx/xxxxx`.

```
python main.py "10.1038/nature14236"
```

SCRA akan mengirim permintaan ke CrossRef API untuk mengambil metadata lengkap termasuk judul, penulis, tahun, jurnal, volume, nomor, dan halaman.

### URL

SCRA menerima URL dalam dua kategori.

URL yang mengandung DOI (seperti `doi.org/10.xxxx/xxxxx`) akan diekstrak DOI-nya dan diproses melalui CrossRef API. URL repository GitHub akan dideteksi sebagai sumber tipe repository, dan nama pemilik/repo akan diekstrak untuk digunakan sebagai judul.

```
python main.py "https://doi.org/10.1038/nature14236"
python main.py "https://github.com/microsoft/vscode"
```

Untuk URL lainnya, SCRA akan menghasilkan sitasi dasar yang mencantumkan URL dan tanggal akses.

### Judul

Judul publikasi dapat diberikan langsung sebagai argumen. SCRA akan mencari judul tersebut melalui CrossRef API dan mengambil hasil dengan skor kecocokan tertinggi.

```
python main.py "Attention Is All You Need"
```

Apabila skor kecocokan yang dikembalikan oleh CrossRef rendah (di bawah 50), SCRA akan menambahkan peringatan pada hasil akhir.

### Metadata Manual

Metadata dapat diberikan dalam format JSON objek. Hal ini berguna apabila referensi tidak tersedia di CrossRef atau apabila pengguna ingin menentukan sendiri nilai-nilai metadata.

```
python main.py '{"title": "Deep Learning", "author": "Ian Goodfellow", "year": 2016, "publisher": "MIT Press"}'
```

Field yang dikenali meliputi `title`, `author` (string atau larik), `year`, `publisher`, `doi`, `url`, `volume`, `issue`, `pages`, dan `source_type`. Apabila input JSON tidak valid atau tidak memiliki field `title`, SCRA akan mengembalikan peringatan.

### Banyak Referensi

Untuk memproses banyak referensi sekaligus, gunakan opsi `--file` dengan file JSON yang berisi larik referensi. Larik tersebut dapat berisi campuran string (DOI, URL, judul) dan objek metadata.

```
python main.py --file daftar-referensi.json
```

---

## Alur Kerja Agent

SCRA tidak menghasilkan sitasi secara langsung. Setiap input melewati serangkaian tahapan pemrosesan yang terdiri dari validasi, analisis, pengambilan keputusan, dan format akhir. Berikut adalah alur kerja yang dilalui oleh setiap referensi.

### 1. Receive Input

SCRA menerima input dari pengguna melalui argumen terminal, file, atau mode interaktif. Pada tahap ini belum ada pemrosesan yang dilakukan; input hanya diterima dan diteruskan ke tahap berikutnya.

### 2. Input Validation

SCRA memeriksa validitas input berdasarkan jenis yang terdeteksi. Untuk DOI, format harus sesuai dengan pola `10.xxxx/xxxxx`. Untuk URL, pola harus diawali dengan `http://` atau `https://`. Untuk metadata JSON, struktur harus dapat diuraikan dan mengandung field yang diperlukan.

Apabila input tidak valid, SCRA akan mencatat peringatan dan melanjutkan pemrosesan dengan metadata yang minimal.

### 3. Source Detection

SCRA menentukan jenis sumber referensi menggunakan aturan berbasis pola domain. Berikut adalah beberapa contoh pemetaan:

- Domain `ieee.org`, `acm.org`, `springer.com`, `nature.com`, dan domain akademik lainnya diklasifikasikan sebagai `journal`.
- Domain `arxiv.org`, `biorxiv.org`, `medrxiv.org` diklasifikasikan sebagai `preprint`.
- Domain `github.com`, `gitlab.com`, `bitbucket.org` diklasifikasikan sebagai `repository`.
- Domain `wikipedia.org`, `medium.com`, dan domain blog lainnya diklasifikasikan sebagai `website`.

Untuk input DOI dan judul, jenis sumber diasumsikan sebagai `journal` karena kedua jenis input ini umumnya merujuk pada publikasi akademik.

### 4. Metadata Analysis

SCRA mengambil atau mengekstrak metadata dari input yang diberikan. Terdapat empat mekanisme yang digunakan bergantung pada jenis input.

Untuk DOI, SCRA mengirim permintaan ke endpoint `https://api.crossref.org/works/{doi}`. CrossRef akan mengembalikan metadata lengkap yang mencakup judul, daftar penulis, tahun publikasi, nama jurnal atau penerbit, volume, nomor, halaman, dan DOI.

Untuk judul, SCRA mengirim permintaan pencarian ke `https://api.crossref.org/works?query.title={title}` dan mengambil hasil dengan skor kecocokan tertinggi.

Untuk URL yang mengandung DOI (seperti tautan `doi.org`), SCRA mengekstrak DOI dari URL terlebih dahulu sebelum mengirim permintaan ke CrossRef.

Untuk URL repository GitHub, SCRA mengekstrak informasi pemilik dan nama repository dari URL dan menggunakannya sebagai judul.

### 5. Metadata Validation

SCRA memeriksa kelengkapan metadata yang diperoleh. Field yang diperiksa meliputi judul, penulis, tahun, dan penerbit. Apabila terdapat field yang kosong, SCRA akan menambahkan peringatan pada hasil akhir. Untuk tahun yang tidak ditemukan, SCRA akan menggunakan nilai `n.d.` (no date) sebagai pengganti.

### 6. Citation Style Selection

Pengguna dapat memilih gaya sitasi melalui opsi `--style`. Dua gaya yang didukung adalah IEEE (default) dan APA. Gaya ini akan digunakan oleh SCRA pada tahap pembentukan sitasi.

### 7. Citation Generation

SCRA menghasilkan teks sitasi berdasarkan metadata yang telah divalidasi dan gaya yang dipilih. Setiap referensi akan diberikan nomor urut sesuai dengan urutan kemunculannya.

Untuk gaya IEEE, format sitasi jurnal adalah sebagai berikut.

```
[N] A. Lastname, "Title," Journal, vol. x, no. y, pp. z, year.
```

Untuk gaya APA, format sitasi jurnal adalah sebagai berikut.

```
Lastname, A. (year). Title. Journal, x(y), z.
```

SCRA menangani berbagai jenis sumber termasuk jurnal, konferensi, buku, preprint, repository, dan website. Masing-masing memiliki format sitasi yang berbeda.

### 8. Bibliography Builder

Apabila terdapat lebih dari satu referensi, SCRA akan menyusun daftar pustaka. Proses ini mencakup tiga langkah.

Pertama, SCRA menghapus referensi yang duplikat berdasarkan DOI atau judul. Kedua, SCRA mengurutkan referensi dan memberi nomor urut. Ketiga, SCRA menggabungkan seluruh sitasi menjadi satu blok teks daftar pustaka.

### 9. Output Validation

SCRA melakukan pemeriksaan akhir terhadap hasil yang dihasilkan. Pemeriksaan meliputi konsistensi nomor urut dan ketersediaan teks sitasi untuk setiap referensi. Apabila ditemukan masalah, SCRA akan mencatatnya dalam daftar isu pada output.

### 10. Return Result

SCRA mengembalikan hasil akhir dalam format teks atau JSON sesuai dengan opsi `--output` yang dipilih. Hasil mencakup daftar sitasi, daftar pustaka, metadata setiap referensi, dan seluruh peringatan yang muncul selama pemrosesan.

---

## Style Sitasi

SCRA mendukung dua gaya sitasi akademik yang umum digunakan.

### IEEE

Gaya IEEE (Institute of Electrical and Electronics Engineers) menggunakan nomor urut dalam kurung siku. Nomor urut diberikan berdasarkan urutan kemunculan referensi dalam daftar. Berikut adalah contoh sitasi untuk berbagai jenis sumber.

```
[1] V. Mnih et al., "Human-level control through deep reinforcement learning," Nature, vol. 518, no. 7540, pp. 529-533, 2015.
[2] "microsoft/vscode," GitHub [Online]. Available: https://github.com/microsoft/vscode. Accessed: Jul 16, 2026.
```

Penulisan nama penulis menggunakan inisial depan diikuti dengan nama belakang. Apabila jumlah penulis lebih dari enam, nama enam penulis pertama ditampilkan diikuti dengan `et al.`.

### APA

Gaya APA (American Psychological Association) menggunakan format nama-belakang, inisial-depan diikuti dengan tahun dalam tanda kurung. Berikut adalah contoh sitasi untuk berbagai jenis sumber.

```
Mnih, V. et al. (2015). Human-level control through deep reinforcement learning. Nature, 518(7540), 529-533. https://doi.org/10.1038/nature14236
```

---

## Format Output

SCRA menyediakan dua format output yang dapat dipilih melalui opsi `--output`.

### Format Teks (Default)

Format teks menampilkan hasil dalam bentuk yang mudah dibaca manusia. Output terdiri dari tiga bagian.

Bagian pertama adalah `=== Citations (IEEE) ===` yang menampilkan daftar sitasi dengan nomor urut. Bagian kedua adalah `=== Bibliography ===` yang menampilkan daftar pustaka lengkap. Bagian ketiga adalah `=== Warnings ===` yang menampilkan seluruh peringatan yang muncul selama pemrosesan. Bagian ketiga hanya ditampilkan apabila terdapat peringatan.

### Format JSON

Format JSON menghasilkan struktur data yang dapat diuraikan oleh program lain. Struktur output JSON adalah sebagai berikut.

```json
{
    "status": "success",
    "citation_style": "ieee",
    "citations": ["..."],
    "bibliography": "...",
    "warnings": ["..."],
    "references": [
        {
            "title": "...",
            "authors": ["..."],
            "year": "...",
            "doi": "...",
            "source_type": "..."
        }
    ]
}
```

Field `citations` berisi larik teks sitasi untuk setiap referensi. Field `bibliography` berisi teks daftar pustaka yang telah digabungkan. Field `warnings` berisi seluruh peringatan dan isu yang ditemukan selama pemrosesan. Field `references` berisi metadata setiap referensi dalam bentuk objek.

---

## Keterbatasan

SCRA versi saat ini memiliki beberapa keterbatasan yang perlu diketahui.

Untuk URL yang tidak mengandung DOI dan bukan merupakan repository GitHub, SCRA hanya dapat menghasilkan sitasi dasar yang mencantumkan URL dan tanggal akses tanpa metadata lengkap. Pengguna disarankan untuk memberikan DOI atau judul untuk referensi dari website umum.

Deteksi jenis sumber sepenuhnya berdasarkan aturan pola domain dan tidak menggunakan analisis konten. Beberapa sumber mungkin tidak terklasifikasikan dengan tepat apabila domainnya tidak tercakup dalam aturan yang tersedia.

CrossRef API bersifat gratis tetapi memiliki batas laju permintaan (rate limit). SCRA belum menerapkan mekanisme antrean atau penundaan untuk permintaan dalam jumlah besar. Untuk daftar referensi yang sangat panjang, disarankan untuk memproses secara bertahap.

Penanganan nama penulis dengan nama belakang ganda (seperti "García Sánchez") masih menggunakan pendekatan sederhana yaitu mengambil elemen terakhir sebagai nama belakang. Hal ini mungkin tidak akurat untuk beberapa nama dengan struktur tertentu.

Fitur-fitur yang belum didukung meliputi integrasi dengan Zotero atau Mendeley, ekspor ke format BibTeX atau RIS, pencarian literatur otomatis, dan deteksi bahasa.
