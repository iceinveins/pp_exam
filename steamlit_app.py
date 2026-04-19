import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="知识刷题小程序", layout="centered")

# 配置文件路径
file_path = "整理后的题库.xlsx"

if not os.path.exists(file_path):
    st.error(f"未找到文件：{file_path}，请确保文件已上传至 GitHub 仓库并配置了 requirements.txt")
else:
    @st.cache_data
    def load_data():
        return pd.read_excel(file_path)

    df = load_data()
    total_questions = len(df)

    # --- 初始化 Session State ---
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total_questions))
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'is_random' not in st.session_state:
        st.session_state.is_random = False

    # --- 侧边栏设置 ---
    st.sidebar.title("设置")
    
    # 随机模式开关
    random_mode = st.sidebar.checkbox("随机乱序练习", value=st.session_state.is_random)
    
    # 如果开关状态改变，重置顺序
    if random_mode != st.session_state.is_random:
        st.session_state.is_random = random_mode
        if random_mode:
            random.shuffle(st.session_state.question_order)
        else:
            st.session_state.question_order = list(range(total_questions))
        st.session_state.index = 0 # 切换模式从头开始
        st.rerun()

    if st.sidebar.button("重新开始练习"):
        if st.session_state.is_random:
            random.shuffle(st.session_state.question_order)
        st.session_state.index = 0
        st.session_state.show_answer = False
        st.rerun()

    # --- 主界面 ---
    # 根据映射表获取真实数据索引
    current_q_idx = st.session_state.question_order[st.session_state.index]
    curr_row = df.iloc[current_q_idx]

    st.sidebar.write(f"当前进度: {st.session_state.index + 1} / {total_questions}")
    st.progress((st.session_state.index + 1) / total_questions)

    st.subheader(f"第 {st.session_state.index + 1} 题")
    
    # 显示题干和选项
    st.info(curr_row.iloc[0])

    # 自动识别是判断题还是选择题来生成按钮
    question_text = str(curr_row.iloc[0])
    if "D" in question_text:
        options = ["A", "B", "C", "D"]
    elif "C" in question_text:
        options = ["A", "B", "C"]
    else:
        options = ["A", "B"]

    # 使用 radio 组件，key 绑定当前题目索引以防复用
    user_ans = st.radio("请选择你的答案：", options, key=f"q_{current_q_idx}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("查看解析", use_container_width=True):
            st.session_state.show_answer = True

    with col2:
        btn_text = "下一题" if st.session_state.index < total_questions - 1 else "完成"
        if st.button(btn_text, use_container_width=True):
            if st.session_state.index < total_questions - 1:
                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()
            else:
                st.balloons()
                st.success("恭喜！你已完成所有题目。")

    # --- 显示答案和解析 ---
    if st.session_state.show_answer:
        correct_ans = str(curr_row['答案']).strip()
        if user_ans == correct_ans:
            st.success(f"回答正确！ ✅ (正确答案: {correct_ans})")
        else:
            st.error(f"回答错误！ ❌ 正确答案是：{correct_ans}")
        
        with st.expander("题目解析", expanded=True):
            analysis_text = curr_row['解析']
            st.write(analysis_text if pd.notna(analysis_text) and str(analysis_text).strip() != "" else "暂无背景解析。")