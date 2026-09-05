from azure.identity import DefaultAzureCredential
from backend.app.core.config import get_settings
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)


settings = get_settings()

credential = DefaultAzureCredential()

index_client = SearchIndexClient(
    endpoint=settings.azure_search_endpoint,
    credential=credential,
)

def create_search_index():

    fields = [

        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
        ),

        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            searchable=True,
        ),

        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="default-vector-profile",
        ),

        SearchableField(
            name="document_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SearchableField(
            name="document_type",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SearchableField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SimpleField(
            name="page_number",
            type=SearchFieldDataType.Int32,
            filterable=True,
        ),

        SimpleField(
            name="chunk_number",
            type=SearchFieldDataType.Int32,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="default-hnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="default-vector-profile",
                algorithm_configuration_name="default-hnsw",
            )
        ],
    )

    index = SearchIndex(
        name=settings.azure_search_index_name,
        fields=fields,
        vector_search=vector_search,
    )

    result = index_client.create_or_update_index(index)

    return result