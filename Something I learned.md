### 1 项目结构图

- D:\CollegeOUC\HM_agent
  - app.py
  - config
    - prompts.yml
    - rag.yml
    - chroma.yml
    - agent.yml
  - prompts
    - main_prompt.txt
    - rag_summarize.txt
    - report_prompt.txt
  - model
    - factory.py
  - agent
    - react_agent.py
    - tools
      - agent_tools.py
      - middleware.py
  - rag
    - rag_service.py
    - vector_store.py
  - utils
    - config_handler.py
    - path_tool.py
    - prompt_loader.py
    - file_handler.py
    - logger_handler.py
  - data
    - external
      - records.csv
  - chroma_db/ (持久化向量数据库目录，路径由 config/chroma.yml 指定)
  - logs/ (日志输出目录，逻辑在 logger_handler 中创建并写入)
  - list/ (环境/虚拟环境相关内容，运行时依赖于此目录的 python.exe 等)

逐个文件作用注释（按文件路径逐一标注，便于查找）

- app.py
  - 作用：Streamlit 的前端入口，用于展示聊天界面、接收用户输入并通过后端 ReactAgent 产生流式输出。
  - 使用场景：用户在网页上提问时，触发整个对话推理流程。
- config/prompts.yml
  - 作用：定义指向系统提示与各种提示文本文件的路径配置，供加载系统提示和 Rag 提示时使用。
- config/rag.yml
  - 作用：RAG 配置文件；指定 chat_model_name（用于选择大模型名称）和相关 Rag 设置。
- config/chroma.yml
  - 作用：向量数据库（Chroma）的配置：集合名、持久化目录、检索参数、数据分片参数等。
- config/agent.yml
  - 作用：代理相关的配置信息，例如 external_data_path、数据源位置等。
- prompts/main_prompt.txt
  - 作用：系统级核心提示文本，定义代理的工作流程、工具使用规则、以及多轮对话的思考/行动/观察流程。
- prompts/rag_summarize.txt
  - 作用：RAG 检索阶段的提示模板，规定输入格式、上下文拼接、以及输出约束。
- prompts/report_prompt.txt
  - 作用：生成使用报告的文本模板/结构，指导模型输出报告性文本。
- model/factory.py
  - 作用：模型与嵌入模型的工厂，提供全局可用的模型实例。
  - 关键点：
    - ChatModelFactory.generator()：返回 ChatTongyi 模型实例，基于 rag_conf["chat_model_name"]。
    - EmbeddingsFactory.generator()：返回 DashScopeEmbeddings 实例，用作文本向量化。
    - 全局变量：chat_model、embed_model，供后续模块使用。
- agent/react_agent.py
  - 作用：封装 LangChain 的代理客户端，加载系统提示、工具集合、以及中间件，提供 execute_stream() 方法实现流式输出。
  - 功能点：将用户输入转化为对模型的输入，逐步输出模型回答。
- agent/tools/agent_tools.py
  - 作用：定义 LangChain 工具函数，供代理在对话中调用以获取上下文和数据。
  - 具体工具及职责：
    - rag_summarize(query)：从向量库检索相关资料并生成摘要，提供上下文用于回答。
    - get_weather(city)：返回指定城市的天气信息字符串。
    - get_user_location()、get_user_id()、get_current_month()：无参工具，返回当前城市、用户ID、当前月份等信息。
    - fetch_external_data(user_id, month)：从外部数据源（data/external/records.csv）读取指定用户在指定月份的使用记录。
    - fill_context_for_report()：触发上下文填充，仅用于报告生成场景。
- agent/tools/middleware.py
  - 作用：实现工具调用的中间件，包含日志、监控与动态提示切换等功能。
  - 主要职责：
    - monitor_tool：记录工具调用信息，必要时修改运行时上下文（如设置 report 标志）。
    - log_before_model：在模型执行前输出日志，便于调试。
    - report_prompt_switch：根据上下文动态切换提示文本（普通对话 vs 报告场景）。
- rag/rag_service.py
  - 作用：RAG 的核心服务类，负责把查询进行向量检索并把检索得到的上下文与查询通过模型链生成回答。
  - 关键流程：通过 VectorStoreService 的检索器获取上下文，将输入与上下文送入模型链，输出最终文本。
- rag/vector_store.py
  - 作用：对向量数据库（Chroma）的封装，提供初始化、文档加载、分片、去重以及检索器获取等功能。
  - 主要点：
    - 使用 DashScopeEmbeddings 作为嵌入模型，使用 RecursiveCharacterTextSplitter 进行文本分片。
    - load_document() 从 data 路径读取 txt/pdf，计算 MD5 进行去重后再分片写入向量库。
    - get_retriever() 提供向量检索器，供 rag_service 调用。
