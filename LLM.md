# Not Lonely – Backend Service (v0.1) — Design Spec for Coding Agent

GOAL  
Build a modular, open-source backend that accepts user speech/text from the iOS client, routes the request to any configured LLM provider (local or remote), and streams a TTS audio reply back. Service must ship in Docker-Compose, be easy to extend with new models, and keep user data private by default.

––– 1. Top-Level Architecture –––
client (iOS)  <-WebSocket/gRPC->  **gateway**  <-REST/gRPC->  **llm-manager**  –plugin–>  provider(s)
                                                                       ↑
                                        **stt-svc**     **tts-svc**    │
                                                                       │
                                        **postgres + pgvector**  <---memory & embeddings

Essentials  
* **gateway**   FastAPI app: TLS, auth, bidirectional streaming, packet framing.  
* **llm-manager**   Python micro-service: selects provider, maintains chat state, yields token stream.  
* **provider plug-ins**   Stateless adapters: OpenAI, Anthropic, Groq, Ollama/vLLM, etc.  
* **stt-svc**   whisper.cpp container (CUDA when GPU present) → UTF-8 text.  
* **tts-svc**   Piper container (or Polly adapter) → 16-kHz PCM chunks.  
* **postgres**   Stores vectorised memories and usage metrics; nothing PII unless “sync” is enabled.

––– 2. Transport Contract –––
WebSocket binary frames (or HTTP/2 gRPC):

| role       | seq | payload                           |
|============|====:|===================================|
| user_pcm   | u16 | 160-frame 16-kHz PCM              |
| user_text  | u16 | UTF-8 text                        |
| llm_text   | u16 | {partial:bool, content:str}       |
| tts_pcm    | u16 | raw PCM audio chunk               |

––– 3. Docker-Compose Skeleton –––
services:
  gateway:     ghcr.io/notlonely/gateway:0.1
  llm-manager: ghcr.io/notlonely/llm-manager:0.1
  stt:         ghcr.io/notlonely/whispercpp:0.1      # runtime: nvidia
  tts:         ghcr.io/notlonely/piper:0.1
  db:          ankane/pgvector:15
networks: [nl_private]

––– 4. Provider Plug-in Interface –––
```python
class BaseProvider(Protocol):
    async def chat(self, messages: list[dict], **kw) -> AsyncIterator[str]:
        """Yield assistant tokens."""
```

• Loaded via entry-point `notlonely_providers`.
• Selected per-request via header `X-Provider`.

––– 5. Security / Privacy –––

* TLS 1.3 - server cert + optional client cert.
* JWT bearer in WebSocket `Sec-WebSocket-Protocol`.
* “Zero-retention” flag drops audio/text after reply; otherwise store embeddings only.
* All images signed with Sigstore; verify on start-up.

––– 6. Performance Targets –––

* End-to-end latency ≤ 800 ms on 5 G.
* Sustained 30 req/s per GPU-equipped node (vLLM + 70 B Q4\_0).
* Whisper small.en, real-time factor ≤ 0.9 on A100 / RTX 6000.

––– 7. Milestones –––
M1 (2 wks)  Gateway skeleton + OpenAIProvider + text-only loop.
M2 (4 wks)  OllamaProvider + streaming PCM + Piper TTS.
M3 (6 wks)  Vector memory, Anthropic/Groq plug-ins, canary deploy script.
M4 (8 wks)  Zero-retention mode, integration tests, docs → GitHub OSS release.

Deliverables:

* `docker-compose.yml` & per-service `Dockerfile`.
* `gateway/`, `llm_manager/`, `providers/` Python packages.
* OpenAPI / proto definitions.
* GitHub Actions CI that builds, tests, signs, and publishes images.

Outcome: a self-contained backend any iOS, Android, or desktop client can hit securely, with hot-swappable LLM/TTS/STT engines and strict privacy controls.
