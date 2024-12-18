# -*- coding: utf-8 -*-
"""2024_Final_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16QTmTi__nQPTHlD-Uf_dOCOQZxka_ynk
"""

!pip install selenium
!apt-get update
!apt-get install -y chromium-chromedriver
!pip install selenium
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
!pip install webdriver_manager

!pip install chromedriver_autoinstaller


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from webdriver_manager.chrome import ChromeDriverManager
import time
import chromedriver_autoinstaller

def initialize_driver():
    options = Options()  # ChromeOptions 인스턴스 생성
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    options.add_argument('user-agent=' + user_agent)  # 사용자 에이전트 설정
    options.add_argument("lang=ko_KR")  # 언어 설정
    options.add_argument('headless')  # Headless 모드 설정
    options.add_argument('window-size=1920x1080')  # 창 크기 설정
    options.add_argument("disable-gpu")  # GPU 비활성화
    options.add_argument("--no-sandbox")  # 권한 문제 방지

    # Chromedriver 초기화
    driver = webdriver.Chrome(options=options)
    return driver




# 멜론 차트 데이터를 수집하는 함수
def melon_collector(driver, url, year):
    time.sleep(5)  # 페이지 로드 대기
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 제목 가져오기
    title = driver.find_elements(by=By.CLASS_NAME, value='ellipsis.rank01')  # 제목
    title_list = [t.text for t in title][:50]  # Top 50만 추출

    # 가수 가져오기
    singer = driver.find_elements(by=By.CLASS_NAME, value='ellipsis.rank02')  # 가수
    singer_list = [s.text for s in singer][:50]  # Top 50만 추출

    # 곡 ID 가져오기
    song_info = soup.find_all('div', attrs={'class': 'ellipsis rank01'})
    song_ids = []

    for i in range(50):
        try:
            # 곡 ID 추출 후 앞 8자리 제거
            raw_song_id = re.sub(r'[^0-9]', '', song_info[i].find("a")["href"][4:])
            song_id = raw_song_id[8:]  # 앞 8자리 제거
            song_ids.append(song_id)
            print(f"곡 ID 추출 성공: {song_id}")  # 곡 ID 출력
        except Exception as e:
            song_ids.append('')
            print(f"곡 ID 추출 실패 at index {i}: {e}")  # 에러 출력
            continue

    # 가사 가져오기
    lyrics = []
    for song_id in song_ids:
        if not song_id:  # song_id가 비어있는 경우
            lyrics.append('')
            continue
        try:
            driver.get(f"https://www.melon.com/song/detail.htm?songId={song_id}")
            time.sleep(2)
            lyric = driver.find_element(by=By.CLASS_NAME, value="lyric")
            lyrics.append(lyric.text.replace("\n", " "))  # 줄바꿈을 공백으로
        except:
            lyrics.append('')  # 가사가 없는 경우
            continue

    # 데이터 프레임 생성
    df = pd.DataFrame({
        "제목": title_list,
        "가수": singer_list,
        "가사": lyrics,
        "연도": year
    })

    return df

# 연도별 데이터 크롤링
start_year = 1990
end_year = 2023
url_template = 'https://www.melon.com/chart/age/index.htm?chartType=YE&chartGenre=KPOP&chartDate='

melon_total = []  # 모든 연도의 데이터를 저장할 리스트

# WebDriver 초기화
driver = initialize_driver()

while start_year <= end_year:
    url = url_template + str(start_year)
    try:
        yearly_data = melon_collector(driver, url, start_year)
        melon_total.append(yearly_data)
        print(f"{start_year}년 데이터 수집 완료")
    except Exception as e:
        print(f"{start_year}년 데이터 수집 중 오류 발생: {e}")
    start_year += 1

# WebDriver 종료
driver.quit()

# 모든 데이터를 하나의 데이터프레임으로 병합
if melon_total:
    combined_data = pd.concat(melon_total, ignore_index=True)

    # Top10 여부 확인 컬럼 추가
    combined_data["Top10"] = combined_data.index % 50 < 10  # Top 10인지 여부 (True/False)

    # 최종 데이터 확인 및 저장
    combined_data.to_csv("통합_데이터.csv", index=False, encoding="utf-8-sig")
    print("모든 데이터 수집 및 저장 완료")
else:
    print("데이터가 수집되지 않았습니다.")

import pandas as pd

