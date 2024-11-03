
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from dotenv import load_dotenv
import chainlit as cl
from langchain_core.runnables import RunnablePassthrough

# Import the MetadataFilteredRetriever class
from metadata_filtered_retriever import MetadataFilteredRetriever

# Load environment variables
load_dotenv()

@cl.on_chat_start
async def on_chat_start():
    """Triggered when a chat starts, initializes LLM and retrievers."""
    ehs = ChatBedrockConverse(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        temperature=0,
        max_tokens=None
    )

    embeddings = BedrockEmbeddings(
        credentials_profile_name="default",
        region_name="us-west-2",
        model_id='amazon.titan-embed-text-v2:0',
    )

    # Initialize the retriever manager
    retriever_manager = MetadataFilteredRetriever(
        embeddings=embeddings,
        persist_directory="../vector/my_embeddings/test2",
        collection_name="my_collection"
    )
    
    # Create different retrievers for different contexts
    retrievers = {
        "quebec": retriever_manager.get_retriever(province="quebec"),
        "default": retriever_manager.get_retriever(province="general"),
    }
    
    # Store all necessary elements in the session
    cl.user_session.set("retrievers", retrievers)
    cl.user_session.set("ehs", ehs)
    cl.user_session.set("current_retriever", "default")  # Set default context

    await cl.Message(content="Connected to Chainlit! Using default context by default.").send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handles incoming messages and processes commands."""
    # Retrieve stored components
    retrievers = cl.user_session.get("retrievers")
    ehs = cl.user_session.get("ehs")
    current_retriever = cl.user_session.get("current_retriever")
    
    # Check if the message contains a command to change context
    if message.content.startswith("/context"):
        new_context = message.content.split()[1]
        if new_context in retrievers:
            cl.user_session.set("current_retriever", new_context)
            await cl.Message(content=f"Switched to {new_context} context.").send()
            return
        else:
            await cl.Message(content="Invalid context. Available contexts: " + 
                             ", ".join(retrievers.keys())).send()
            return

    # Create and execute the RAG chain with the current retriever
    rag_chain = create_chain(ehs, retrievers[current_retriever])
    res = rag_chain.invoke(message.content)
    await cl.Message(content=res).send()

def create_chain(llm, retriever):
    """Creates a RAG chain for processing queries."""
    template = """
    You are an assistant. Use the following pieces of retrieved context to answer the question.\n
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\n
    Question: {question}\n
    Context: {context}\n
    Answer: """
    
    prompt = PromptTemplate(template=template, input_variables=['question', 'context'])
    
    def format_docs(docs):
        """Formats retrieved documents for the prompt."""
        return "\n\n".join(doc.page_content for doc in docs)

    # Create chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
