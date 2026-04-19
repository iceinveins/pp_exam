import pandas as pd
import re
import os

def process_bank(input_file, output_file):
    print(f"正在处理: {input_file}")
    
    # 1. 健壮的读取逻辑
    ext = os.path.splitext(input_file)[-1].lower()
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            # 解决编码问题，优先尝试 utf-8-sig (带BOM的utf8)
            try:
                df = pd.read_csv(input_file, sep=None, engine='python', encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(input_file, sep=None, engine='python', encoding='gbk')
    except Exception as e:
        print(f"读取失败! 提示: 如果你手动把 .xlsx 改成了 .csv，请改回 .xlsx 后运行。")
        print(f"原始错误: {e}")
        return

    # 2. 删除第二列 (题目内容)
    if df.shape[1] > 1:
        cols = df.columns.tolist()
        df = df.drop(columns=[cols[1]])

    # 3. 核心逻辑：提取并剪切选项
    def clean_and_move(row):
        title = str(row.iloc[0])   # 第一列题干
        analysis = str(row.get('解析', '')) # 解析列
        
        # 匹配以 A 开头的部分 (处理判断题 AB 或选择题 ABCD)
        # 匹配模式：寻找 A 前面有空白符或位于行首的部分
        pattern = r'([\n\s]*A[\.\s\n].*)'
        match = re.search(pattern, analysis, re.DOTALL)
        
        if match:
            options_block = match.group(1)
            # 拼接题干
            new_title = f"{title}\n{options_block.strip()}"
            # 从解析中删除该部分
            new_analysis = analysis.replace(options_block, "").strip()
            return new_title, new_analysis
        return title, analysis

    # 使用 expand=True 避免 zip 解包报错
    results = df.apply(clean_and_move, axis=1, result_type='expand')
    df.iloc[:, 0] = results[0]
    df['解析'] = results[1]

    # 4. 保存为 XLSX
    df.to_excel(output_file, index=False)
    print(f"处理成功！结果已保存至: {output_file}")

if __name__ == "__main__":
    # 请根据你的实际文件名修改此处
    input_fn = "题库总表.xlsx" 
    output_fn = "整理后的题库.xlsx"
    process_bank(input_fn, output_fn)