# Dokumentasi API Agent Citation Reference

**Agent:** `citation_reference`  
**Versi API:** 1.0.0  
**Tipe Input:** `text`  
**Tipe Output:** `text`  

Dokumen ini diperuntukkan bagi tim pengelola API Gateway (orkestrator) yang perlu mengintegrasikan agent Citation Reference ke dalam pipeline Multi-Agent System Joki Tugas AI.

---

## Daftar Isi

- [Base URL](#base-url)
- [Autentikasi](#autentikasi)
- [Endpoint](#endpoint)
- [Struktur Request](#struktur-request)
- [Struktur Response](#struktur-response)
- [Kode Status HTTP](#kode-status-http)
- [Skenario Penggunaan](#skenario-penggunaan)
- [Pemetaan Agent](#pemetaan-agent)
- [Integrasi ke Pipeline](#integrasi-ke-pipeline)

---

## Base URL

Berikut adalah base URL untuk setiap environment.

| Environment | URL |
|-------------|-----|
| **Production** | `https://<domain-production>` |
| **Staging** | `https://<domain-staging>` |
| **Local Development** | `http://127.0.0.1:8000` |

Base URL production akan diberikan setelah proses deployment selesai.

---

## Autentikasi

Agent ini tidak memerlukan autentikasi khusus. Seluruh request diterima secara publik melalui endpoint yang tersedia.

---

## Endpoint

### GET /health

Endpoint untuk memeriksa status kesehatan agent.

**Contoh Request:**
```
GET https://<domain>/health
```

**Response:**
```json
{
    "status": "healthy",
    "agent": "citation_reference",
    "input_type": "text",
    "output_type": "text"
}
```

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `status` | string | Nilai `"healthy"` jika agent berjalan normal. |
| `agent` | string | Nama agent, selalu `"citation_reference"`. |
| `input_type` | string | Tipe data input agent, selalu `"text"`. |
| `output_type` | string | Tipe data output agent, selalu `"text"`. |

### POST /process

Endpoint utama untuk memproses referensi dan menghasilkan sitasi.

**Contoh Request:**
```
POST https://<domain>/process
Content-Type: application/json
```

---

## Struktur Request

### Body Request

```json
{
    "task_id": "req-12345-abc",
    "agent_type": "citation_reference",
    "payload": {
        "url": "",
        "keyword": "ieee",
        "raw_text": "10.1038/nature14236"
    },
    "metadata": {
        "sender": "orchestrator",
        "timestamp": 1689694097
    }
}
```

### Deskripsi Field

| Field | Tipe | Wajib | Deskripsi |
|-------|------|:-----:|-----------|
| `task_id` | string | Ya | ID unik yang diberikan oleh orkestrator. Akan dikembalikan dalam response secara persis. |
| `agent_type` | string | Ya | Harus bernilai `"citation_reference"`. |
| `payload.url` | string | Tidak | URL sumber referensi. Digunakan jika `raw_text` tidak diisi. |
| `payload.keyword` | string | Tidak | Gaya sitasi. Nilai yang diterima: `"ieee"` atau `"apa"`. Default: `"ieee"`. |
| `payload.raw_text` | string | Tidak | Teks berisi satu atau lebih referensi. Format dijelaskan pada bagian [Format Input Referensi](#format-input-referensi). |
| `metadata` | object | Tidak | Informasi tambahan dari pengirim. |

### Format Input Referensi

Field `raw_text` dapat diisi dalam beberapa format berikut.

**Satu referensi per baris (multi-line):**

Setiap baris diproses sebagai satu referensi terpisah.

```
10.1038/nature14236
10.1145/3368089.3409741
Attention Is All You Need
```

**JSON Array:**

Seluruh konten `raw_text` dapat berupa JSON array yang berisi campuran string (DOI, URL, judul) atau objek metadata.

```json
[
    "10.1038/nature14236",
    {"title": "Deep Learning", "author": "Ian Goodfellow", "year": 2016},
    "https://github.com/microsoft/vscode"
]
```

**Objek Metadata Manual:**

Referensi tunggal dapat diberikan sebagai objek JSON dengan field yang ditentukan pengguna.

```json
{"title": "Deep Learning", "author": "Ian Goodfellow", "year": 2016, "publisher": "MIT Press"}
```

Field yang dikenali pada objek metadata:

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `title` | string | Judul publikasi. |
| `author` | string atau array | Nama penulis, dapat berupa string (dipisah koma) atau array of strings. |
| `year` | number atau string | Tahun publikasi. |
| `publisher` | string | Nama penerbit atau jurnal. |
| `doi` | string | Digital Object Identifier. |
| `url` | string | URL publikasi. |
| `volume` | string | Volume jurnal. |
| `issue` | string | Nomor issue jurnal. |
| `pages` | string | Rentang halaman. |
| `source_type` | string | Jenis sumber (`journal`, `conference`, `book`, `repository`, `website`). |

### Aturan Prioritas Input

Apabila kedua field `url` dan `raw_text` diisi, agent akan memprioritaskan `raw_text` terlebih dahulu. Urutan prioritas adalah sebagai berikut.

1. `payload.raw_text` -- jika tidak kosong, gunakan sebagai input referensi.
2. `payload.url` -- jika `raw_text` kosong, gunakan URL sebagai input.
3. Jika keduanya kosong, agent mengembalikan response error HTTP 400.

---

## Struktur Response

### Response Sukses (HTTP 200)

```json
{
    "status": "success",
    "task_id": "req-12345-abc",
    "data": {
        "result": "=== Citations (IEEE) ===\n[1] V. Mnih et al., \"Human-level control through deep reinforcement learning,\" Nature, vol. 518, no. 7540, pp. 529-533, 2015.\n\n=== Bibliography ===\n[1] V. Mnih et al., ...\n",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `status` | string | `"success"` |
| `task_id` | string | Sama dengan `task_id` dari request. |
| `data.result` | string | Teks output berisi sitasi dan daftar pustaka. |
| `data.file_url` | null | Selalu `null` karena agent ini tidak menghasilkan file. |
| `message` | string | `"Pemrosesan berhasil"` |

### Response Error (HTTP 400)

Dikembalikan apabila payload tidak valid atau kosong.

```json
{
    "status": "error",
    "task_id": "req-12345-abc",
    "data": null,
    "message": "Payload kosong: tidak ada raw_text atau url"
}
```

### Response Error (HTTP 500)

Dikembalikan apabila terjadi kesalahan internal saat pemrosesan.

```json
{
    "status": "error",
    "task_id": "req-12345-abc",
    "data": null,
    "message": "Internal Server Error: <deskripsi error>"
}
```

---

## Kode Status HTTP

| Kode | Deskripsi |
|:----:|-----------|
| 200 | Request berhasil diproses. Response berisi sitasi dan daftar pustaka. |
| 400 | Request tidak valid. Payload kosong atau format tidak sesuai. |
| 405 | Method tidak diizinkan. Hanya `POST` yang diterima pada endpoint `/process`. |
| 500 | Terjadi kesalahan internal pada server agent. |

---

## Skenario Penggunaan

### Skenario 1: Satu Referensi DOI

Memproses satu DOI untuk menghasilkan sitasi IEEE.

**Request:**
```json
{
    "task_id": "req-001",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "10.1038/nature14236",
        "keyword": "ieee"
    }
}
```

**Response (disingkat):**
```json
{
    "status": "success",
    "task_id": "req-001",
    "data": {
        "result": "=== Citations (IEEE) ===\n[1] V. Mnih et al., \"Human-level control through deep reinforcement learning,\" Nature, vol. 518, no. 7540, pp. 529-533, 2015.",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

### Skenario 2: Banyak Referensi Multi-line

Memproses beberapa referensi yang dipisahkan oleh baris baru.

**Request:**
```json
{
    "task_id": "req-002",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "10.1038/nature14236\nAttention Is All You Need",
        "keyword": "apa"
    }
}
```

**Response (disingkat):**
```json
{
    "status": "success",
    "task_id": "req-002",
    "data": {
        "result": "=== Citations (APA) ===\nMnih, V. et al. (2015). ...\nVaswani, A. et al. (2025). ...",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

### Skenario 3: Referensi via URL

Menggunakan URL publikasi sebagai input.

**Request:**
```json
{
    "task_id": "req-003",
    "agent_type": "citation_reference",
    "payload": {
        "url": "https://github.com/microsoft/vscode",
        "keyword": "ieee"
    }
}
```

**Response (disingkat):**
```json
{
    "status": "success",
    "task_id": "req-003",
    "data": {
        "result": "=== Citations (IEEE) ===\n[1] \"microsoft/vscode,\" GitHub [Online], Available: https://github.com/microsoft/vscode, Accessed: Jul 20, 2026.",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

### Skenario 4: Metadata Manual

Menentukan metadata secara langsung tanpa melalui CrossRef.

**Request:**
```json
{
    "task_id": "req-004",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "{\"title\": \"Deep Learning\", \"author\": \"Ian Goodfellow\", \"year\": 2016, \"publisher\": \"MIT Press\"}",
        "keyword": "ieee"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "task_id": "req-004",
    "data": {
        "result": "=== Citations (IEEE) ===\n[1] I. Goodfellow, \"Deep Learning,\" MIT Press, 2016.",
        "file_url": null
    },
    "message": "Pemrosesan berhasil"
}
```

### Skenario 5: Payload Kosong

Orkestrator mengirim request tanpa data referensi.

**Request:**
```json
{
    "task_id": "req-005",
    "agent_type": "citation_reference",
    "payload": {
        "raw_text": "",
        "keyword": "ieee"
    }
}
```

**Response (HTTP 400):**
```json
{
    "status": "error",
    "task_id": "req-005",
    "data": null,
    "message": "Payload kosong: tidak ada raw_text atau url"
}
```

---

## Pemetaan Agent

Berdasarkan tabel pemetaan tipe data pada sistem Multi-Agent, agent ini memiliki spesifikasi sebagai berikut.

| Aspek | Spesifikasi |
|-------|-------------|
| Nama Agent | `citation_reference` |
| Tipe Input | `text` |
| Tipe Output | `text` |
| Method | `POST` |
| Endpoint | `/process` |
| Menghasilkan File | Tidak (file_url: null) |

### Posisi dalam Pipeline

Agent `citation_reference` menerima input teks dari agent sebelumnya dan mengembalikan teks berisi sitasi untuk agent selanjutnya. Karena tipe input dan output sama-sama `text`, agent ini dapat di-skip (bypass) oleh mekanisme Type-Safe Smart Skip apabila agent sebelumnya atau sesudahnya juga bertipe `text`.

Contoh pipeline yang mungkin:

```
literature_reviewer (text) → citation_reference (text) → qna_simulator (text)
```

Apabila `citation_reference` offline, orkestrator dapat melewatkannya karena output `literature_reviewer` (text) dapat langsung diteruskan ke `qna_simulator` (text).

---

## Integrasi ke Pipeline

### Langkah Registrasi

Tim API Gateway perlu mendaftarkan agent ini pada konfigurasi orkestrator melalui file `.env` atau mekanisme registrasi yang tersedia. Data yang diperlukan adalah sebagai berikut.

```
CITATION_REFERENCE_URL=https://<domain>/process
CITATION_REFERENCE_INPUT=text
CITATION_REFERENCE_OUTPUT=text
```

### Timeout

Agent ini memiliki batas waktu pemrosesan maksimal 30 detik sesuai ketentuan sistem. Apabila request memuat banyak referensi (lebih dari 10), waktu pemrosesan dapat bertambah karena setiap referensi memerlukan satu panggilan ke CrossRef API.

Rekomendasi jumlah referensi per request adalah 1 hingga 10 referensi untuk memastikan response dalam batas waktu yang ditentukan.

### CORS

Server agent telah mengaktifkan CORS dengan whitelist origin sebagai berikut.

```
Origin: https://jokitugas.bananaunion.web.id
Methods: POST, GET, OPTIONS
Headers: Content-Type, Authorization
```

Pastikan orkestrator mengirim request dari domain yang terdaftar agar tidak terkena CORS blocking.

---

## Contoh Kode Integrasi

### Go (Gin Gonic) -- Sesuai Stack Orkestrator

```go
type CitationPayload struct {
    URL     string `json:"url"`
    Keyword string `json:"keyword"`
    RawText string `json:"raw_text"`
}

type CitationRequest struct {
    TaskID    string          `json:"task_id"`
    AgentType string          `json:"agent_type"`
    Payload   CitationPayload `json:"payload"`
}

type CitationData struct {
    Result  string `json:"result"`
    FileURL *string `json:"file_url"`
}

type CitationResponse struct {
    Status  string       `json:"status"`
    TaskID  string       `json:"task_id"`
    Data    CitationData `json:"data"`
    Message string       `json:"message"`
}

func callCitationAgent(taskID, rawText, style string) (*CitationResponse, error) {
    url := os.Getenv("CITATION_REFERENCE_URL")
    body := CitationRequest{
        TaskID:    taskID,
        AgentType: "citation_reference",
        Payload: CitationPayload{
            RawText: rawText,
            Keyword: style,
        },
    }
    jsonBody, _ := json.Marshal(body)
    resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonBody))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    var result CitationResponse
    json.NewDecoder(resp.Body).Decode(&result)
    return &result, nil
}
```

### Python (FastAPI / Requests)

```python
import requests

def call_citation_agent(task_id: str, raw_text: str, style: str = "ieee") -> dict:
    url = "https://<domain>/process"
    payload = {
        "task_id": task_id,
        "agent_type": "citation_reference",
        "payload": {
            "raw_text": raw_text,
            "keyword": style,
        },
    }
    response = requests.post(url, json=payload, timeout=30)
    return response.json()
```

### Node.js (Express / Axios)

```javascript
const axios = require('axios');

async function callCitationAgent(taskId, rawText, style = 'ieee') {
    const url = 'https://<domain>/process';
    const payload = {
        task_id: taskId,
        agent_type: 'citation_reference',
        payload: {
            raw_text: rawText,
            keyword: style,
        },
    };
    const response = await axios.post(url, payload, { timeout: 30000 });
    return response.data;
}
```

---

## Catatan Penting

1. **Task ID** harus dikembalikan dalam response secara persis. Gunakan field ini untuk mencocokkan request dengan response pada sistem logging orkestrator.

2. **File URL** selalu bernilai `null` karena agent ini tidak menghasilkan file fisik. Orkestrator tidak perlu menunggu atau memproses field ini.

3. **Peringatan** disertakan dalam `data.result` bersama dengan sitasi. Orkestrator dapat menampilkan peringatan ini kepada user atau mengabaikannya.

4. **Gaya default** adalah IEEE. Apabila field `keyword` tidak diisi atau tidak dikenali, agent akan menggunakan IEEE sebagai gaya sitasi.

5. **Rate limit** CrossRef API bersifat gratis tanpa autentikasi. Untuk request dengan banyak referensi, disarankan mengirim secara bertahap untuk menghindari potensi pemblokiran.
