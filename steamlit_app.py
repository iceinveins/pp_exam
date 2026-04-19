import streamlit as st
import pandas as pd

st.title("企业党建知识刷题宝")

# 读取你整理好的xlsx
df = pd.read_excel("整理后的题库.xlsx")

# 初始化进度
if 'index' not in st.session_state:
    st.session_state.index = 0

curr_row = df.iloc[st.session_state.index]

# 显示题目（包含你之前移进去的选项）
st.write(f"### 第 {st.session_state.index + 1} 题")
st.text(curr_row[0]) 

# 用户选择
user_ans = st.radio("请选择答案：", ["A", "B", "C", "D"], key=st.session_state.index)

if st.button("提交"):
    if user_ans == curr_row['答案']:
        st.success("回答正确！")
    else:
        st.error(f"回答错误，正确答案是：{curr_row['答案']}")
    st.info(f"解析：{curr_row['解析']}")

if st.button("下一题"):
    st.session_state.index += 1
    st.rerun()