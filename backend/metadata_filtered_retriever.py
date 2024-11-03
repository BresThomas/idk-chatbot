from langchain_community.vectorstores import Chroma
from typing import Optional

class MetadataFilteredRetriever:
    def __init__(self, embeddings, persist_directory: str, collection_name: str):
        """Initializes the metadata filtered retriever."""
        self.vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )

    def get_retriever(self, province: Optional[str] = None):
        """Constructs a retriever with an optional filter for province."""
        filter_dict = {}
        if province:
            filter_dict["province"] = province

        # If no filters are set, allow retrieval of all documents
        if not filter_dict:
            return self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    'k': 6,
                    'fetch_k': 20,
                    'lambda_mult': 0.5
                }
            )

        # Take the first key-value pair for the filter
        key = next(iter(filter_dict))
        value = filter_dict[key]

        return self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                'k': 6,
                'fetch_k': 20,
                'lambda_mult': 0.5,
                'filter': {key: value}  # Use the selected filter here
            }
        )
