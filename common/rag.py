import uuid, logging
from pathlib import Path
from common.file import getFolderSize
from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.core import ServiceContext, SimpleDirectoryReader, PromptHelper, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore 
from llama_index.core import StorageContext
from llama_index.core import Settings
from llama_index.core.node_parser import TokenTextSplitter, SimpleNodeParser
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
from llama_index.llms.openai import OpenAI
import tiktoken

class pedRAG:

    def __init__(self, llmModel = "gpt-3.5-turbo", maxTokens = 800, maxModelRetry = 2, temperature = 0.5, \
                        top_p = 1.0, frequency_penalty=0.0, presence_penalty=0.0):
        self.qdClient = QdrantClient(
                                url="https://2832bf98-d911-4b70-b3a5-f7fcc0e4dc78.us-east4-0.gcp.cloud.qdrant.io:6333",
                                api_key="",
                            )
        self.llm = OpenAI(model=llmModel, 
                          api_key= "", 
                          max_tokens=maxTokens, 
                          temperature= temperature,
                          top_p= top_p,
                          frequency_penalty = frequency_penalty,
                          presence_penalty = presence_penalty,
                          max_retries=maxModelRetry)
        
        self.embed_model = OpenAIEmbedding(model="text-embedding-3-large", 
                                           api_key="")

        # self.aclient = AsyncQdrantClient( url="https://2832bf98-d911-4b70-b3a5-f7fcc0e4dc78.us-east4-0.gcp.cloud.qdrant.io:6333",
        #     api_key="",
        # )

    # Create an index using a chat model, so that we can use the chat prompts!
    def createVectorCollection(self, filePath):

        try:
            # check for path's existance
            if not Path(filePath).exists():
                return None

            # check for total file size
            fileSize = getFolderSize(filePath)
            if fileSize > 1000000:
                logging.debug("Method createVectorCollection:: Files are more than 1 MB in size. Quiting vector creation.")
                return None
                                    
            documents = SimpleDirectoryReader(filePath).load_data()

            text_splitter = TokenTextSplitter(
                    separator=" ",
                    chunk_size=1024,
                    chunk_overlap=20,
                    backup_separators=["\n"],
                    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
                    )

            node_parser = SimpleNodeParser.from_defaults( chunk_size=1024)
            
            prompt_helper = PromptHelper(
                context_window=4096, 
                num_output=256, 
                chunk_overlap_ratio=0.1, 
                chunk_size_limit=None
                )

            service_context = ServiceContext.from_defaults(
                llm=self.llm,
                embed_model=self.embed_model,
                node_parser=node_parser,
                prompt_helper=prompt_helper
                )

            # commented hybrid index because of Space crunch
            #create qdrant collection with hybrid search on dense and sparse vectors
            # batch size is the # of nodes at a time will be encoded in sparse vectors
            self.collection_name = str(uuid.uuid1())
            vector_store = QdrantVectorStore(client=self.qdClient, 
                                            #  aclient=aclient, 
                                            enable_hybrid=False, 
                                            #  batch_size=20,
                                            collection_name=self.collection_name)

            
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_documents( documents,
                                                    transformations=[text_splitter],
                                                    service_context=service_context,
                                                    storage_context=storage_context,
                                                    # use_async=True,
                                                )
            #hybrid query for better result
            # self.query_engine = index.as_query_engine(similarity_top_k=2,
            #                                         # sparse_top_k=10,
            #                                         # vector_store_query_mode="hybrid"
            #                                         )
            

            return self.collection_name
        
        except Exception as e:
            logging.error("Error in createVectorCollection method in rag file::" + str(e))

        return None

    def utilizeVectorCollection(self, collection_name):
        try:

            self.collection_name = collection_name
            vector_store = QdrantVectorStore(client=self.qdClient, 
                                             collection_name=collection_name)

            # Create a StorageContext with the vector store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Create a VectorStoreIndex
            self.index = VectorStoreIndex.from_vector_store(storage_context=storage_context, 
                                                            vector_store=vector_store)

            return self.collection_name

        except Exception as e:
            logging.error("Error in executePromptwithContext method in rag file::" + str(e))

        return None


    def executePrompt(self, systemrole, prompt):

        # chat_text_qa_msgs = [
        # ChatMessage(
        #         role=MessageRole.SYSTEM,
        #         content=(
        #             systemrole
        #         ),
        #     ),
        # ]
        # text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

        response = self.index.as_query_engine(
                                    # text_qa_template=text_qa_template
                                ).query(prompt)
        
        print(response.response if response is not None else None)

        return response.response


    def __del__(self):
        # delete the index
        if hasattr(self, 'collection_name') and self.qdClient.collection_exists(self.collection_name):
            self.qdClient.delete_collection(self.collection_name)
