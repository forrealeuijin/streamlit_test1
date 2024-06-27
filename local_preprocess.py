import pandas as pd
import xlwings as xw

# 엑셀 파일 열기 및 데이터프레임으로 변환
file_path = 'C:/Users/shinsegaeDF/Downloads/4,5월 오프라인.xlsx'
book = xw.Book(file_path)
sheet = book.sheets[0]
df = sheet.used_range.options(pd.DataFrame, index=False).value

# CSV 파일로 저장
df.to_csv('processed_data.csv', index=False)
