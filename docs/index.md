--8<-- "README.md"

<!-- Override links and references from README.md -->
<script>
  document.addEventListener('DOMContentLoaded', function() {
    // Fix repository reference links
    const repoLinks = document.querySelectorAll('a[href^="https://github.com/Couchbase-Ecosystem/couchbase-haystack"]');
    repoLinks.forEach(link => {
      if (link.href.includes('/blob/main/examples/')) {
        const newPath = link.href.replace('/blob/main/examples/', '/examples/');
        link.href = newPath;
      }
    });

    // Fix API documentation links
    const apiLinks = document.querySelectorAll('a[href^="https://couchbase-ecosystem.github.io/couchbase-haystack/reference/"]');
    apiLinks.forEach(link => {
      const parts = link.href.split('/');
      const lastPart = parts[parts.length - 1];
      if (lastPart === 'couchbase_document_store') {
        link.href = 'reference/document_stores/document_store.md';
      }
    });

    // Fix empty component links
    document.querySelectorAll('a[href=""]').forEach(link => {
      if (link.textContent.includes('CouchbaseSearchEmbeddingRetriever')) {
        link.href = 'reference/components/retrievers/embedding_retriever';
      }
    });

    // Fix example file references
    document.querySelectorAll('a').forEach(link => {
      // Handle relative example paths
      if (link.getAttribute('href') === 'examples/indexing_pipeline.py' ||
          link.getAttribute('href') === 'examples/rag_pipeline.py') {
        // Update to point to GitHub repo with proper path
        const fileName = link.getAttribute('href').split('/').pop();
        link.href = `https://github.com/Couchbase-Ecosystem/couchbase-haystack/blob/main/examples/${fileName}`;

        // Add icon to indicate external link and title
        const icon = document.createElement('span');
        icon.innerHTML = ' 🔗';
        icon.title = 'View on GitHub';
        icon.style.fontSize = '0.8em';
        link.appendChild(icon);

        // Open in new tab
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }

      // Also handle the [repository](examples) link
      if (link.textContent === 'repository' && link.getAttribute('href') === 'examples') {
        link.href = 'https://github.com/Couchbase-Ecosystem/couchbase-haystack/tree/main/examples';
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
    });

    // Remove GitHub alignment styling
    document.querySelectorAll('[align="center"]').forEach(elem => {
      elem.removeAttribute('align');
      elem.style.textAlign = 'left';
    });
  });
</script>

<style>
  /* Override GitHub-specific styling */
  h1:first-of-type {
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    font-size: 2.5em !important;
  }
  
  p:nth-of-type(1), p:nth-of-type(2) {
    font-size: 1.2em;
    margin-bottom: 1.5rem;
  }
  
  /* Style external example links */
  a[href^="https://github.com/Couchbase-Ecosystem/couchbase-haystack/blob/main/examples/"] {
    text-decoration: none;
    padding: 0.1em 0.3em;
    background-color: rgba(204, 52, 45, 0.1);
    border-radius: 3px;
    transition: background-color 0.2s;
  }
  
  a[href^="https://github.com/Couchbase-Ecosystem/couchbase-haystack/blob/main/examples/"]:hover {
    background-color: rgba(204, 52, 45, 0.2);
  }
</style>
