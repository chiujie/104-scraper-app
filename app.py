import streamlit as st
import requests
import pandas as pd
import io
import time

st.set_page_config(page_title="職缺爬蟲小工具", page_icon="🔍")
st.title("🚀 104 職缺爬蟲與下載器 (API 版)")
st.write("只要輸入關鍵字，就能自動爬取 104 人力銀行的職缺並下載成 Excel。")

# 輸入區塊
keyword = st.text_input("請輸入你想搜尋的職缺關鍵字 (例如：AI, 軟體工程師)：")

if st.button("開始爬蟲"):
    if keyword:
        with st.spinner(f"正在透過 API 爬取「{keyword}」的資料，請稍候..."):
            # 必須加上 Referer 偽裝成從 104 首頁搜尋過來的
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Referer': f'https://www.104.com.tw/jobs/search/?keyword={keyword}'
            }
            jobs_data = []
            
            # 預設爬取前 3 頁
            for page in range(1, 4): 
                # 改用 104 背後真實傳輸資料的 API 網址 (回傳 JSON 格式)
                url = f"https://www.104.com.tw/jobs/search/list?keyword={keyword}&page={page}&jobsource=2018indexpoc&ro=0"
                
                try:
                    res = requests.get(url, headers=headers)
                    res.raise_for_status() # 檢查是否被 104 阻擋
                    data = res.json()
                    
                    # 從 JSON 結構中提取職缺列表
                    job_list = data.get('data', {}).get('list', [])
                    
                    for job in job_list:
                        title = job.get('jobName', '')
                        company = job.get('custName', '')
                        
                        # 處理連結，有些 API 回傳的連結沒有 https:
                        link = job.get('link', {}).get('job', '')
                        if link and not link.startswith('http'):
                            link = "https:" + link
                            
                        # 確保有抓到標題才加入列表
                        if title and company:
                            jobs_data.append({
                                '職缺名稱': title,
                                '公司名稱': company,
                                '職缺連結': link
                            })
                    time.sleep(1) # 停頓1秒避免被封鎖
                except Exception as e:
                    st.error(f"第 {page} 頁爬取失敗，可能是被 104 阻擋。錯誤細節: {e}")
                    break

            if jobs_data:
                # 轉成 DataFrame 並去除重複職缺
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
                    label="📥 點我下載 Excel 檔案",
                    data=excel_data,
                    file_name=f"104職缺_{keyword}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("還是沒有找到職缺！可能是 104 的防爬蟲機制阻擋了 Streamlit 雲端主機的 IP。
