# rag.py
import os
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing import Sequence
from typing_extensions import Annotated, TypedDict
from langchain_core.documents import Document
from langchain_community.chat_models import ChatZhipuAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

load_dotenv()
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")


model_name = "sentence-transformers/all-MiniLM-L6-v2"
# 创建 HuggingFaceEmbeddings 实例
embedding = HuggingFaceEmbeddings(model_name=model_name)
vector_store = InMemoryVectorStore(embedding)
llm = ChatZhipuAI(model="glm-4", temperature=0.7,api_key=ZHIPUAI_API_KEY)
prompt = hub.pull("rlm/rag-prompt")

# 1. 加载并分块
loader = TextLoader(r"D:\desktop\code\zr\polls\rag\touzi.txt", encoding="utf-8")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# 假设 vector_store 已经初始化
_ = vector_store.add_documents(documents=all_splits)


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: list[Document]

def retrieve(state: State):
    latest_human_msg = state["messages"][-1].content
    retrieved_docs = vector_store.similarity_search(latest_human_msg)
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    latest_question = state["messages"]
    messages = prompt.invoke({"question": latest_question, "context": docs_content})
    response = llm.invoke(messages)
    return {"messages": [AIMessage(content=response.content)]}

graph_builder = StateGraph(state_schema=State)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")

memory = InMemorySaver()
app = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}

def get_rag_answer(input_messages):
    """
    传入消息列表 input_messages，流式返回模型输出字符串片段
    """
    # input_messages是BaseMessage列表，比如 [HumanMessage(content=...)]
    input = [HumanMessage(content=input_messages)]
    # 使用 app.stream 流式调用，stream_mode="messages"
    for chunk, metadata in app.stream(
        {"messages": input},
        config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):  # 只处理模型回复
            # chunk.content 是本次返回的文本片段
            yield chunk.content
