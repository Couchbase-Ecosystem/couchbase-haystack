import os
from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack.utils.hf import HFGenerationAPIType
from haystack.utils import Secret
from couchbase_haystack import (
    CouchbaseClusterOptions,
    CouchbasePasswordAuthenticator,
    CouchbaseQueryDocumentStore,
    CouchbaseQueryEmbeddingRetriever,
    QueryVectorSearchType,
)
from couchbase.options import KnownConfigProfiles

# Load HF Token from environment variables.
HF_TOKEN = Secret.from_env_var("HF_API_TOKEN")

# Make sure you have a running couchbase database, e.g. with Docker:
# docker run \
#     --restart always \
#     --publish=8091-8096:8091-8096 --publish=11210:11210 \
#     --env COUCHBASE_ADMINISTRATOR_USERNAME=admin \
#     --env COUCHBASE_ADMINISTRATOR_PASSWORD=passw0rd \
#     couchbase:enterprise-8.0.0

document_store = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(username=Secret.from_env_var("USER_NAME"), password=Secret.from_env_var("PASSWORD")),
    cluster_options=CouchbaseClusterOptions(
        profile=KnownConfigProfiles.WanDevelopment,
    ),
    bucket=os.getenv("BUCKET_NAME"),
    scope=os.getenv("SCOPE_NAME"),
    collection=os.getenv("COLLECTION_NAME"),
    search_type=QueryVectorSearchType.ANN,
    similarity="L2",
    nprobes=10,
)

# Build a RAG pipeline with a Retriever to get relevant documents to the query and a HuggingFaceAPIChatGenerator
# interacting with LLMs using a custom prompt.
prompt_messages = [
    ChatMessage.from_system("You are a helpful assistant that answers questions based on the provided documents."),
    ChatMessage.from_user("""Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

Question: {{question}}
Answer:""")
]
rag_pipeline = Pipeline()
rag_pipeline.add_component(
    "query_embedder",
    SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", progress_bar=False),
)
rag_pipeline.add_component("retriever", CouchbaseQueryEmbeddingRetriever(document_store=document_store))
rag_pipeline.add_component("prompt_builder", ChatPromptBuilder(template=prompt_messages, required_variables=["question"]))
rag_pipeline.add_component("llm", HuggingFaceAPIChatGenerator(
    api_type=HFGenerationAPIType.SERVERLESS_INFERENCE_API, 
    api_params={"model": "mistralai/Mistral-7B-Instruct-v0.2"},
))
rag_pipeline.add_component("answer_builder", AnswerBuilder())

rag_pipeline.connect("query_embedder", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")

# Ask a question on the data you just added.
question = "Who created the Dothraki vocabulary?"
result = rag_pipeline.run(
    {
        "query_embedder": {"text": question},
        "retriever": {"top_k": 3},
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question},
    }
)

# For details, like which documents were used to generate the answer, look into the GeneratedAnswer object
answer: GeneratedAnswer = result["answer_builder"]["answers"][0]

# ruff: noqa: T201
print("Query: ", answer.query)
print("Answer: ", answer.data)
print("== Sources:")
for doc in answer.documents:
    print("-> ", doc.meta["file_path"])
