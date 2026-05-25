from sentence_transformers import SentenceTransformer
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def getcontext():
    import json

    with open("./information/about-me.json") as f:
        aboutme = json.load(f)
    with open("./information/Projects.json") as f:
        projects = json.load(f)
    context=[]

    context.append("My name is " + aboutme.get("aboutMe").get("Name"))
    context.append("Garfield's major is " + aboutme.get("aboutMe").get("Major"))
    context.append("Garfield went to this university " + aboutme.get("aboutMe").get("School"))
    context.append("You can contact Garfield at the following email: " + aboutme.get("ContactInfo").get("email"))
    context.append("You can find more projects created at: " + aboutme.get("ContactInfo").get("Github"))
    context.append("Garfield has the following certificates: " + " ".join([x for x in aboutme.get("aboutMe").get("Certifications").keys()]))
    context.append("Garfield has the position of: " + aboutme.get("aboutMe").get("PositionTitle"))
    context.append("Garfield has the following skills: " + " ".join([x for x in aboutme.get("aboutMe").get("Skills").keys()]))
    context.append("Garfield has taken the following courses: " + " ".join([x for x in aboutme.get("aboutMe").get("Education").keys()]))
    for x in aboutme.get("aboutMe").get("Education").keys():
        context.append(x + " course is "+ aboutme.get("aboutMe").get("Education").get(x))
    return context

embedder = SentenceTransformer("all-MiniLM-L6-v2")

qa = pipeline(
    "question-answering",
    model="./distilbert-base-cased-distilled-squad",
    tokenizer="./distilbert-base-cased-distilled-squad"
)

context=getcontext()
context_embeddings = embedder.encode(context)

def retrieve(question, k=3):
    question_embedding = embedder.encode([question])

    scores = cosine_similarity(
        question_embedding,
        context_embeddings
    )[0]

    top_indices = np.argsort(scores)[-k:][::-1]

    return [(context[i], scores[i]) for i in top_indices]

def ask(question):
    import json
    with open("./information/about-me.json") as f:
        aboutme = json.load(f)
    with open("./information/Projects.json") as f:
        projects = json.load(f)
    q = question.lower()

    # Handle list questions directly
    if "project" in q:
        return {
            "answer": [
                x.get("Name")
                for x in projects.get("Projects")
            ]
        }

    if "skill" in q:
        return {
            "answer": list(
                aboutme["aboutMe"]["Skills"].keys()
            )
        }

    # Otherwise use QA
    retrieved = retrieve(question)

    answers = []

    for c, retrieval_score in retrieved:
        result = qa(question=question, context=c)

        result["combined_score"] = (
            result["score"] * 0.7 +
            retrieval_score * 0.3
        )

        answers.append(result)

    best = max(
        answers,
        key=lambda x: x["combined_score"]
    )

    return best

result = ask("Where did Garfield go for University?")

print(result["answer"])