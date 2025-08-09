# myapp/rag_chain.py
import os
import bs4
from langchain_community.chat_models import ChatZhipuAI
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
load_dotenv()
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")


llm = ChatZhipuAI(model="glm-4", temperature=0.7, api_key=ZHIPUAI_API_KEY)


""" # 加载网页数据（只解析指定 class）
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
) """
loader = TextLoader("D:\\desktop\\code\\zr\\polls\\rag\\touzi.txt", encoding="utf-8")

docs = loader.load()

# 文本切分
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# 嵌入模型
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 向量数据库（持久化，避免每次重建）
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory="chroma_db"
)


# 检索器
retriever = vectorstore.as_retriever()

# Prompt 模板
prompt = hub.pull("rlm/rag-prompt")


# 格式化文档
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 构建 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 对外暴露一个方法
def get_rag_answer(question: str):
    # rag_chain.stream 返回的是一个迭代器，逐步产出字符串片段
    for chunk in rag_chain.stream(question):
        yield chunk
