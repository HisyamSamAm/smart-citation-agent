# Rencana Pengujian SCRA Agent Server

Dokumen ini berisi tahapan pengujian untuk memverifikasi bahwa SCRA Agent Server berfungsi sesuai dengan API Contract yang ditetapkan oleh sistem Multi-Agent Joki Tugas AI.

---

## Daftar Isi

- [Prasyarat](#prasyarat)
- [Tahap 1: Verifikasi Server dan Health Check](#tahap-1-verifikasi-server-dan-health-check)
- [Tahap 2: Pengujian Endpoint /process](#tahap-2-pengujian-endpoint-process)
- [Tahap 3: Verifikasi API Contract](#tahap-3-verifikasi-api-contract)
- [Tahap 4: Pengujian CORS](#tahap-4-pengujian-cors)
- [Tahap 5: Pengujian Beban dan Timeout](#tahap-5-pengujian-beban-dan-timeout)
- [Tahap 6: Deployment ke Production](#tahap-6-deployment-ke-production)

---

## Prasyarat

 sebelum memulai pengujian, pastikan hal-hal berikut telah terpenuhi.

1. Server SCRA Agent berjalan pada `http://127.0.0.1:8000` untuk pengujian lokal, atau URL production `https://smart-citation-agent-production.up.railway.app` untuk pengujian jarak jauh.
2. FastAPI dan uvicorn telah terinstal (lihat `requirements-api.txt` untuk daftar dependensi).
3. Koneksi internet aktif untuk mengakses CrossRef API.
4. Terminal atau PowerShell siap digunakan untuk mengirim request.

---

## Tahap 1: Verifikasi Server dan Health Check

Tujuan: memastikan server berjalan dan endpoint dasar dapat diakses.

### 1.1 Akses Dokumentasi Swagger

Buka browser dan akses URL berikut.

```
http://127.0.0.1:8000/docs
```

Yang diverifikasi:

- Halaman Swagger UI muncul tanpa error.
- Terdapat dua endpoint yang terdaftar: `GET /health` dan `POST /process`.
- Skema request dan response ditampilkan dengan benar.

### 1.2 Health Check

Kirim request GET ke endpoint health.

```
GET http://127.0.0.1:8000/health
```

Response yang diharapkan:

```json
{
    "status": "healthy",
    "agent": "citation_reference",
    "input_type": "text",
    "output_type": "text"
}
```

Yang diverifikasi:

- HTTP status code 200.
- Field `status` bernilai `"healthy"`.
- Field `agent` bernilai `"citation_reference"`.
- Field `input_type` dan `output_type` bernilai `"text"` sesuai tabel pemetaan agent.

---

## Tahap 2: Pengujian Endpoint /process

Tujuan: memastikan endpoint pemrosesan referensi bekerja untuk berbagai jenis input.

### 2.1 Referensi Tunggal via DOI

Kirim satu DOI melalui field `raw_text`.

```powershell
$body = @{
    task_id = "req-001"
    agent_type = "citation_reference"
    payload = @{
        raw_text = "10.1038/nature14236"
        keyword = "ieee"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/process" `
  -Method POST -Body $body -ContentType "application/json"
```

Yang diverifikasi:

- Response status `"success"`.
- `data.result` berisi sitasi dalam format IEEE yang valid.
- `data.file_url` bernilai `null`.
- `task_id` pada response sama dengan yang dikirim.

### 2.2 Referensi via Judul

Kirim judul publikasi sebagai input.

```json
{
    "task_id": "req-002",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "Attention Is All You Need",
        "keyword": "apa"
    }
}
```

Yang diverifikasi:

- CrossRef API berhasil menemukan judul.
- Response berisi sitasi dalam format APA.
- Apabila skor kecocokan rendah, peringatan disertakan dalam output.

### 2.3 Referensi via URL

Kirim URL yang mengandung DOI.

```json
{
    "task_id": "req-003",
    "agent_type": "citation_reference",
    "payload": {
        "url": "https://doi.org/10.1038/nature14236",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- DOI berhasil diekstrak dari URL.
- Metadata diambil dari CrossRef API.
- Sitasi yang dihasilkan identik dengan pengujian 2.1.

### 2.4 Banyak Referensi (Multi-line)

Kirim beberapa referensi dalam satu request, dipisahkan oleh baris baru.

```json
{
    "task_id": "req-004",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "10.1038/nature14236\n10.1145/3368089.3409741",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- Kedua referensi diproses.
- Output berisi dua sitasi dengan nomor urut `[1]` dan `[2]`.
- Bibliography tersusun dengan rapi.

### 2.5 Banyak Referensi via JSON Array

Kirim referensi dalam format JSON array melalui `raw_text`.

```json
{
    "task_id": "req-005",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "[\"10.1038/nature14236\", \"10.1145/3368089.3409741\"]",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- JSON array berhasil diurai.
- Setiap elemen array diproses sebagai referensi terpisah.
- Output identik dengan pengujian 2.4.

### 2.6 Referensi dengan Metadata Manual

Kirim metadata dalam format JSON objek.

```json
{
    "task_id": "req-006",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "{\"title\": \"Deep Learning\", \"author\": \"Ian Goodfellow\", \"year\": 2016, \"publisher\": \"MIT Press\"}",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- Metadata diurai tanpa perlu akses CrossRef.
- Sitasi dihasilkan berdasarkan data yang diberikan.

### 2.7 Repository GitHub

Kirim URL repository GitHub.

```json
{
    "task_id": "req-007",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "https://github.com/microsoft/vscode",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- Nama repository berhasil diekstrak dari URL.
- Sumber terdeteksi sebagai `repository`.
- Sitasi menyertakan URL dan tanggal akses.

### 2.8 Referensi Tidak Ditemukan

Kirim DOI yang tidak valid atau tidak terdaftar.

```json
{
    "task_id": "req-008",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "10.9999/invalid-doi-test-12345",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- Response tetap `"success"` (tidak crash).
- Peringatan disertakan dalam output bahwa DOI tidak ditemukan.
- Sitasi tetap dihasilkan dengan informasi yang tersedia.

### 2.9 Payload Kosong

Kirim request tanpa `raw_text` dan `url`.

```json
{
    "task_id": "req-009",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "",
        "keyword": "ieee"
    }
}
```

Yang diverifikasi:

- HTTP status code 400.
- Response status `"error"`.
- Pesan error menjelaskan bahwa payload kosong.

### 2.10 Gaya APA

Uji coba dengan gaya APA untuk referensi yang sama dengan pengujian 2.1.

```json
{
    "task_id": "req-010",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "10.1038/nature14236",
        "keyword": "apa"
    }
}
```

Yang diverifikasi:

- Format sitasi menggunakan gaya APA.
- Tidak ada elemen format IEEE yang tercampur.

---

## Tahap 3: Verifikasi API Contract

Tujuan: memastikan response sesuai dengan standar yang ditetapkan dalam dokumen integrasi agent.

### 3.1 Response Sukses

Setiap response sukses harus memiliki struktur berikut.

```json
{
    "status": "success",
    "task_id": "req-xxx",
    "data": {
        "result": "Teks hasil proses agent",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

Yang diverifikasi:

- Field `status` bertipe string dan bernilai `"success"`.
- Field `task_id` bertipe string dan nilainya sama persis dengan request.
- Field `data` bertipe object dan berisi `result` (string) serta `file_url` (null atau string URL).
- Field `message` bertipe string.

### 3.2 Response Error

Setiap response error harus memiliki struktur berikut.

```json
{
    "status": "error",
    "task_id": "req-xxx",
    "data": null,
    "message": "Deskripsi alasan error"
}
```

Yang diverifikasi:

- Field `status` bertipe string dan bernilai `"error"`.
- Field `data` bernilai `null`.
- Field `message` berisi deskripsi error yang jelas.
- HTTP status code sesuai dengan jenis error (400 untuk bad request, 500 untuk internal error).

### 3.3 Pemetaan Tipe Data

Berdasarkan tabel pemetaan agent, `citation_reference` memiliki spesifikasi berikut.

| Aspek | Spesifikasi |
|-------|-------------|
| Nama agent | `citation_reference` |
| Tipe input | `text` |
| Tipe output | `text` |
| Endpoint | `POST /process` |
| Tanpa file output | `file_url: null` |

Yang diverifikasi:

- Endpoint yang diakses adalah `POST /process`.
- Input diambil dari `payload.raw_text` (tipe `text`).
- Output dikembalikan melalui `data.result` (tipe `text`).
- `data.file_url` bernilai `null` karena agent tidak menghasilkan file.

---

## Tahap 4: Pengujian CORS

Tujuan: memastikan konfigurasi CORS berfungsi dengan benar.

### 4.1 Verifikasi Header CORS

Kirim request OPTIONS ke endpoint `/process` dan periksa header response.

```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/process" `
  -Method OPTIONS `
  -Headers @{"Origin" = "https://jokitugas.bananaunion.web.id"}

$response.Headers
```

Yang diverifikasi:

- Header `Access-Control-Allow-Origin` bernilai `https://jokitugas.bananaunion.web.id`.
- Header `Access-Control-Allow-Methods` mencakup `POST`, `GET`, `OPTIONS`.
- Header `Access-Control-Allow-Headers` mencakup `Content-Type`, `Authorization`.

### 4.2 Origin Tidak Terdaftar

Kirim request dengan origin yang tidak terdaftar.

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/process" `
  -Method OPTIONS `
  -Headers @{"Origin" = "https://situs-tidak-dikenal.com"}
```

Yang diverifikasi:

- Header `Access-Control-Allow-Origin` tidak menyertakan origin tersebut.
- Request dari origin tidak dikenal tetap diblokir.

---

## Tahap 5: Pengujian Beban dan Timeout

Tujuan: memastikan agent dapat menangani beberapa request dalam waktu 30 detik.

### 5.1 Waktu Respon

Kirim request dengan referensi yang membutuhkan akses CrossRef dan ukur waktu respon.

```powershell
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
Invoke-RestMethod -Uri "http://127.0.0.1:8000/process" `
  -Method POST -Body $body -ContentType "application/json"
$stopwatch.Stop()
$stopwatch.Elapsed.TotalSeconds
```

Yang diverifikasi:

- Waktu respon kurang dari 30 detik.
- Response berhasil dikembalikan tanpa timeout.

### 5.2 Request Berurutan

Kirim 5 request secara berurutan tanpa jeda.

Yang diverifikasi:

- Seluruh request mendapatkan response sukses.
- Tidak ada request yang mengalami timeout atau error.

---

## Tahap 6: Deployment ke Production

Tujuan: men-deploy agent ke hosting cloud gratis dan memastikan dapat diakses oleh orkestrator.

### 6.1 Persiapan Deployment

Sebelum deployment, pastikan hal-hal berikut.

- File `requirements-api.txt` berisi daftar dependensi yang benar.
- Kode server tidak mengandung konfigurasi yang bersifat lokal (seperti `0.0.0.0`).
- Port yang digunakan dapat dikonfigurasi melalui environment variable.

Rekomendasi untuk penanganan port pada kode deployment:

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 6.2 Platform Deployment

Berikut adalah platform yang dapat digunakan beserta langkah-langkahnya.

| Platform | Biaya | Catatan |
|----------|-------|---------|
| Railway | Gratis | Hubungkan repository GitHub, Railway akan mendeteksi `requirements-api.txt` secara otomatis. |
| Render | Gratis | Buat Web Service, set start command menjadi `uvicorn agent_server:app --host 0.0.0.0 --port $PORT`. |
| Hugging Face Spaces | Gratis | Gunakan Docker SDK image `python:3.11` dengan start command `uvicorn agent_server:app --host 0.0.0.0 --port 7860`. |
| Fly.io | Gratis (dengan kartu kredit) | Gunakan `fly launch` dan konfigurasi `fly.toml`. |

### 6.3 Verifikasi Pasca Deployment

Setelah berhasil di-deploy, lakukan verifikasi berikut.

- Health check melalui URL publik: `GET https://smart-citation-agent-production.up.railway.app/health`.
- Test process dengan referensi melalui: `POST https://smart-citation-agent-production.up.railway.app/process`.
- Pastikan CORS berfungsi dengan origin orkestrator.
- Laporkan URL publik ke tim API Gateway untuk didaftarkan pada file `.env` orkestrator.

```
Nama Agent : citation_reference
Endpoint   : POST https://smart-citation-agent-production.up.railway.app/process
Tipe Input : text
Tipe Output: text
```

---

## Hasil Pengujian

Pengujian dilakukan terhadap deployment production di `https://smart-citation-agent-production.up.railway.app` pada tanggal 20 Juli 2026.

### Servis

| No | Skenario | Target | Hasil |
|:--:|----------|--------|:-----:|
| 1.1 | Dokumentasi Swagger | `/docs` dan `/openapi.json` tersedia | LULUS |
| 1.2 | Health check | Status `healthy`, field lengkap | LULUS |

### Fungsional

| No | Skenario | Input | Hasil |
|:--:|----------|-------|:-----:|
| 2.1 | DOI tunggal | `10.1038/nature14236` (IEEE) | LULUS |
| 2.2 | Judul publikasi | `Attention Is All You Need` (APA) | LULUS |
| 2.3 | URL via payload | `url` field dengan GitHub repo | LULUS |
| 2.4 | Multi-line | 2 DOIs dipisah baris baru | LULUS |
| 2.5 | JSON array | Array berisi 2 DOI | LULUS |
| 2.6 | Metadata manual | Objek JSON `{title, author, year, publisher}` | LULUS |
| 2.7 | Repository GitHub | URL GitHub terekstrak nama repo | LULUS |
| 2.8 | DOI tidak valid | `10.9999/invalid-doi` (warning dihasilkan) | LULUS |
| 2.9 | Payload kosong | `raw_text: ""` (HTTP 400) | LULUS |
| 2.10 | Gaya APA | Format APA, tidak ada elemen IEEE | LULUS |

### API Contract

| No | Skenario | Verifikasi | Hasil |
|:--:|----------|------------|:-----:|
| 3.1 | Response sukses | Status `success`, `task_id` cocok, `file_url` null | LULUS |
| 3.2 | Response error | Status `error`, data null, HTTP 400 | LULUS |
| 3.3 | Pemetaan tipe data | Input text, output text, endpoint POST | LULUS |

### CORS

| No | Skenario | Hasil |
|:--:|----------|:-----:|
| 4.1 | Header CORS valid (`Allow-Origin`) | LULUS |

### Performa

| No | Skenario | Detail | Hasil |
|:--:|----------|--------|:-----:|
| 5.1 | Waktu respon | 1.38 detik (batas 30 detik) | LULUS |
| 5.2 | Request berurutan (5x) | Rata-rata 0.92 detik/request, total 4.59 detik | LULUS |

### Deployment

| No | Skenario | Hasil |
|:--:|----------|:-----:|
| 6.1 | Persiapan deployment | LULUS |
| 6.2 | Deploy ke Railway | LULUS |
| 6.3 | Verifikasi pasca deploy | LULUS |
