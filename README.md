# Building RAG Systems with a Vector Database

This project demonstrates building RAG (Retrieval-Augmented Generation) systems using Weaviate vector database.

## Windows Compatibility Fix

**Issue**: The original code used `weaviate.connect_to_embedded()` which is not supported on Windows systems. This caused a `WeaviateStartUpError` when trying to run the Jupyter notebook.

**Solution**: Modified the project to use Docker-based Weaviate instead of the embedded database.

### Changes Made:

1. **Created `docker-compose.yml`**:

   - Sets up Weaviate server with required modules (text2vec-transformers, reranker-transformers)
   - Includes transformer inference services for embeddings and reranking
   - Configures persistent data storage using Docker volumes
   - Uses Weaviate version 1.28.3 for compatibility

2. **Modified `weaviate_server.py`**:
   - Replaced `weaviate.connect_to_embedded()` with `weaviate.connect_to_local()`
   - Added `wait_for_weaviate()` function to ensure Weaviate is ready before connecting
   - Added proper error handling with user-friendly messages
   - Removed Windows-incompatible embedded database configuration

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.12+

### Installation Steps

1. **Setup Python Environment**:

```bash
python --version
python -m venv venv
source venv/Scripts/activate  # On Windows Git Bash
# OR
venv\Scripts\activate  # On Windows PowerShell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. **Start Weaviate (Required before running Jupyter)**:

```bash
docker-compose up -d
```

This will start:

- Weaviate server on `http://localhost:8080`
- Text-to-vector transformer service on port 8081
- Reranker transformer service on port 8082

3. **Verify Weaviate is Running**:

```bash
curl http://localhost:8080/v1/.well-known/ready
```

Should return: `{"status":"ready"}`

4. **Setup the BBC Collection (First time only)**:

```bash
python setup_collection.py
```

This will:

- Create the `bbc_collection` in Weaviate
- Load all BBC news data from `data/bbc_data.joblib`
- Set up the proper schema and vectorization

5. **Run Jupyter Notebook**:

```bash
jupyter lab
# OR
jupyter notebook
```

### Managing Weaviate

- **Stop Weaviate**: `docker-compose down`
- **Stop and remove data**: `docker-compose down -v`
- **View logs**: `docker-compose logs weaviate`

## Why Docker Instead of Embedded?

- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **Better resource management**: Isolated container environment
- **Production-like setup**: More similar to real deployment scenarios
- **Easier troubleshooting**: Clear separation of services with individual logs