# CSV 파일 경로를 지정하세요.
file_path = '통합_데이터.csv'

# CSV 파일 읽기
data = pd.read_csv(file_path)

# 데이터 출력
print(data)

!pip install konlpy

import pandas as pd
from konlpy.tag import Komoran

# 수집된 데이터를 불러옵니다
# "sss.csv" 파일이 존재한다고 가정합니다.
data_path = "통합_데이터.csv"
melon_data = pd.read_csv(data_path, encoding="utf-8-sig")

# Top10 여부를 판단하여 'Top10' 컬럼 생성
melon_data["Top10"] = melon_data.groupby("연도").cumcount() < 10  # 각 연도별 Top 10 판단
melon_data["Top10"] = melon_data["Top10"].astype(int)  # True/False를 1/0으로 변환

# 연대별 데이터 분리
melon_1990s = melon_data[melon_data["연도"].between(1990, 1999)]
melon_2000s = melon_data[melon_data["연도"].between(2000, 2009)]
melon_2010s = melon_data[melon_data["연도"].between(2010, 2019)]
melon_2020s = melon_data[melon_data["연도"].between(2020, 2023)]

# 각 연대의 가사 데이터 추출
gasa_1990s = melon_1990s["가사"].dropna()
gasa_2000s = melon_2000s["가사"].dropna()
gasa_2010s = melon_2010s["가사"].dropna()
gasa_2020s = melon_2020s["가사"].dropna()

# Komoran을 사용하여 명사 추출
komoran = Komoran()

def extract_nouns(gasa_series):
    """가사 데이터에서 명사를 추출하여 리스트로 반환"""
    nouns = []
    for gasa in gasa_series:
        try:
            nouns.append(komoran.nouns(gasa))
        except:
            continue
    return nouns

# 연대별 명사 추출
noun_1990s = extract_nouns(gasa_1990s)
noun_2000s = extract_nouns(gasa_2000s)
noun_2010s = extract_nouns(gasa_2010s)
noun_2020s = extract_nouns(gasa_2020s)

# 연대별 데이터프레임으로 변환 (명사 리스트를 문자열로 저장)
df_1990s = pd.DataFrame({"연대": "1990s", "명사": [" ".join(n) for n in noun_1990s]})
df_2000s = pd.DataFrame({"연대": "2000s", "명사": [" ".join(n) for n in noun_2000s]})
df_2010s = pd.DataFrame({"연대": "2010s", "명사": [" ".join(n) for n in noun_2010s]})
df_2020s = pd.DataFrame({"연대": "2020s", "명사": [" ".join(n) for n in noun_2020s]})

# 모든 데이터를 하나로 합치기
final_data = pd.concat([df_1990s, df_2000s, df_2010s, df_2020s], ignore_index=True)

# CSV 파일로 저장
final_data.to_csv("명사_추출_데이터.csv", index=False, encoding="utf-8-sig")
print("명사 추출 완료 및 저장 완료!")

import pandas as pd

# CSV 파일 경로를 지정하세요.
file_path = '명사_추출_데이터.csv'

# CSV 파일 읽기
data = pd.read_csv(file_path)

# 데이터 출력
print(data)

# 불용어 파일 로드
stopword_path = "stopword.txt"  # 불용어가 저장된 파일 경로
with open(stopword_path, 'r', encoding='utf-8') as f:
    stopwords = f.read().split()  # 불용어를 리스트로 변환

# 불용어 처리된 명사를 저장할 리스트 초기화
noun_1990s_sw = []
noun_2000s_sw = []
noun_2010s_sw = []
noun_2020s_sw = []

# 불용어 처리 함수
def remove_stopwords(noun_list, stopwords):
    """명사 리스트에서 불용어를 제거"""
    result = []
    for text in noun_list:  # 명사 리스트에서 각 텍스트를 순회
        temp = [word for word in text if word not in stopwords]  # 불용어 제거
        result.append(temp)
    return result

# 연대별 불용어 처리
noun_1990s_sw = remove_stopwords(noun_1990s, stopwords)
noun_2000s_sw = remove_stopwords(noun_2000s, stopwords)
noun_2010s_sw = remove_stopwords(noun_2010s, stopwords)
noun_2020s_sw = remove_stopwords(noun_2020s, stopwords)

