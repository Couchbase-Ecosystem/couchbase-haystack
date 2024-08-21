import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  homeSidebar: [ {
    type: 'category',
    label: 'Home',
    collapsible: false,
    collapsed: false,
    items: [
      "home/overview"
        // Correct document ID
    ],
  }],
  tutorialSidebar: [ {
    type: 'category',
    label: 'Code Reference',
    collapsible: false,
    collapsed: false,
    items: [
      "reference/couchbase_embedding_retriever",
      "reference/couchbase_document_store",
      "reference/document_filter",
      "reference/cluster_options",
      "reference/authentication",
    ],
  }
]
};

export default sidebars;
