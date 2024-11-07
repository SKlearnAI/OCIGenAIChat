from PyPDF2 import PdfReader
import oracledb

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.vectorstores import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import BaseDocumentTransformer, Document
from LoadProperties import LoadProperties
print("Successfully imported libraries and modules")

properties = LoadProperties()
#Declare username and password and dsn (data connection string)
username = "ADMIN"
password = "Iz2yIlEMo37Wf5HgYXApmNr2I"
dsn = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g620084201a219b_lgjp26j8kjiikxu3_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

# Connect to the database
try:
    conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connection successful!")
except Exception as e:
    print("Connection failed!")

# RAG Step 1: Load the document and create pdf reader object
pdf = PdfReader('./pdf-docs/oci-ai-foundations.pdf')

# RAG Step 2: Transform the document to text
text = ""
for page in pdf.pages:
    text += page.extract_text()

print("You have transformed the PDF document to text format.")


# RAG Step 3: Chunk the text document into smaller chunks
text_splitter = CharacterTextSplitter(separator="_", chunk_size=2000, chunk_overlap=100)
chunks = text_splitter.split_text(text)
# Function to format and add metadata to Oracle 23ai Vector Store
def chunks_to_docs_wrapper(row: dict) -> Document:
    """
    Converts text into a Document object suitable for ingestion into Oracle Vector Store.
    - row (dict): A dictionary representing a row of data with keys for 'id', 'link', and 'text'.
    """
    metadata = {'id': row['id'], 'link': row['link']}
    return Document(page_content=row['text'], metadata=metadata)

# RAG Step 4: Create metadata wrapper to store additional information in the vector store
docs = [chunks_to_docs_wrapper({'id': str(page_num), 'link': f'Page {page_num}', 'text': text}) for page_num, text in enumerate(chunks)]

COMPARTMENT_OCID = "ocid1.compartment.oc1..aaaaaaaa66xctsplwbmxlabjytax7od3xdtzn74xcoqxh53b7ilbxaoccgaa"
embed_model = OCIGenAIEmbeddings(
    model_id=properties.getEmbeddingModelName(),
    service_endpoint=properties.getEndpoint(),
    compartment_id=properties.getCompartment(),
    model_kwargs={"truncate":True}
)

# RAG Step 5 - Using an embedding model, embed the chunks as vectors into Oracle Database 23ai.

# RAG Step 6 - Configure the vector store with the model, table name, and using the indicated distance strategy for the similarity search and vectorize the chunks
knowledge_base = OracleVS.from_documents(docs, embed_model, client=conn23c, table_name="MY_DEMO", distance_strategy=DistanceStrategy.DOT_PRODUCT)