# 처리 결과 확인 (필요 시)
print("1990s 처리 완료:", noun_1990s_sw[:5])  # 일부만 출력
print("2000s 처리 완료:", noun_2000s_sw[:5])
print("2010s 처리 완료:", noun_2010s_sw[:5])
print("2020s 처리 완료:", noun_2020s_sw[:5])

# 불용어 제거된 데이터를 데이터프레임으로 변환 (선택적으로 저장 가능)
df_1990s_sw = pd.DataFrame({"연대": "1990s", "명사": [" ".join(n) for n in noun_1990s_sw]})
df_2000s_sw = pd.DataFrame({"연대": "2000s", "명사": [" ".join(n) for n in noun_2000s_sw]})
df_2010s_sw = pd.DataFrame({"연대": "2010s", "명사": [" ".join(n) for n in noun_2010s_sw]})
df_2020s_sw = pd.DataFrame({"연대": "2020s", "명사": [" ".join(n) for n in noun_2020s_sw]})

# 불용어 제거 후 데이터 병합
final_data_sw = pd.concat([df_1990s_sw, df_2000s_sw, df_2010s_sw, df_2020s_sw], ignore_index=True)

# CSV 파일로 저장
final_data_sw.to_csv("불용어_처리_데이터.csv", index=False, encoding="utf-8-sig")
print("불용어 처리 완료 및 저장 완료!")

from collections import Counter
import pandas as pd

# 연대별 빈도수를 저장할 리스트 초기화
mostwords_1990s = []
mostwords_2000s = []
mostwords_2010s = []
mostwords_2020s = []

# 연대별 명사 리스트(nouns)에서 가장 많이 등장한 Top 10 단어와 빈도수 추출
def extract_top_words(noun_list, top_n=10):
    """명사 리스트에서 Top N 단어와 빈도수를 추출"""
    result = []
    for document in noun_list:
        counter = Counter(document)
        result.append(counter.most_common(top_n))
    return result

# 연대별 Top 10 단어 추출
mostwords_1990s = extract_top_words(noun_1990s_sw, top_n=10)
mostwords_2000s = extract_top_words(noun_2000s_sw, top_n=10)
mostwords_2010s = extract_top_words(noun_2010s_sw, top_n=10)
mostwords_2020s = extract_top_words(noun_2020s_sw, top_n=10)

# DataFrame 형태로 변환 및 컬럼 이름 변경
def convert_to_dataframe(mostwords, decade_label):
    """빈도 데이터 리스트를 데이터프레임으로 변환"""
    df = pd.DataFrame(mostwords).fillna(0)  # 결측값을 0으로 채움
    df.columns = df.columns.map(lambda x: f"{decade_label}_빈도_{x + 1}")  # 컬럼명 설정
    return df

# 연대별 데이터프레임 생성
df_mostwords_1990s = convert_to_dataframe(mostwords_1990s, "1990s")
df_mostwords_2000s = convert_to_dataframe(mostwords_2000s, "2000s")
df_mostwords_2010s = convert_to_dataframe(mostwords_2010s, "2010s")
df_mostwords_2020s = convert_to_dataframe(mostwords_2020s, "2020s")

# 최종적으로 병합된 데이터 저장
final_mostwords_df = pd.concat([df_mostwords_1990s, df_mostwords_2000s, df_mostwords_2010s, df_mostwords_2020s], axis=1)

# 결과를 CSV 파일로 저장
final_mostwords_df.to_csv("연대별_단어_빈도분석.csv", index=False, encoding="utf-8-sig")
print("빈도 분석 완료 및 저장 완료!")

# 단계 1: 폰트 설치
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

!apt-get -qq -y install fonts-nanum > /dev/null
#fontpath = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'

#font = fm.FontProperties(fname=fontpath, size=9)

#fm._rebuild()



fe = fm.FontEntry(
    fname=r'/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf', # ttf 파일이 저장되어 있는 경로
    name='NanumGothic')                        # 이 폰트의 원하는 이름 설정
fm.fontManager.ttflist.insert(0, fe)              # Matplotlib에 폰트 추가
plt.rcParams.update({'font.size': 18, 'font.family': 'NanumGothic'}) # 폰트 설

# 단계 2: 런타임 재시작
import os
os.kill(os.getpid(), 9)

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# apt-get update
# apt-get install g++ openjdk-8-jdk python-dev python3-dev
# pip3 install JPype1
# pip3 install konlpy

