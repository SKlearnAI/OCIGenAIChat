import oracledb
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import OracleVS
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from LoadProperties import LoadProperties
print("Successfully imported libraries and modules")

properties = LoadProperties()
# Declare username and password and dsn (data connection string)
username = "ADMIN"
password = properties.getDBPassword()
dsn = properties.getDBDSN()
# dsn = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g620084201a219b_lgjp26j8kjiikxu3_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

# Connect to the database
try:
    conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connection successful!")
except Exception as e:
    print("Connection failed!")

# Retrieval Step 1 - Build the llm, embed_model and prompt to query the document
COMPARTMENT_OCID = "ocid1.compartment.oc1..aaaaaaaa66xctsplwbmxlabjytax7od3xdtzn74xcoqxh53b7ilbxaoccgaa"

llm = ChatOCIGenAI(
    model_id=properties.getModelName(),
    service_endpoint=properties.getEndpoint(),
    compartment_id=properties.getCompartment(),
    model_kwargs={"temperature": 0.7, "max_tokens": 400,"prompt_truncation": "AUTO_PRESERVE_ORDER"}
)

embed_model = OCIGenAIEmbeddings(
    model_id=properties.getEmbeddingModelName(),
    service_endpoint=properties.getEndpoint(),
    compartment_id=properties.getCompartment(),
    model_kwargs={"truncate":True}
)

# Set up the template for the questions and context, and instantiate the database retriever object
template = """Answer the question based only on the following context:
{context} Question: {user_question} """
prompt = PromptTemplate.from_template(template)

# Retrieval Step 2 - Create retriever without ingesting documents again.
vs = OracleVS(
    embedding_function=embed_model,
    client=conn23c,
    table_name="MY_DEMO",
    distance_strategy=DistanceStrategy.DOT_PRODUCT
)

retriever = vs.as_retriever(search_type="similarity", search_kwargs={'k': 1})

chain = (
  {"context": retriever, "user_question": RunnablePassthrough()}
     | prompt
     | llm
     | StrOutputParser()
)

user_question = "Tell us about Module 4 of AI Foundations Certification course."
response = chain.invoke(user_question)
print("User question was ->", user_question)
print("LLM response is ->", response)


# Set up the template for the questions and context, and instantiate the database retriever object
template = """Answer the question based only on the following context:
{context} Question: {user_question} """
prompt = PromptTemplate.from_template(template)

# Retrieval Step 2 - Create retriever without ingesting documents again.
vs = OracleVS(
    embedding_function=embed_model,
    client=conn23c,
    table_name="MY_DEMO",
    distance_strategy=DistanceStrategy.DOT_PRODUCT
)

retriever = vs.as_retriever(search_type="similarity", search_kwargs={'k': 1})

chain = (
  {"context": retriever, "user_question": RunnablePassthrough()}
     | prompt
     | llm
     | StrOutputParser()
)
user_question = "Tell us about Module 4 of AI Foundations Certification course."
response = chain.invoke(user_question)

print("User question was ->", user_question)
print("LLM response is ->", response)

