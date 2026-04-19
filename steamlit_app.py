import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="知识刷题小程序", layout="centered")

# 配置文件路径
file_path = "整理后的题库.xlsx"

if not os.path.exists(file_path):
    st.error(f"未找到文件：{file_path}，请确保文件已上传并配置了 requirements.txt")
else:
    @st.cache_data
    def load_data():
        return pd.read_excel(file_path)

    df = load_data()
    total_questions = len(df)

    # --- 初始化 Session State ---
    # question_order: 当前模式下的题目索引序列
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total_questions))
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'is_random' not in st.session_state:
        st.session_state.is_random = False
    # wrong_questions: 字典格式 {题目索引: 错误次数}
    if 'wrong_questions' not in st.session_state:
        st.session_state.wrong_questions = {}
    # mode: 'all' (全部题目), 'wrong' (错题集)
    if 'mode' not in st.session_state:
        st.session_state.mode = 'all'

    # --- 侧边栏：功能控制 ---
    st.sidebar.title("控制面板")
    
    # 模式选择
    mode_options = {"全部题目": 'all', "错题本 ({}题)".format(len(st.session_state.wrong_questions)): 'wrong'}
    selected_mode_label = st.sidebar.radio("练习模式", list(mode_options.keys()))
    new_mode = mode_options[selected_mode_label]

    # 随机开关
    is_random = st.sidebar.checkbox("随机乱序", value=st.session_state.is_random)

    # 处理模式切换逻辑
    def reset_order():
        if st.session_state.mode == 'all':
            order = list(range(total_questions))
        else:
            order = list(st.session_state.wrong_questions.keys())
        
        if st.session_state.is_random:
            random.shuffle(order)
        
        st.session_state.question_order = order
        st.session_state.index = 0
        st.session_state.show_answer = False

    # 监听模式或随机状态改变
    if new_mode != st.session_state.mode or is_random != st.session_state.is_random:
        st.session_state.mode = new_mode
        st.session_state.is_random = is_random
        reset_order()
        st.rerun()

    if st.sidebar.button("重置当前进度"):
        reset_order()
        st.rerun()

    if st.sidebar.button("清空错题记录"):
        st.session_state.wrong_questions = {}
        if st.session_state.mode == 'wrong':
            st.session_state.mode = 'all'
        reset_order()
        st.rerun()

    # --- 主界面 ---
    if not st.session_state.question_order:
        st.warning("当前列表为空（可能是你还没有错题，快去练习吧！）")
    else:
        # 获取当前题目
        current_q_idx = st.session_state.question_order[st.session_state.index]
        curr_row = df.iloc[current_q_idx]

        # 进度条
        current_progress = st.session_state.index + 1
        total_in_mode = len(st.session_state.question_order)
        st.write(f"**模式：{selected_mode_label}**")
        st.progress(current_progress / total_in_mode)
        st.write(f"进度: {current_progress} / {total_in_mode}")

        # 如果是错题，显示错误频率
        if current_q_idx in st.session_state.wrong_questions:
            freq = st.session_state.wrong_questions[current_q_idx]
            st.caption(f"⚠️ 这道题你已经错过 {freq} 次了，请注意！")

        # 显示题干
        st.info(curr_row.iloc[0])

        # 选项识别
        question_text = str(curr_row.iloc[0])
        options = ["A", "B", "C", "D"] if "D" in question_text else (["A", "B", "C"] if "C" in question_text else ["A", "B"])
        
        user_ans = st.radio("选择答案：", options, key=f"q_{current_q_idx}_{st.session_state.index}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("提交/查看解析", use_container_width=True):
                st.session_state.show_answer = True
                # 记录错题逻辑
                correct_ans = str(curr_row['答案']).strip()
                if user_ans != correct_ans:
                    st.session_state.wrong_questions[current_q_idx] = st.session_state.wrong_questions.get(current_q_idx, 0) + 1
                elif st.session_state.mode == 'wrong' and user_ans == correct_ans:
                    # 如果在刷错题模式下答对了，可以选择是否移除（此处保持记录以便观察频率，或根据需要移除）
                    pass

        with col2:
            if st.button("下一题", use_container_width=True):
                if st.session_state.index < total_in_mode - 1:
                    st.session_state.index += 1
                    st.session_state.show_answer = False
                    st.rerun()
                else:
                    st.balloons()
                    st.success("本轮练习已完成！")

        # 显示解析
        if st.session_state.show_answer:
            correct_ans = str(curr_row['答案']).strip()
            if user_ans == correct_ans:
                st.success(f"回答正确！ ✅")
            else:
                st.error(f"回答错误！ ❌ 正确答案是：{correct_ans}")
            
            with st.expander("查看详细解析", expanded=True):
                st.write(curr_row['解析'] if pd.notna(curr_row['解析']) else "暂无解析")

    # 侧边栏统计
    st.sidebar.divider()
    st.sidebar.subheader("统计信息")
    st.sidebar.write(f"总题库数量: {total_questions}")
    st.sidebar.write(f"错题集数量: {len(st.session_state.wrong_questions)}")