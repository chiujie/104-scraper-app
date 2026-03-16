import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time

st.set_page_config(page_title="職缺爬蟲小工具", page_icon="🔍")
st.title("🚀 104 職缺爬蟲與下載器")
st.write("只要輸入關鍵字，就能自動爬取 104 人力銀行的職缺並下載成 Excel。")

# 輸入區塊
keyword = st.text_input("請輸入你想搜尋的職缺關鍵字 (例如：AI, 軟體工程師)：")

if st.button("開始爬蟲"):
    if keyword:
        with st.spinner(f"正在前往 104 爬取「{keyword}」的資料，請稍候..."):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            jobs_data = []
            
            # 預設爬取前 3 頁 (可自行修改 range)
            for page in range(1, 4): 
                url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}&page={page}&jobsource=2018indexpoc&ro=0"
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                articles = soup.find_all('article', class_='b-block--top-bord')
                
                for article in articles:
                    if article.get('data-job-no') is None:
                        continue
                    try:
                        title_tag = article.find('a', class_='js-job-link')
                        title = title_tag.text.strip()
                        link = "https:" + title_tag.get('href')
                        company = article.get('data-cust-name')
                        jobs_data.append({
                            '職缺名稱': title,
                            '公司名稱': company,
                            '職缺連結': link
                        })
                    except:
                        continue
                time.sleep(1) # 停頓1秒避免被封鎖

            if jobs_data:
                df = pd.DataFrame(jobs_data)
                st.success(f"✅ 爬取完成！共找到 {len(jobs_data)} 筆職缺。")
                
                # 預覽前幾筆資料
                st.dataframe(df.head())
                
                # 將 DataFrame 轉成 Excel 供下載
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='職缺')
                excel_data = output.getvalue()
                
                # 下載按鈕
                st.download_button(
                    label="📥 點我下載 Excel 檔案",
                    data=excel_data,
                    file_name=f"104職缺_{keyword}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("沒有找到相關職缺，請嘗試其他關鍵字。")
    else:
        st.error("請先輸入關鍵字！")
