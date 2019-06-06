import csv
import sys
import urllib3 as ulib
import pandas as pd
import datetime
from bs4 import BeautifulSoup as bs
ulib.disable_warnings()

try:
    #Create csv file only with column headers
    columnNames = ['CompanyName','Year','Ergebnis je Aktie (unverwaessert, nach Steuern)','Ergebnis je Aktie (verwaessert, nach Steuern)',
                   'Dividende je Aktie','Gesamtdividendenausschuettung in Mio.',
                   'Umsatz je Aktie','KGV (Jahresendkurs)','KGV (Jahresendkurs, EPS verwaessert)','Dividendenrendite Jahresende in %',
                  'Eigenkapitalquote in %', 'Fremdkapitalquote in %', 'Umsatzerloese', 'Umsatzveraenderung in %', 'Bruttoergebnis vom Umsatz', 'Bruttoergebnisveraenderung in %',
                  'Operatives Ergebnis', 'Veraenderung Operatives Ergebnis in %', 'Ergebnis vor Steuern', 'Veraenderung Ergebnis vor Steuern in %',
                  'Ergebnis nach Steuer', 'Veraenderung Ergebnis nach Steuer in %', 'Gesamtverbindlichkeiten', 'Langzeit Gesamtverbindlichk. pro Aktie',
                  'Eigenkapital', 'Veraenderung Eigenkapital in %', 'Bilanzsumme', 'Veraenderung Bilanzsumme in %', 'Gewinn je Aktie (unverwaessert, nach Steuern)',
                  'Veraenderung EPS (unverwässert) in %', 'Gewinn je Aktie (verwaessert, nach Steuern)', 'Veraenderung EPS (verwässert) in %', 'Dividende je Aktie',
                  'Veraenderung Dividende je Aktie in %', 'Anzahl Mitarbeiter', 'Veraenderung Anzahl Mitarbeiter in %']
    df = pd.DataFrame(columns=columnNames)
    csv_name = "FinanzenNet_" + datetime.datetime.now().isoformat().replace(":","_")[:19] + "_GuV-Data.csv"
    df.to_csv(csv_name, encoding='utf-8')
    f_csv = open(csv_name, 'a') # Open csv file in append mode
    
    #Read URLs from csv and store them in a list
    with open('SP_500_Finanznet_urls.csv', 'r') as f:
        reader = csv.reader(f)
        urls = list(reader) 
    
    #urls = ['https://www.finanzen.net/bilanz_guv/General_Mills','https://www.finanzen.net/bilanz_guv/Kellogg','https://www.finanzen.net/bilanz_guv/PepsiCo']
    
    #Loop opver all urls in list
    for url in urls[:]:
        print(url[0])
        
        #Open url and parse data
        http = ulib.PoolManager()
        response = http.request('GET', url[0])
        soup = bs(response.data,"lxml")
        
        #Initialize dataframes for each year
        df1 = pd.DataFrame(columns=columnNames,index=range(1))
        df2 = pd.DataFrame(columns=columnNames,index=range(1))
        df3 = pd.DataFrame(columns=columnNames,index=range(1))
        df4 = pd.DataFrame(columns=columnNames,index=range(1))
        df5 = pd.DataFrame(columns=columnNames,index=range(1))
        df6 = pd.DataFrame(columns=columnNames,index=range(1))
        df7 = pd.DataFrame(columns=columnNames,index=range(1))
        df_array = [df1,df2,df3,df4,df5,df6,df7]
        
        #Fill CompanyName and Year Column
        startyear = int(soup.find_all("table")[1].find_all("thead")[0].find_all("th")[2].contents[0])
        for i in range (7):
            df_array[i]['CompanyName'] = url[0].split('/')[4]            
            df_array[i]['Year'] = startyear+i
        
        #Find all tables in parsed url
        table = soup.find_all("table", { "class" : "table" })
        counter = 1
        
        #Loop over all tables
        for i, mytable in enumerate(table):
            if i != 0: #First table is irrelevant
                try:
                    rows = mytable.find_all('tr')
                    
                    #Loop over rows of table
                    for j, tr in enumerate(rows):
                        if j != 0: #First row is irrelevant (Headers)
                            cols = tr.find_all('td')
                            counter += 1
                            
                            #Loop over colummns in row
                            for k, td in enumerate(cols):
                                if k > 1: # first two columns (checkbox, Name) are irrelevant
                                    
                                    #Store data from each column in a different dataframe
                                    df_array[k-2][columnNames[counter]] = td.text
                                    
                except Exception as e:
                    print("Error in For-Loop")
                    print (e)
        
        #Loop over all dataframes and write them to csv file
        for i in range(7):
            df_array[i].to_csv(f_csv, header = False, encoding='utf-8',index=False)
        
        print("-scraped! Startyear: " + str(startyear))
        
    #Successfully scraped all urls
    f_csv.close()
    print("SUCCESS")
except KeyboardInterrupt:
    f_csv.close()
    print("Ausführung manuell beendet")
except Exception as e:
    print("Error occured")
    f_csv.close()
    type, value, traceback = sys.exc_info()
    print('Error opening %s: %s' % (value.filename, value.strerror))