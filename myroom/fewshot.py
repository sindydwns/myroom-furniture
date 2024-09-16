from models import Environment
import util
from glob import glob
import chromadb
from openai import OpenAI
import json

ai = OpenAI()

client = chromadb.PersistentClient("chroma/db")
collections = client.list_collections()
collection_names = [c.name for c in collections]
if "fewshot" not in collection_names:
    client.create_collection("fewshot")
fewshot_db = client.get_collection("fewshot")

def get_fallbacks():
    files = glob("resources/fewshot/*.jsonl")
    fewshots = []
    for file in files:
        fewshots += util.read_jsonl(file)
    contain_items = fewshot_db.get([f["id"] for f in fewshots])
    contain_items = contain_items["ids"]
    fallbacks = [f for f in fewshots if f["id"] not in contain_items]
    return fallbacks

def get_embedding(texts: list[str], model="text-embedding-3-large") -> str:
    res = ai.embeddings.create(input=texts, model=model)
    return [data.embedding for data in res.data]

def load_fallbacks(fallbacks: list[dict]) -> None:
    print(f"fallbacks: {len(fallbacks)}")
    if not fallbacks:
        return
    queries = [f["query"] for f in fallbacks]
    embeddings = get_embedding(queries)
    fewshot_db.upsert(
        ids=[f["id"] for f in fallbacks],
        embeddings=embeddings,
        documents=[json.dumps(x) for x in fallbacks],
    )
    print(f"fallbacks: {len(fallbacks)} loaded")

fallbacks = get_fallbacks()
load_fallbacks(fallbacks)
fewshot_essential = util.read_jsonl("resources/fewshot/failure.jsonl")
fewshot_header = util.read_file_to_text("resources/fewshot.txt")

def to_plain_text(fewshot: dict) -> str:
    if isinstance(fewshot, list):
        return "\n".join([to_plain_text(f) for f in fewshot])
    query = fewshot["query"]
    explain = fewshot["explain"]
    answers = fewshot["answer"]
    answer_str = "\n".join(answers)
    return f"요청 예: {query}\n추론: {explain}\n답변 예:\n{answer_str}\n"

def embedding_query(query: str, n_results=20) -> list[str]:
    em = get_embedding([query])
    embedding = em[0]
    res = fewshot_db.query(embedding, n_results=n_results, )
    print(res["distances"])
    return res["documents"][0]

def get_fewshot_prompt(q: str) -> str:
    res = embedding_query(q)
    new_fewshot_data = [json.loads(r) for r in res]
    print([f["query"] for f in new_fewshot_data])
    plain_text = to_plain_text(new_fewshot_data)
    extra_text = to_plain_text(fewshot_essential)
    return fewshot_header + plain_text + "\n" + extra_text

if __name__ == "__main__":
    pass
