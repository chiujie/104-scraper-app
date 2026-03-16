import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time
import urllib.parse
import re
import urllib3 # 🌟 新增：用來處理憑證警告

# 🌟 新增：關閉「不安全連線」的警告訊息，讓畫面保持乾淨
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="職缺爬蟲小工具", page_icon="🔍")
st.title("🚀 1111 職缺爬蟲與下載器 (略過憑證版)")
st.write("只要輸入關鍵字，就能自動爬取 1111 人力銀行的職缺並下載成 Excel。")

# 輸入區塊
keyword = st.text_input("請輸入你想搜尋的職缺關鍵字 (例如：AI, 軟體工程師)：")

if st.button("開始爬蟲"):
    if keyword:
        with st.spinner(f"正在前往 1111 爬取「{keyword}」的資料，請稍候..."):
            
            # 將中文字轉換成 URL 編碼
            encoded_keyword = urllib.parse.quote(keyword)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            jobs_data = []
            
            # 預設爬取前 3 頁
            for page in range(1, 4): 
                # 換成 1111 的搜尋網址
                url = f"https://www.1111.com.tw/search/job?ks={encoded_keyword}&page={page}"
                
                try:
                    # 🌟 關鍵修改：加入 verify=False 強制略過 SSL 憑證檢查
                    res = requests.get(url, headers=headers, verify=False)
                    res.raise_for_status()
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    # 1111 的職缺連結特徵 (包含 /job/數字)
                    job_links = soup.find_all('a', href=re.compile(r'/job/\d+'))
                    
                    for a in job_links:
                        # 抓取職缺標題
                        title = a.get('title') or a.text.strip()
                        link = a.get('href')
                        
                        # 補齊完整網址
                        if link and link.startswith('/'):
                            link = "https://www.1111.com.tw" + link
                            
                        if not title or len(title) < 2:
                            continue
                            
                        # 尋找公司名稱 (從父節點往下找 corp 連結)
                        company = "未知公司"
                        parent = a.find_parent('div', class_=re.compile(r'job|item', re.I))
                        if parent:
                            comp_a = parent.find('a', href=re.compile(r'/corp/\d+'))
                            if comp_a:
                                company = comp_a.get('title') or comp_a.text.strip()
                        
                        # 清理排版空白
                        title = title.replace('\n', '').strip()
                        company = company.replace('\n', '').strip()
                        
                        jobs_data.append({
                            '職缺名稱': title,
                            '公司名稱': company,
                            '職缺連結': link
                        })
                        
                    time.sleep(1) # 停頓1秒避免過度請求
                except Exception as e:
                    st.error(f"第 {page} 頁爬取發生錯誤: {e}")
                    break

            if jobs_data:
                # 轉成 DataFrame 並用「職缺連結」去除重複的卡片
                df = pd.DataFrame(jobs_data).drop_duplicates(subset=['職缺連結'])
                st.success(f"✅ 爬取完成！共找到 {len(df)} 筆不重複的職缺。")
                
                # 預覽前幾筆資料
                st.dataframe(df.head())
                
                # 將 DataFrame 轉成 Excel 供下載
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='職缺')
                excel_data = output.getvalue()
                
                # 下載按鈕
                st.download_button(
                    label="📥 點我下載 1111 Excel 檔案",
                    data=excel_data,
                    file_name=f"1111職缺_{keyword}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("沒有找到職缺資料。")
    else:
        st.error("請先輸入關鍵字！")
