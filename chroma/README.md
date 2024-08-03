## Setup

### Chroma

Chroma vector store is used for RAG.

1. Clone Chroma:

```bash
git clone https://github.com/chroma-core/chroma.git
cd chroma
```

2. Update chroma docker-compose.yml env variables:

```yml
- ALLOW_RESET=TRUE
```

3. Run local Chroma server with Docker within Chroma repository root:

```bash
docker-compose up -d --build
```

4. Reset your chroma store (when necessary):

* [chroma-reset.py](.chroma/chroma_reset.py)
* [chroma-client.py](.chroma/chroma_client.py)