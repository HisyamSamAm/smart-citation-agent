import json
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from main import process_multiple, format_text_output


app = FastAPI(
    title="SCRA - Citation Reference Agent",
    description="Smart Citation & Reference Agent untuk sistem Multi-Agent Joki Tugas AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jokitugas.bananaunion.web.id"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


class Payload(BaseModel):
    url: Optional[str] = ""
    keyword: Optional[str] = ""
    raw_text: Optional[str] = ""


class AgentRequest(BaseModel):
    task_id: str
    agent_type: str
    payload: Payload
    metadata: Optional[dict] = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "citation_reference",
        "input_type": "text",
        "output_type": "text",
    }


@app.post("/process")
async def process(request: AgentRequest):
    try:
        style = (request.payload.keyword or "ieee").lower()
        if style not in ("ieee", "apa"):
            style = "ieee"

        raw_text = request.payload.raw_text or ""
        url = request.payload.url or ""

        inputs = []
        if raw_text.strip():
            stripped = raw_text.strip()
            if stripped.startswith("["):
                try:
                    data = json.loads(stripped)
                    inputs = [
                        json.dumps(item) if isinstance(item, dict) else str(item)
                        for item in data
                    ]
                except json.JSONDecodeError:
                    inputs = [stripped]
            else:
                inputs = [line.strip() for line in stripped.split("\n") if line.strip()]
        elif url.strip():
            inputs = [url.strip()]
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "task_id": request.task_id,
                    "data": None,
                    "message": "Payload kosong: tidak ada raw_text atau url",
                },
            )

        if not inputs:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "task_id": request.task_id,
                    "data": None,
                    "message": "Tidak ada referensi yang ditemukan dalam payload",
                },
            )

        refs, bibliography, issues = process_multiple(inputs, style)

        result_text = (
            format_text_output(refs, style, bibliography, issues)
            if refs
            else "Tidak ada referensi yang diproses."
        )

        return {
            "status": "success",
            "task_id": request.task_id,
            "data": {
                "result": result_text,
                "file_url": None,
            },
            "message": "Pemrosesan berhasil",
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "task_id": request.task_id,
                "data": None,
                "message": f"Internal Server Error: {str(e)}",
            },
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
