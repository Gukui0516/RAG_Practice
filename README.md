```
docker build -t rag-local-app .
```

```
docker run -p 8501:8501 --env-file .env rag-local-app
```