import time

import streamlit as st
from agent.react_agent import ReactAgent

# 标题
st.title("智扫通机器人智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()#实例

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])#接收execute_stream返回的流式响应

# 用户输入提示词
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):

            for chunk in generator:
                cache_list.append(chunk)

                for char in chunk:
                    time.sleep(0.01)
                    yield char

        #capture 函数将每个 chunk 添加到 response_messages 列表中，并逐字符地显示在聊天界面上，模拟打字效果。
        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        #完整的模型响应会被添加到
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()


#app.py (用户输入) -> ReactAgent (代理初始化，包含模型和工具) -> model/factory.py (根据 config/rag.yml 配置实例化 ChatTongyi 千问模型) -> ReactAgent (执行代理逻辑，调用千问模型和相关工具) -> app.py (流式显示千问模型的回答)。