# Commented out IPython magic to ensure Python compatibility.
# %env JAVA_HOME "/usr/lib/jvm/java-8-openjdk-amd64"

# 단계 3: 한글 폰트 설정
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm

# 마이너스 표시 문제
mpl.rcParams['axes.unicode_minus'] = False

# 한글 폰트 설정
fe = fm.FontEntry(
    fname=r'/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf', # ttf 파일이 저장되어 있는 경로
    name='NanumGothic')                        # 이 폰트의 원하는 이름 설정
fm.fontManager.ttflist.insert(0, fe)              # Matplotlib에 폰트 추가
plt.rcParams.update({'font.size': 18, 'font.family': 'NanumGothic'}) # 폰트 설

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from ast import literal_eval

# 데이터 로드
file_path = '/content/불용어_처리_데이터.csv'
data = pd.read_csv(file_path)

# 데이터 변환 함수
def convert_column_to_dict(data, columns_prefix):
    """주어진 연대별 열에서 단어와 빈도를 추출하여 딕셔너리로 변환"""
    freq_dict = {}
    for col in data.columns:
        if columns_prefix in col:  # 특정 연대의 열만 처리
            for item in data[col].dropna():
                try:
                    word, count = literal_eval(item)  # 문자열을 튜플로 변환
                    freq_dict[word] = freq_dict.get(word, 0) + count  # 빈도 합산
                except Exception as e:
                    continue
    return freq_dict

# 연대별 데이터 추출
freq_1990s = convert_column_to_dict(data, "1990s")
freq_2000s = convert_column_to_dict(data, "2000s")
freq_2010s = convert_column_to_dict(data, "2010s")
freq_2020s = convert_column_to_dict(data, "2020s")

# 워드클라우드 생성 및 저장 함수
def plot_and_save_wordcloud(freq, title, file_name):
    wordcloud = WordCloud(
        background_color="white",
        font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        width=800,
        height=400
    ).generate_from_frequencies(freq)

    # 워드클라우드 저장
    wordcloud.to_file(file_name)
    print(f"{title} 워드클라우드가 {file_name}에 저장되었습니다.")

    # 워드클라우드 시각화
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=16)

# 워드클라우드 시각화 및 저장 실행
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plot_and_save_wordcloud(freq_1990s, "1990년대", "wordcloud_1990s.png")

plt.subplot(2, 2, 2)
plot_and_save_wordcloud(freq_2000s, "2000년대", "wordcloud_2000s.png")

plt.subplot(2, 2, 3)
plot_and_save_wordcloud(freq_2010s, "2010년대", "wordcloud_2010s.png")

plt.subplot(2, 2, 4)
plot_and_save_wordcloud(freq_2020s, "2020년대", "wordcloud_2020s.png")

plt.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 데이터 로드
file_path = '/content/frequency.csv'
data = pd.read_csv(file_path)

# 데이터 전처리 함수
def process_column(column):
    return column.str.extract(r"\('([^']*)',\s*(\d+)\)").dropna()

# 특정 연대의 상위 단어 추출 및 시각화 함수
def visualize_decade_words(decade, ax):
    columns = [col for col in data.columns if decade in col]
    processed_data = pd.concat([
        process_column(data[col]).rename(columns={0: 'word', 1: 'frequency'})
        for col in columns
    ])
    processed_data['frequency'] = processed_data['frequency'].astype(int)
    word_frequencies = processed_data.groupby('word')['frequency'].sum().reset_index()
    top_words = word_frequencies.nlargest(10, 'frequency')

    # 그래프 생성
    ax.bar(top_words['word'], top_words['frequency'], color='skyblue')
    ax.set_title(f"{decade} 상위 10개 단어", fontsize=14)
    ax.set_xlabel("단어", fontsize=10)
    ax.set_ylabel("빈도", fontsize=10)
    ax.tick_params(axis='x', rotation=45)

# 4개의 막대 그래프를 생성
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
decades = ['1990s', '2000s', '2010s', '2020s']

for ax, decade in zip(axes.flat, decades):
    visualize_decade_words(decade, ax)

# 레이아웃 조정
plt.tight_layout()

# 그래프를 파일로 저장
plt.savefig("decade_word_frequencies.png", dpi=300, bbox_inches='tight')  # 그래프 저장
plt.show()

