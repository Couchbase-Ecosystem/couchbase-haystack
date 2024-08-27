"use strict";(self.webpackChunkcouchbase_haystack=self.webpackChunkcouchbase_haystack||[]).push([[918],{1195:(e,n,r)=>{r.r(n),r.d(n,{assets:()=>d,contentTitle:()=>c,default:()=>h,frontMatter:()=>i,metadata:()=>o,toc:()=>a});var t=r(4848),s=r(8453);const i={id:"couchbase_embedding_retriever",title:"CouchbaseEmbeddingRetriever"},c=void 0,o={id:"reference/couchbase_embedding_retriever",title:"CouchbaseEmbeddingRetriever",description:"def init(",source:"@site/docs/reference/couchbase_embedding_retriever.md",sourceDirName:"reference",slug:"/reference/couchbase_embedding_retriever",permalink:"/couchbase-haystack/reference/couchbase_embedding_retriever",draft:!1,unlisted:!1,editUrl:"https://github.com/Couchbase-Ecosystem/couchbase-haystack/docs/reference/couchbase_embedding_retriever.md",tags:[],version:"current",frontMatter:{id:"couchbase_embedding_retriever",title:"CouchbaseEmbeddingRetriever"},sidebar:"tutorialSidebar",next:{title:"CouchbaseDocumentStore",permalink:"/couchbase-haystack/reference/couchbase_document_store"}},d={},a=[{value:"<code>run</code>",id:"run",level:4},{value:"<code>to_dict</code>",id:"to_dict",level:4},{value:"<code>from_dict</code>",id:"from_dict",level:4},{value:"Usage Example",id:"usage-example",level:2}];function l(e){const n={code:"code",h2:"h2",h4:"h4",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,s.R)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-markdown",children:"# Couchbase Embedding Retriever\n\n## Class Overview\n\n### `CouchbaseEmbeddingRetriever`\n\nThe `CouchbaseEmbeddingRetriever` retrieves documents from the `CouchbaseDocumentStore` by embedding similarity. The similarity depends on the `vector_search_index` used in the `CouchbaseDocumentStore` and the metric chosen during the creation of the index (e.g., dot product, or L2 norm).\n\n#### Initialization\n\n```python\ndef __init__(\n    self,\n    *,\n    document_store: CouchbaseDocumentStore,\n    top_k: int = 10,\n)\n"})}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Input Parameters:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"document_store"})," (CouchbaseDocumentStore): An instance of ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"})," where the documents are stored."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"top_k"})," (int): Maximum number of documents to return. Defaults to 10."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Raises:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"ValueError"}),": If ",(0,t.jsx)(n.code,{children:"document_store"})," is not an instance of ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"}),"."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Example Usage:"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'import numpy as np\nfrom couchbase_haystack import CouchbaseDocumentStore, CouchbaseEmbeddingRetriever\nfrom haystack.utils.auth import Secret\n\nstore = CouchbaseDocumentStore(\n    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),,\n    cluster_options=CouchbaseClusterOptions(),\n    authenticator=CouchbasePasswordAuthenticator(),\n    bucket="haystack_test_bucket",\n    scope="scope_name",\n    collection="collection_name",\n    vector_search_index="vector_index"\n)\n\nretriever = CouchbaseEmbeddingRetriever(document_store=store)\n\nquery_embedding = np.random.random(768).tolist()\nresults = retriever.run(query_embedding=query_embedding)\nprint(results["documents"])\n'})}),"\n",(0,t.jsx)(n.h4,{id:"run",children:(0,t.jsx)(n.code,{children:"run"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"@component.output_types(documents=List[Document])\ndef run(\n    self,\n    query_embedding: List[float],\n    top_k: Optional[int] = None,\n    search_query: Optional[SearchQuery] = None,\n    limit: Optional[int] = None,\n) -> Dict[str, List[Document]]\n"})}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Description:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Retrieves documents from the ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"})," based on the similarity of their embeddings to the provided query embedding."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Input Parameters:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"query_embedding"})," (List[float]): A list of float values representing the query embedding. The dimensionality of this embedding must match the dimensionality of the embeddings stored in the ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"}),"."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"top_k"})," (Optional[int]): The maximum number of documents to return. Overrides the value specified during initialization. Defaults to the value of ",(0,t.jsx)(n.code,{children:"top_k"})," set during initialization."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"search_query"})," (Optional[SearchQuery]): An optional search query to combine with the embedding query. The embedding query and search query are combined using an OR operation."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"limit"})," (Optional[int]): The maximum number of documents to return from the Couchbase full-text search (FTS) query. Defaults to ",(0,t.jsx)(n.code,{children:"top_k"}),"."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Response:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Returns a dictionary with a single key, ",(0,t.jsx)(n.code,{children:"documents"}),", which maps to a list of ",(0,t.jsx)(n.code,{children:"Document"})," objects that are most similar to the provided ",(0,t.jsx)(n.code,{children:"query_embedding"}),"."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Example Usage:"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'query_embedding = [0.1, 0.2, 0.3, ...]  # Example embedding vector\nresults = retriever.run(query_embedding=query_embedding, top_k=5)\nprint(results["documents"])\n'})}),"\n",(0,t.jsx)(n.h4,{id:"to_dict",children:(0,t.jsx)(n.code,{children:"to_dict"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"def to_dict() -> Dict[str, Any]\n"})}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Description:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Serializes the ",(0,t.jsx)(n.code,{children:"CouchbaseEmbeddingRetriever"})," instance into a dictionary format."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Response:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Returns a dictionary containing the serialized state of the ",(0,t.jsx)(n.code,{children:"CouchbaseEmbeddingRetriever"})," instance."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Example Usage:"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"retriever_dict = retriever.to_dict()\n"})}),"\n",(0,t.jsx)(n.h4,{id:"from_dict",children:(0,t.jsx)(n.code,{children:"from_dict"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'@classmethod\ndef from_dict(cls, data: Dict[str, Any]) -> "CouchbaseEmbeddingRetriever"\n'})}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Description:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Deserializes a ",(0,t.jsx)(n.code,{children:"CouchbaseEmbeddingRetriever"})," instance from a dictionary."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Input Parameters:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"data"})," (Dict[str, Any]): A dictionary containing the serialized state of a ",(0,t.jsx)(n.code,{children:"CouchbaseEmbeddingRetriever"}),"."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Response:"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Returns a ",(0,t.jsx)(n.code,{children:"CouchbaseEmbeddingRetriever"})," instance reconstructed from the provided dictionary."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Example Usage:"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"retriever_instance = CouchbaseEmbeddingRetriever.from_dict(retriever_dict)\n"})}),"\n",(0,t.jsx)(n.h2,{id:"usage-example",children:"Usage Example"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'import numpy as np\nfrom couchbase_haystack import CouchbaseDocumentStore, CouchbaseEmbeddingRetriever\n\nstore = CouchbaseDocumentStore(\n    cluster_connection_string="couchbases://localhost",\n    cluster_options=CouchbaseClusterOptions(),\n    authenticator=CouchbasePasswordAuthenticator(),\n    bucket="haystack_test_bucket",\n    scope="scope_name",\n    collection="collection_name",\n    vector_search_index="vector_index"\n)\n\nretriever = CouchbaseEmbeddingRetriever(document_store=store)\n\nquery_embedding = np.random.random(768).tolist()\nresults = retriever.run(query_embedding=query_embedding)\nprint(results["documents"])\n'})}),"\n",(0,t.jsxs)(n.p,{children:["This example retrieves the 10 most similar documents to a randomly generated query embedding from the ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"}),". Note that the dimensionality of the ",(0,t.jsx)(n.code,{children:"query_embedding"})," must match the dimensionality of the embeddings stored in the ",(0,t.jsx)(n.code,{children:"CouchbaseDocumentStore"}),"."]})]})}function h(e={}){const{wrapper:n}={...(0,s.R)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(l,{...e})}):l(e)}},8453:(e,n,r)=>{r.d(n,{R:()=>c,x:()=>o});var t=r(6540);const s={},i=t.createContext(s);function c(e){const n=t.useContext(i);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function o(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:c(e.components),t.createElement(i.Provider,{value:n},e.children)}}}]);