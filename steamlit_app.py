import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="知识刷题小程序", layout="centered")

# 检查文件是否存在
file_path = "整理后的题库.xlsx"

if not os.path.exists(file_path):
    st.error(f"未找到文件：{file_path}，请确保文件已上传至 GitHub 仓库。")
else:
    @st.cache_data
    def load_data():
        return pd.read_excel(file_path)

    df = load_data()

    # 初始化 Session State
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False

    # 答题进度
    total_questions = len(df)
    st.progress((st.session_state.index + 1) / total_questions)
    st.sidebar.write(f"当前进度: {st.session_state.index + 1} / {total_questions}")

    # 获取当前题目数据
    curr_row = df.iloc[st.session_state.index]
    
    st.subheader(f"第 {st.session_state.index + 1} 题")
    # 显示题干和选项（之前处理过的第一列）
    st.info(curr_row.iloc[0])

    # 选项交互
    options = ["A", "B", "C", "D"] if "C" in str(curr_row.iloc[0]) else ["A", "B"]
    user_ans = st.radio("请选择你的答案：", options, key=f"q_{st.session_state.index}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("提交答案", use_container_width=True):
            st.session_state.show_answer = True

    with col2:
        if st.button("下一题", use_container_width=True):
            if st.session_state.index < total_questions - 1:
                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()
            else:
                st.balloons()
                st.success("恭喜！你已完成所有题目。")

    # 显示结果和解析
    if st.session_state.show_answer:
        correct_ans = str(curr_row['答案']).strip()
        if user_ans == correct_ans:
            st.success(f"回答正确！ ✅")
        else:
            st.error(f"回答错误！ ❌ 正确答案是：{correct_ans}")
        
        with st.expander("查看题目解析", expanded=True):
            st.write(curr_row['解析'] if pd.notna(curr_row['解析']) else "暂无解析")

    # 重置功能
    if st.sidebar.button("重置练习"):
        st.session_state.index = 0
        st.session_state.show_answer = False
        st.rerun()