# Colab 환경에서 파일 읽기
import pandas as pd
import matplotlib.pyplot as plt
from ast import literal_eval

# CSV 파일 읽기
file_path = '/content/frequency.csv'
data = pd.read_csv(file_path)

# 데이터 변환 함수
def convert_column_to_dict(data, columns_prefix):
    """주어진 연대별 열에서 단어와 빈도를 추출하여 딕셔너리로 변환"""
    freq_dict = {}
    for col in data.columns:
        if columns_prefix in col:  # 특정 연대의 열만 처리
            for item in data[col].dropna():
                try:
                    word, count = literal_eval(item)  # 문자열을 튜플로 변환
                    freq_dict[word] = freq_dict.get(word, 0) + count  # 빈도 합산
                except Exception:
                    continue
    return freq_dict

# 연대별 데이터 추출
freq_1990s = convert_column_to_dict(data, "1990s")
freq_2000s = convert_column_to_dict(data, "2000s")
freq_2010s = convert_column_to_dict(data, "2010s")
freq_2020s = convert_column_to_dict(data, "2020s")

# 데이터프레임 생성 (시각화를 위해 정리)
freq_df = pd.DataFrame({
    "1990s": pd.Series(freq_1990s),
    "2000s": pd.Series(freq_2000s),
    "2010s": pd.Series(freq_2010s),
    "2020s": pd.Series(freq_2020s)
}).fillna(0).astype(int)

# 상위 10개 단어만 선택
top_words = freq_df.sum(axis=1).sort_values(ascending=False).head(10).index
freq_top_df = freq_df.loc[top_words]

# 막대그래프 시각화
freq_top_df.plot(kind="bar", figsize=(12, 6))
plt.title("연대별 단어 빈도 비교 (상위 10개 단어)", fontsize=16)
plt.ylabel("빈도", fontsize=12)
plt.xlabel("단어", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="연대")
plt.tight_layout()

# 그래프 저장
plt.savefig("frequency.png", dpi=300, bbox_inches='tight')  # 그래프 저장
plt.show()

import matplotlib.pyplot as plt

# 연대별 상위 N개 단어 추출 함수
def get_top_n_words(freq_dict, n=5):
    sorted_items = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_items[:n])

# 연대별 상위 N개 단어 추출
top_n = 5  # 상위 N개 단어
top_1990s = get_top_n_words(freq_1990s, n=top_n)
top_2000s = get_top_n_words(freq_2000s, n=top_n)
top_2010s = get_top_n_words(freq_2010s, n=top_n)
top_2020s = get_top_n_words(freq_2020s, n=top_n)

# 파이 차트 시각화 함수
def visualize_pie_chart(data, title, ax):
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=140)
    ax.set_title(title, fontsize=14)

# 파이 차트 그리기
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
visualize_pie_chart(top_1990s, "1990s 상위 단어", axes[0, 0])
visualize_pie_chart(top_2000s, "2000s 상위 단어", axes[0, 1])
visualize_pie_chart(top_2010s, "2010s 상위 단어", axes[1, 0])
visualize_pie_chart(top_2020s, "2020s 상위 단어", axes[1, 1])

plt.tight_layout()

# 전체 차트를 파일로 저장
plt.savefig("decade_top_words_pie_chart.png", dpi=300, bbox_inches='tight')  # 파일 저장
plt.show()

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
from ast import literal_eval
import numpy as np

# 데이터 로드
data_path = '/content/frequency.csv'
data = pd.read_csv(data_path)

# 특정 열에서 단어와 빈도를 추출하여 딕셔너리로 변환하는 함수
def extract_word_frequencies(data, decade_prefix):
    freq_dict = {}
    for col in data.columns:
        if col.startswith(decade_prefix):
            for item in data[col].dropna():
                try:
                    word, count = literal_eval(item)  # 문자열을 튜플로 변환
                    freq_dict[word] = freq_dict.get(word, 0) + count  # 빈도 합산
                except Exception:
                    continue
    return freq_dict

# 연대별 데이터 추출
freq_1990s = extract_word_frequencies(data, "1990s")
freq_2000s = extract_word_frequencies(data, "2000s")
freq_2010s = extract_word_frequencies(data, "2010s")
freq_2020s = extract_word_frequencies(data, "2020s")

