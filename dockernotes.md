# from repo root (PROD)
docker build -t linguapi .
docker run --name linguapi-container -p 8000:8000 -e PORT=8000 linguapi

# run with watcher
docker run --rm -it \
    -p 8000:8000 \
    -w /app \
    -v $(pwd)/app:/app \
    linguapi uvicorn main:app --reload --host 0.0.0.0 --port 8000

# test
curl http://localhost:8000/healthz
curl http://localhost:8000/intro
