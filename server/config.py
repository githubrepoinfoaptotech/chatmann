import chromadb
from chromadb.config import Settings
from langchain.chat_models import ChatOpenAI
from chromadb.utils import embedding_functions
from langchain.embeddings.openai import OpenAIEmbeddings
import os
import warnings
from dotenv import load_dotenv 
load_dotenv() 
# Suppress the specific warnings by category
warnings.filterwarnings("ignore")
hostname = "https://tg60a835a6.execute-api.us-east-1.amazonaws.com/dev"
apikey = "tKx9nlDBoGaOmyIZUb1du9s0ZwrNSHln5lIU5meA"

# os.environ["OPENAI_API_TYPE"] = "azure"
# os.environ["OPENAI_API_VERSION"] = "2023-05-15"
# os.environ["OPENAI_API_BASE"] = "https://ai-ramsol-traning.openai.azure.com/"
# os.environ["OPENAI_API_KEY"] = "5b60d2473952443cafceeee0b2797cf4"

# Example setup of the client to connect to your chroma server
#client = chromadb.HttpClient(host='3.90.187.44', port=8000)

client = chromadb.HttpClient(
    host=hostname,
    ssl=True,
    port="8000",
    headers={
        "X-Api-Key": apikey 
    }
)


llm = ChatOpenAI(
                    api_key=os.environ.get('OPENAI_API_KEY'),
                    api_base=os.environ.get('OPENAI_API_BASE'),
                    api_type=os.environ.get('OPENAI_API_TYPE'),
                    deployment_id=os.environ.get('DEPLOYMENT_ID_LLM'),   
                    model_name=os.environ.get('MODEL_NAME_LLM'), 
                    temperature=0.5
                    #top_p=0.1
                )


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                 api_key=os.environ.get('OPENAI_API_KEY'),
                 api_base=os.environ.get('OPENAI_API_BASE'),
                 api_type=os.environ.get('OPENAI_API_TYPE'),
                 api_version=os.environ.get('OPENAI_API_VERSION'),
                 model_name=os.environ.get('MODEL_NAME_EMBEDDING')) 

 
embedding_function = OpenAIEmbeddings(
                        api_key=os.environ.get('OPENAI_API_KEY'),
                        openai_api_base=os.environ.get('OPENAI_API_BASE'),
                        openai_api_type=os.environ.get('OPENAI_API_TYPE'),
                        api_version=os.environ.get('OPENAI_API_VERSION'),
                        deployment=os.environ.get('MODEL_NAME_EMBEDDING'),
                        model=os.environ.get('MODEL'))