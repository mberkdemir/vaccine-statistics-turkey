import requests
from datetime import datetime
import subprocess
import pandas as pd
from bs4 import BeautifulSoup

r = requests.get("https://covid19asi.saglik.gov.tr/")
soup = BeautifulSoup(r.content, features="html.parser")
vaccine_data = []
total_first_dose = 0
total_second_dose = 0

for data in soup.find_all(id='color1'):
    temp_dic = {
        "city": data.get('data-adi'),
        "total": data.get('data-toplam'),
        "first_dose": data.get('data-birinci-doz'),
        "second_dose": data.get('data-ikinci-doz')
    }
    total_first_dose += int(data.get('data-birinci-doz').replace(".", ""))
    total_second_dose += int(data.get('data-ikinci-doz').replace(".", ""))
    vaccine_data.append(temp_dic)
df = pd.DataFrame(vaccine_data)
df = df.rename(columns={"city": "Şehir", "total": "Toplam", "first_dose": "İlk Doz", "second_dose": "İkinci Doz"})
df.to_html('vaccinetable.html', index=False)

with open("vaccinetable.html") as inf:
    txt = inf.read()
    soup = BeautifulSoup(txt, features="html.parser")

meta = soup.new_tag('meta')
meta['content'] = "text/html; charset=UTF-8"
meta['http-equiv'] = "Content-Type"

p_datetime = soup.new_tag('p')
p_datetime.append(f"Bu tablo {datetime.now().strftime('%d.%m.%Y tarihinde saat %H.%M')}'de otomatik olarak oluşturuldu.")

p_total_firstdose = soup.new_tag('p')
p_total_firstdose.append("Toplam ilk doz aşı yaptıran sayısı: "+"{:,}".format(total_first_dose))

p_total_seconddose = soup.new_tag('p')
p_total_seconddose.append("Toplam ikinci doz aşı yaptıran sayısı: "+"{:,}".format(total_second_dose))

p_total_vaccinated = soup.new_tag('p')
p_total_vaccinated.append("Toplam aşılanan sayısı: "+"{:,}".format(total_first_dose+total_second_dose))

p_percentage_first = soup.new_tag('p')
p_percentage_first.append("Nüfusa göre oran (ilk doz): %"+"{:.2f}".format(((total_first_dose)*100)/83614512))

p_percentage_second = soup.new_tag('p')
p_percentage_second.append("Nüfusa göre oran (ikinci doz): %"+"{:.2f}".format(((total_second_dose)*100)/83614512))

soup.insert(0, meta)
soup.insert(1, p_datetime)
soup.insert(2, p_total_firstdose)
soup.insert(3, p_total_seconddose)
soup.insert(4, p_total_vaccinated)
soup.insert(5, p_percentage_first)
soup.insert(6, p_percentage_second)

with open("vaccinetable.html", "w") as outf:
    outf.write(str(soup))

subprocess.call('wkhtmltoimage --encoding utf-8 -f png --width 0 vaccinetable.html vaccinetable.png', shell=True)