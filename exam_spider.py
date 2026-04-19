import time
import pandas as pd
import re
import os
import random
import shutil
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 配置 ---
DB_FILE = "题库总表.xlsx"
RUN_COUNT = 10  # 调多点也没关系

def clean_q_text(text):
    """去除第几题前缀及空白，用于去重"""
    text = re.sub(r'^第\d+题\s*', '', text)
    return "".join(text.split())

def click_element_safely(driver, xpaths):
    for xpath in xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    return True
        except: continue
    return False

def smart_navigate(driver):
    time.sleep(random.uniform(3, 5)) 
    click_element_safely(driver, ["//div[contains(text(), '交卷')]", "//button[contains(., '交卷')]"])
    time.sleep(2)
    click_element_safely(driver, ["//button[contains(., '确认')]", "//span[contains(., '确认')]"])
    time.sleep(2)
    
    print("   等待解析页面加载...")
    for _ in range(20):
        if "正确答案" in driver.page_source:
            return True
        click_element_safely(driver, ["//div[contains(text(), '查看试卷')]", "//button[contains(., '查看试卷')]"])
        time.sleep(2)
    return False

def scrape_session(driver):
    data = []
    while True:
        time.sleep(2)
        ans_els = driver.find_elements(By.XPATH, "//*[contains(text(), '正确答案：')]")
        for ae in ans_els:
            try:
                parent = ae.find_element(By.XPATH, "./ancestor::div[contains(@class, 'item') or count(div)>2][1]")
                lines = [l.strip() for l in parent.text.split('\n') if l.strip()]
                idx = next(i for i, line in enumerate(lines) if "正确答案：" in line)
                raw_body = "\n".join(lines[:idx])
                data.append({
                    "唯一标识": clean_q_text(raw_body),
                    "题目内容": raw_body,
                    "答案": lines[idx].replace("正确答案：", "").strip(),
                    "解析": "\n".join(lines[idx+1:])
                })
            except: continue

        try:
            next_btn = driver.find_element(By.XPATH, "//*[contains(text(), '下一页')]")
            if next_btn.is_displayed() and "disabled" not in next_btn.get_attribute("class"):
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(random.uniform(1, 2))
            else: break
        except: break
    return data

def run():
    # 初始化题库
    if os.path.exists(DB_FILE):
        db_df = pd.read_excel(DB_FILE)
    else:
        db_df = pd.DataFrame(columns=["唯一标识", "题目内容", "答案", "解析"])
    
    existing_ids = set(db_df['唯一标识'].astype(str).tolist())

    for i in range(RUN_COUNT):
        # 1. 强力清理残留进程 (针对 Windows)
        try:
            subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, capture_output=True)
        except: pass

        print(f"\n--- 第 {i+1} 轮开始 (库内: {len(db_df)} 题) ---")
        
        # 2. 创建纯净的临时用户目录，防止 Session 锁死
        tmp_user_dir = tempfile.mkdtemp()
        
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={tmp_user_dir}") # 隔离环境
        chrome_options.add_argument("--incognito") # 无痕
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = None
        try:
            # 增加初始化超时设置
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(40) 

            driver.get("https://gzwexam.shitac.net/#/pcPractise?exerciseRoleId=10")
            
            if smart_navigate(driver):
                new_data = scrape_session(driver)
                added = 0
                for item in new_data:
                    if item['唯一标识'] not in existing_ids:
                        db_df = pd.concat([db_df, pd.DataFrame([item])], ignore_index=True)
                        existing_ids.add(item['唯一标识'])
                        added += 1
                
                print(f"✅ 成功！新增 {added} 题")
                db_df.to_excel(DB_FILE, index=False)
            else:
                print("❌ 无法进入解析页")
                
        except Exception as e:
            print(f"⚠️ 轮次异常: {e}")
        finally:
            if driver:
                driver.quit()
            # 3. 清理临时目录
            time.sleep(2)
            try:
                shutil.rmtree(tmp_user_dir)
            except: pass
            
            wait_time = random.randint(8, 15)
            print(f"等待 {wait_time} 秒释放资源...")
            time.sleep(wait_time)

if __name__ == "__main__":
    run()