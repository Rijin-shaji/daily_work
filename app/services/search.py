import mysql.connector
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# load FAISS index
index = faiss.read_index("resume_index.faiss")

# connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rijin@1234",
    database="resume_db"
)

cursor = conn.cursor(dictionary=True)


def search_resumes(query):

    # convert query to embedding
    query_embedding = model.encode([query])

    # search vector DB
    distances, indices = index.search(np.array(query_embedding), 5)

    candidates = []

    for idx in indices[0]:

        cursor.execute(
            "SELECT name, skills, total_experience_years FROM resume_metadata WHERE resume_id=%s",
            (int(idx),)
        )

        result = cursor.fetchone()

        if result:
            candidates.append(result)

    return candidates