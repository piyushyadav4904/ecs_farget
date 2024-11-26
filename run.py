#
# from langchain_community.document_loaders import PyPDFLoader
# loader = PyPDFLoader("nural_network (1).pdf")
# documents = loader.load_and_split()
#
#
# from langchain_openai import OpenAIEmbeddings
# from langchain_pinecone import PineconeVectorStore
# embeddings_model = OpenAIEmbeddings()
# docsearch = PineconeVectorStore.from_documents(documents, embeddings_model, index_name="research-index1")
#
#
# from pinecone import Pinecone, ServerlessSpec
# pc = Pinecone(api_key="eca71299-8cdb-4798-8650-16d41bb37867")
# # # index_name = "research-index1"
# # # pc.create_index(
# # #     name=index_name,
# # #     dimension=1536, # Replace with your model dimensions
# # #     metric="cosine", # Replace with your model metric
# # #     spec=ServerlessSpec(
# # #         cloud="aws",
# # #         region="us-east-1"
# # #     )
# # # )
# index = pc.Index("research-index1")
#
#
# question = "What is a type of neural network?"
# question_embedding = embeddings_model.embed_query(question)
# search_results = index.query(vector=question_embedding, top_k=5,include_metadata=True)
#
#
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="gpt-4")
# context = "\n".join([doc.metadata["text"] for doc in search_results.matches])
# prompt = [f"{context}\nQuestion: {question}"]
# response = model.invoke(prompt)
#
#
# from langchain_core.output_parsers import StrOutputParser
# parser = StrOutputParser()
# print(parser.invoke(response))
from tempfile import TemporaryDirectory
from typing import Union

from fastapi import FastAPI, Header, HTTPException
from langchain.chains.question_answering.map_reduce_prompt import messages
from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi import FastAPI, File, UploadFile

import shutil

from langchain_community.document_loaders import DirectoryLoader

fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

app = FastAPI()



class ResponseModel(BaseModel):
    message: str



@app.post("/add_data/")
def upload(files: list[UploadFile]):
    from pathlib import Path
    from tempfile import NamedTemporaryFile
    for upload_file in files:
        try:
            suffix = Path(upload_file.filename).suffix
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(upload_file.file, tmp)
                tmp_path = Path(tmp.name)
                print(tmp_path)
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(tmp_path)
                # loader = DirectoryLoader("/tmp/", glob="**/*.md")
                documents = loader.load_and_split()
                from langchain_openai import OpenAIEmbeddings
                from langchain_pinecone import PineconeVectorStore
                embeddings_model = OpenAIEmbeddings()
                PineconeVectorStore.from_documents(documents, embeddings_model, index_name="research-index1")
        finally:
            upload_file.file.close()
    return {
        "message": "file uploaded successfully"
    }


@app.post("/chata/",response_model=ResponseModel)
async def create_item(question: ResponseModel,):
    import psycopg2
    from psycopg2 import OperationalError
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            database="postgres",  # Replace with your database name
            user="postgres",  # Replace with your username
            password="Awesome123",  # Replace with your password
            host="database-1.cfssqcm06z8w.us-east-2.rds.amazonaws.com",
            port="5432"
        )

        # Create a cursor object
        cursor = conn.cursor()

        # SQL to create the users table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        print("Table 'users' created successfully.")

        # Insert 5 users into the table
        insert_users_query = """
        INSERT INTO users (name, email, age)
        VALUES 
            ('John Doe', 'john@example.com', 25),
            ('Jane Smith', 'jane@example.com', 30),
            ('Alice Johnson', 'alice@example.com', 22),
            ('Bob Brown', 'bob@example.com', 28),
            ('Charlie White', 'charlie@example.com', 35)
        RETURNING id;
        """
        cursor.execute(insert_users_query)
        inserted_ids = cursor.fetchall()
        print(f"Inserted users with IDs: {inserted_ids}")

        # Commit the transaction
        conn.commit()

    except OperationalError as e:
        print("Error connecting to the database:", e)

    finally:
        # Ensure the connection is closed
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

    from pinecone import Pinecone, ServerlessSpec
    from langchain_openai import OpenAIEmbeddings
    pc = Pinecone(api_key="eca71299-8cdb-4798-8650-16d41bb37867")
    index = pc.Index("research-index1")
    embeddings_model = OpenAIEmbeddings()
    question_embedding = embeddings_model.embed_query(question.message)
    search_results = index.query(vector=question_embedding, top_k=5,include_metadata=True)
    from langchain_openai import ChatOpenAI
    model = ChatOpenAI(model="gpt-4")
    context = "\n".join([doc.metadata["text"] for doc in search_results.matches])
    prompt = [f"{context}\nQuestion: {question}"]
    response = model.invoke(prompt)
    from langchain_core.output_parsers import StrOutputParser
    parser = StrOutputParser()
    return ResponseModel(message=parser.invoke(response))
#
