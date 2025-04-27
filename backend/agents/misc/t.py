
from vertexai import rag
import vertexai

# TODO(developer): Update and un-comment below lines
# PROJECT_ID = "your-project-id"

# Initialize Vertex AI API once per session
vertexai.init(project="animind-458004", location="us-central1")

corpora = rag.list_corpora()
print(corpora)
# Example response:
# ListRagCorporaPager<rag_corpora {
#   name: "projects/[PROJECT_ID]/locations/us-central1/ragCorpora/2305843009213693952"
#   display_name: "test_corpus"
#   create_time {
# ...