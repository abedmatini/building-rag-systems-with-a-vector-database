#!/usr/bin/env python3
"""
Script to create the BBC collection in Weaviate and load the data.
Run this script after starting Weaviate with docker-compose up -d
"""

import joblib
import weaviate
from weaviate.classes.config import Configure, Property, DataType
import sys
import time

def wait_for_weaviate(url="http://localhost:8080", timeout=60):
    """Wait for Weaviate to be ready"""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/v1/.well-known/ready", timeout=5)
            if response.status_code == 200:
                print("✅ Weaviate is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print("⏳ Waiting for Weaviate to start...")
        time.sleep(2)
    return False

def create_bbc_collection(client):
    """Create the BBC collection with proper schema"""
    
    # Check if collection already exists
    if client.collections.exists("bbc_collection"):
        print("⚠️  Collection 'bbc_collection' already exists. Deleting it...")
        client.collections.delete("bbc_collection")
    
    print("📝 Creating BBC collection...")
    
    # Create collection with schema based on the data structure
    collection = client.collections.create(
        name="bbc_collection",
        properties=[
            Property(name="article_content", data_type=DataType.TEXT),
            Property(name="chunk", data_type=DataType.TEXT),
            Property(name="chunk_index", data_type=DataType.INT),
            Property(name="description", data_type=DataType.TEXT),
            Property(name="link", data_type=DataType.TEXT),
            Property(name="pubDate", data_type=DataType.TEXT),
            Property(name="title", data_type=DataType.TEXT),
        ],
        # Configure which field to vectorize
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(
            vectorize_collection_name=False
        ),
        # Set the main vector field to be the chunk content
        vector_index_config=Configure.VectorIndex.hnsw()
    )
    
    print("✅ Collection created successfully!")
    return collection

def load_data_to_collection(client, collection):
    """Load BBC data into the collection"""
    
    print("📂 Loading BBC data...")
    try:
        bbc_data = joblib.load('data/bbc_data.joblib')
        print(f"📊 Found {len(bbc_data)} data items")
    except FileNotFoundError:
        print("❌ Error: data/bbc_data.joblib not found!")
        print("Make sure the data file exists in the data/ directory")
        return False
    
    print("🔄 Inserting data into Weaviate...")
    
    # Prepare data for batch insertion
    data_objects = []
    for item in bbc_data:
        # Prepare the object for insertion
        data_object = {
            "article_content": item.get("article_content", ""),
            "chunk": item.get("chunk", ""),
            "chunk_index": item.get("chunk_index", 0),
            "description": item.get("description", ""),
            "link": item.get("link", ""),
            "pubDate": item.get("pubDate", ""),
            "title": item.get("title", ""),
        }
        data_objects.append(data_object)
    
    # Batch insert data
    try:
        with collection.batch.dynamic() as batch:
            for i, data_object in enumerate(data_objects):
                batch.add_object(properties=data_object)
                if (i + 1) % 100 == 0:
                    print(f"  📤 Inserted {i + 1}/{len(data_objects)} objects...")
        
        print(f"✅ Successfully loaded {len(data_objects)} objects into the collection!")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False

def main():
    print("🚀 Setting up BBC Collection in Weaviate")
    print("=" * 50)
    
    # Wait for Weaviate to be ready
    if not wait_for_weaviate():
        print("❌ Weaviate is not ready. Make sure it's running with: docker-compose up -d")
        sys.exit(1)
    
    # Connect to Weaviate
    try:
        client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=50051
        )
        print("✅ Connected to Weaviate!")
        
        # Create collection
        collection = create_bbc_collection(client)
        
        # Load data
        if load_data_to_collection(client, collection):
            print("\n🎉 Setup completed successfully!")
            print("You can now run your Jupyter notebook.")
        else:
            print("\n❌ Setup failed during data loading.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error connecting to Weaviate: {e}")
        print("Make sure Weaviate is running with: docker-compose up -d")
        sys.exit(1)
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
