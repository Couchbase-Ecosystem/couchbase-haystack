from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import HuggingFaceTGIGenerator
from haystack.utils import Secret

from couchbase_haystack import CouchbaseDocumentStore, CouchbasePasswordAuthenticator, CouchbaseEmbeddingRetriever

# Load HF Token from environment variables.
HF_TOKEN = Secret.from_env_var("HF_API_TOKEN")

# Make sure you have a running couchbase database, e.g. with Docker:
# docker run \
#     --restart always \
#     --publish=8091-8096:8091-8096 --publish=11210:11210 \
#     --env COUCHBASE_ADMINISTRATOR_USERNAME=admin \
#     --env COUCHBASE_ADMINISTRATOR_PASSWORD=passw0rd \
#     couchbase:enterprise-7.6.2

document_store = CouchbaseDocumentStore(
    cluster_connection_string= Secret.from_token("localhost"),
    authenticator=CouchbasePasswordAuthenticator(
        username = Secret.from_token("username"),
        password = Secret.from_token("password")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index"
)

# Build a RAG pipeline with a Retriever to get relevant documents to the query and a HuggingFaceTGIGenerator
# interacting with LLMs using a custom prompt.
prompt_template = """
Given these documents, answer the question.\nDocuments:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

\nQuestion: {{question}}
\nAnswer:
"""
rag_pipeline = Pipeline()
rag_pipeline.add_component(
    "query_embedder",
    SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", progress_bar=False),
)
rag_pipeline.add_component("retriever", CouchbaseEmbeddingRetriever(document_store=document_store))
rag_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipeline.add_component(
    "llm",
    HuggingFaceTGIGenerator(model="mistralai/Mistral-7B-v0.1", token=HF_TOKEN),
)
rag_pipeline.add_component("answer_builder", AnswerBuilder())

rag_pipeline.connect("query_embedder", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("llm.meta", "answer_builder.meta")
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