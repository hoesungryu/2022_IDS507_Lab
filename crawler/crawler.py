# -*- coding: utf-8 -*-
import os 
import pandas as pd
from datetime import datetime
from pprint import pprint
from tqdm.notebook import tqdm

import requests
from bs4 import BeautifulSoup



# user-defined functions
def get_news(n_url):
    news_detail = []

    breq = requests.get(n_url, headers={'User-Agent':'Mozilla/5.0'})
    bsoup = BeautifulSoup(breq.content, 'lxml')

    title = bsoup.select('h3#articleTitle')[0].text 
    news_detail.append(title)

    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
    _text = _text.replace("    동영상 뉴스   ", "")
    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
    
    news_detail.append(btext.strip())
    news_detail.append(n_url)
    pcompany = bsoup.select('#footer address')[0].a.get_text()
    news_detail.append(pcompany)

    return news_detail

def crawler(maxpage, query, s_date, e_date):

    crawled_data = {}
    years = []
    company = []
    title = []
    contents = []
    link = []
    
    s_from = s_date.replace(".","")
    e_to = e_date.replace(".","")


    maxpage_t =(int(maxpage)-1)*10+1   # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지
    os.makedirs("./save_txt", exist_ok=True)
    f = open(f"./save_txt/contents_text_{query}.txt", 'w', encoding='utf-8-sig')
    
    page_cnt = 0
    for page in tqdm(range(1, maxpage_t+1, 10)):
        page_cnt+=1
        print(f"page{page_cnt}/{maxpage}")
        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=0&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)
        
        req = requests.get(url,
                          headers={'User-Agent':'Mozilla/5.0'})
#         print(url)
#         print(page )
        cont = req.content
        soup = BeautifulSoup(cont, 'lxml')
        
        for urls in soup.find_all("a", class_="info"):
            try :
                if urls.get_text() == "네이버뉴스":

                    news_detail = get_news(urls["href"])
                    f.write("{}\t{}\t{}\t{}\t{}\n".format(news_detail[1], news_detail[4], news_detail[0], news_detail[2],news_detail[3]))  # new style
                    years.append(news_detail[1])
                    company.append(news_detail[4])
                    title.append(news_detail[0])
                    print(news_detail[0])
                    contents.append(news_detail[2])
                    link.append(news_detail[3])
                    
            except Exception as e:
                # print(e)
                continue
        
    crawled_data["years"] = years
    crawled_data["company"] = company
    crawled_data["title"] = title
    crawled_data["contents"] = contents
    crawled_data["link"] = link
    f.close()
    return crawled_data

def excel_make(crawled_data, file_name, RESULT_PATH):
    today = datetime.now().strftime("%Y%m%d_%H%M%S") # 현재시간
    data = pd.DataFrame(crawled_data)
    
    xlsx_outputFileName = f'[{today}]{file_name}.xlsx'
    save_path = RESULT_PATH+xlsx_outputFileName
    data.to_excel(save_path, encoding='utf-8-sig',index=False)
    return save_path