# 데이터프레임으로 변환
freq_data = pd.DataFrame({
    "1990s": pd.Series(freq_1990s),
    "2000s": pd.Series(freq_2000s),
    "2010s": pd.Series(freq_2010s),
    "2020s": pd.Series(freq_2020s)
}).fillna(0).astype(int)

# 라벨 생성: 각 연대별 상위 10개의 단어를 라벨 1로 설정
for col in freq_data.columns:
    freq_data[f"{col}_label"] = 0
    top_10_indices = freq_data[col].nlargest(10).index
    freq_data.loc[top_10_indices, f"{col}_label"] = 1

# 특성과 라벨 준비
feature_columns = ["1990s", "2000s", "2010s", "2020s"]
label_columns = ["1990s_label", "2000s_label", "2010s_label", "2020s_label"]

# 학습 데이터와 테스트 데이터 준비
X_train = freq_data[["1990s", "2000s", "2010s"]].values
y_train = freq_data[["1990s_label", "2000s_label", "2010s_label"]].max(axis=1).values

X_test = freq_data[["2020s", "2020s", "2020s"]].values  # 테스트 데이터를 학습 데이터와 동일하게 확장
y_test = freq_data["2020s_label"].values

# 랜덤 포레스트 모델 학습
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

# 테스트 데이터에 대한 예측
y_pred = rf_model.predict(X_test)

# 성능 평가
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

print(f"정확도(Accuracy): {accuracy}")
print(f"분류 리포트(Classification Report):\n{classification_rep}")

# 시각화: 실제 라벨 vs 예측 라벨
labels = ["Not Top10", "Top10"]
y_test_counts = np.bincount(y_test, minlength=2)
y_pred_counts = np.bincount(y_pred, minlength=2)

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(x - width/2, y_test_counts, width, label='실제 값', alpha=0.7)
ax.bar(x + width/2, y_pred_counts, width, label='예측 값', alpha=0.7)

ax.set_ylabel('개수')
ax.set_title('실제 값과 예측 값 비교')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# 라벨 준비
# 예시용 가상의 라벨 데이터 생성
# 실제 데이터에서는 적절한 라벨 컬럼을 사용해야 합니다.
y_train = np.random.choice([0, 1], size=len(X_train))  # 1990s, 2000s, 2010s 라벨
y_test = np.random.choice([0, 1], size=len(X_test))    # 2020s 라벨

# 랜덤 포레스트 모델 학습
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

# 테스트 데이터 예측
y_pred = rf_model.predict(X_test)

# 성능 평가
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

# 결과 출력
print(f"정확도(Accuracy): {accuracy}")
print(f"분류 리포트(Classification Report):\n{classification_rep}")

# 실제 vs 예측 라벨 시각화
import matplotlib.pyplot as plt

labels = ["Not Top10", "Top10"]
y_test_counts = np.bincount(y_test, minlength=2)
y_pred_counts = np.bincount(y_pred, minlength=2)

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(x - width/2, y_test_counts, width, label='실제 값', alpha=0.7)
ax.bar(x + width/2, y_pred_counts, width, label='예측 값', alpha=0.7)

ax.set_ylabel('개수')
ax.set_title('실제 값과 예측 값 비교')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score
import numpy as np

# StratifiedKFold 설정
skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=2020)

# 학습 및 테스트 데이터 분리
X_train2, X_dev, y_train2, y_dev = train_test_split(
    X_train, y_train, test_size=0.3, random_state=2020, shuffle=True, stratify=y_train
)

# 모델 정의
models = {
    "RandomForest": RandomForestClassifier(random_state=2020),
    "LogisticRegression": LogisticRegression(random_state=2020, n_jobs=-1),
    "KNN": KNeighborsClassifier(n_jobs=-1),
    "ExtraTrees": ExtraTreesClassifier(random_state=2020, n_jobs=-1),
}

# 모델 학습 및 교차 검증
results = {}

print("#### 모델들의 ROC-AUC 교차 검증 결과 ####")
for model_name, model in models.items():
    # 교차 검증
    cv_scores = cross_val_score(model, X_dev, y_dev, cv=skf, scoring="roc_auc")
    results[model_name] = {
        "scores": cv_scores,
        "mean_score": np.mean(cv_scores),
    }
    # 결과 출력
    print(f"{model_name} : {cv_scores}")
    print(f"{model_name} 평균 : {np.mean(cv_scores)}")

# 최종 결과 저장
results