- utils/config_handler.py
  - 作用：集中加载 YAML 配置并暴露全局变量：rag_conf、chroma_conf、prompts_conf、agent_conf。
  - 作用过程：提供统一的配置信息入口，确保各模块遵循同一配置。
- utils/prompt_loader.py
  - 作用：加载 prompts.yml 指定的系统提示、RAG 提示、报告提示等文本路径，并读取文本内容。
  - 主要函数：load_system_prompts()、load_rag_prompts()、load_report_prompts()。
- utils/file_handler.py
  - 作用：文件相关帮助工具，包含：
    - get_file_md5_hex(filepath)：计算文件 MD5（用于去重）。
    - listdir_with_allowed_type(path, allowed_types)：列出目录下符合允许后缀的文件。
    - pdf_loader(filepath)、txt_loader(filepath)：将 PDF/TXT 文件加载为 LangChain 文档对象。
- utils/logger_handler.py
  - 作用：提供全局日志器，统一输出到控制台和日志文件，方便调试与追踪。
- data/external/records.csv
  - 作用：外部数据样本，供 fetch_external_data 工具读取，用于生成个性化使用报告。
- chroma_db/ (由 config/chroma.yml 指定 persist_directory)
  - 作用：Chroma 向量数据库的实际存储目录，保存文本分片的嵌入向量和元数据。
- logs/（若存在，由 logger_handler 管理）
  - 作用：运行时日志输出文件夹，用于持久化运行日志。

### 2 技术栈

Agent：Langchain

RAG：Langchain

向量数据库：chroma_db

前端网页：Streamlit

RAG去重：md5

### 3 工作流

#### 总体流程

app.py (用户输入) -> ReactAgent (代理初始化，包含模型和工具) -> model/factory.py (根据 config/rag.yml 配置实例化 ChatTongyi 千问模型) -> ReactAgent (执行代理逻辑，调用千问模型和相关工具) -> app.py (流式显示模型的回答)

#### 细节拆分

1. 用户输入 (app.py)

- 用户在 app.py 中通过 Streamlit 的 st.chat_input() 输入问题。
- 输入的问题被添加到 st.session_state["message"] 中，并显示在聊天界面上。
2. Agent 处理 (agent/react_agent.py)

- 当用户输入问题后， app.py 会调用 st.session_state["agent"].execute_stream(prompt) 。
- st.session_state["agent"] 是 ReactAgent 的一个实例，它在 app.py 启动时被初始化。
- ReactAgent 的 __init__ 方法中，通过 create_agent 函数创建了一个代理（agent）。这个代理的核心是 model=chat_model 。
3. 模型工厂 (model/factory.py)

- chat_model 是在 model/factory.py 中定义的。
- chat_model = ChatModelFactory().generator() 这一行代码创建了一个 ChatTongyi 实例。
- ChatTongyi 是 langchain_community.chat_models.tongyi 模块中的一个类，它负责与阿里云的通义千问模型进行交互。
- ChatTongyi 的 model 参数被设置为 rag_conf["chat_model_name"] 。
4. 配置加载 (config/rag.yml)

- rag_conf 是通过 utils.config_handler 加载的配置。
- 在 config/rag.yml 文件中， chat_model_name: qwen3-max 明确指定了使用的千问模型是 qwen3-max 。
5. 代理执行与流式响应 (agent/react_agent.py)

- ReactAgent 的 execute_stream 方法接收用户查询，并将其封装成 input_dict 。
- self.agent.stream(input_dict, stream_mode="values", context={"report": False}) 调用代理的 stream 方法，以流式方式获取模型的响应。
- 代理在执行过程中，会根据 system_prompt 和 tools （例如 rag_summarize , get_weather 等）进行思考和工具调用。
- middleware （例如 monitor_tool , log_before_model , report_prompt_switch ）会在模型调用前后执行，用于监控、日志记录和动态提示词切换。
- 模型返回的每个 chunk 都会被 execute_stream 方法 yield 出来。
6. 响应显示 (app.py)

- app.py 中的 st.chat_message("assistant").write_stream(capture(res_stream, response_messages)) 接收 execute_stream 返回的流式响应。
- capture 函数将每个 chunk 添加到 response_messages 列表中，并逐字符地显示在聊天界面上，模拟打字效果。
- 最终，完整的模型响应会被添加到 st.session_state["message"] 中。 


先做multi-agent同进程，再做unicorn跨进程