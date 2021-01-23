import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import time
from flask import Flask, jsonify, render_template
import json
app = Flask(__name__)

with open('mapdata.json') as f:
    #print(f)
    x = json.load(f)
with open('mapabbr.json') as f:
    mapabbrv = json.load(f)
#print(mapabbrv['United States'])
URL = 'https://www.worldometers.info/coronavirus/'
page = requests.get(URL)
print(page)
soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find_all("table")
countryTable = results[0]
body = countryTable.find_all("tr")
headings = ['Country', 'Total Cases', 'Deaths', 'Population']
body_rows = body[9:]
all_rows = [] # will be a list for list for all rows
counter = 0
for row_num in range(len(body_rows)): # A row at a time
    row = [] # this will hold entries for one row
    counter = 0
    for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
        # row_item.text removes the tags from the entries
        # the following regex is to remove \xa0 and \n and comma from row_item.text
        # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
        aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
        #append aa to row - note one row entry is being appended
        if (counter != 7 and counter !=0 and 28%counter == 0):
            row.append(aa)
        counter += 1
    # append one row to all_rows
    all_rows.append(row)

df = pd.DataFrame(data=all_rows, columns=headings)
df = df.to_dict()
print(df["Country"][0] + df["Population"][0])


@app.route('/')
def hello_world():
    #simplemaps_worldmap_mapdata.state_specific.AF.description = 1000
    #change js

    for i in range(215):
        if i == 185 or i == 194 or i == 214:
            continue
        deaths = ""
        if i<190:
            deaths = int(df["Deaths"][i])
        per_capita = int(df["Population"][i])/int(df["Total Cases"][i])
        cases = int(df["Total Cases"][i])
        red  = 255
        green = 229
        blue = 204
        if per_capita<=2000:
            red = 255
            green = 178
            blue  = 102
        if per_capita<=500:
            green = 128
            blue =  0
        if per_capita<=200:
            red = 240
            green = 120
            blue = 0
        if per_capita <=100:
            red = 240
            green = 0
        if per_capita <=50:
            red = 180
            green = 30
            blue = 30
        if per_capita <=20:
            red = 120
            green = 0
            blue = 0


        #color = ((-1276400/(per_capita+1696.57)) + 896.637)
        #color = color/(255)
        #red = min(1, color)*255
        #green = max(color-1, 0)*255
        #blue = max(color-2, 0)*255
        country_name = df["Country"][i]
        if country_name == "Gibraltar" or country_name == "Channel Islands" or country_name == "San Marino" or country_name == 'Monaco' or country_name == "Isle of Man" \
                or country_name == "Caribbean Netherlands" or country_name == "BL" or country_name == "Macao" or country_name == 'Vatican City' or country_name == 'Saint Pierre Miquelon':
            continue
        x['state_specific'][mapabbrv[country_name]]['color'] = f"rgb({red},{green}, {blue})"
        x['state_specific'][mapabbrv[country_name]]['hover_color'] = f"rgb({red},{green}, {blue})"
        x['state_specific'][mapabbrv[country_name]]['description'] = f"1 in {round(per_capita)} | Total cases: {cases} | Total Deaths: {deaths}"


    return render_template("home.html",data=x)

if __name__ == "__main__":
    app.run(debug=True)
