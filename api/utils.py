import asyncio
from langchain_postgres.vectorstores import PGVector
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from squeme import BodyGenerate
from config import (PGV_USER,PGV_PASSWORD,PGV_HOST,PGV_PORT,
                 PGV_DATABASE_NAME,EMBEDDING_MODEL,UCN_MODEL_NAME,
                 OLLAMA_HOST,OLLAMA_PORT)
from squeme import LineListOutputParser


def initialize_retriever():
    connection = f'postgresql+psycopg://{PGV_USER}:{PGV_PASSWORD}@{PGV_HOST}:{PGV_PORT}/{PGV_DATABASE_NAME}'
    vector_store = PGVector(
                embeddings=moder_for_embedding,
                connection=connection,
                use_jsonb=True,
            )
    retriever = vector_store.as_retriever(search_kwargs={"k":2})

    
    return retriever
def initialize_multiquery_retriever(retriever,llm_chain):
    retriever_from_llm=MultiQueryRetriever(retriever=retriever,llm_chain=llm_chain,parser_key="lines")
    #k: número de documentos a retornar
    return retriever_from_llm

def get_context(query):

    documents = retriever.invoke(input=query)

    context = "\n".join([doc.page_content for doc in documents])

    return context

def get_multi_query_context(query):
    
    documents = multi_query_retriever.invoke(query)
    
    context = "\n".join([doc.page_content for doc in documents])

    return context

def format_ollama_messages(body:BodyGenerate):
    history= body.history
    messages = []
    context= get_multi_query_context(body.query)
    for item in history:
        messages.append({
            "role": "user",
            "content": item.query
        })
        messages.append({
            "role": "assistant",
            "content": item.answer
        })
    content=f"[Este es tu contexto para responder la pregunta] {context} y [esta es la pregunta del estudiante]: {body.query}"
    messages.append({"role":"user","content":content})
    print(messages)
    return messages


#for websocket endpoint
async def stream(query):
    loop = asyncio.get_event_loop()
    context= get_context(query)

    prompt = f"""
        [Contexto] : {context} + '\n'
        [Pregunta Alumno]: {query}    
    """
    print(prompt)
    stream_gen = await loop.run_in_executor(None, model.stream, prompt)
    for response in stream_gen:
        print(response)
        yield response




QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Your task is to generate 4
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions directly as separate lines, without introducing them or adding a header.
    Original question: {question}"""
)

ollam_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

model = OllamaLLM(model=UCN_MODEL_NAME,host=OLLAMA_HOST,port=OLLAMA_PORT)

moder_for_embedding = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

model_for_multiQueryRetriever= OllamaLLM(model=UCN_MODEL_NAME,host=OLLAMA_HOST,port=OLLAMA_PORT)

output_parser = LineListOutputParser()

llm_chain= QUERY_PROMPT | model_for_multiQueryRetriever | output_parser

retriever= initialize_retriever()

multi_query_retriever= initialize_multiquery_retriever(retriever=retriever,llm_chain=llm_chain)