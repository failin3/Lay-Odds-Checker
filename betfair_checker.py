from urllib import request
import json
import requests
from tkinter import*
import webbrowser

DATE_OF_MATCHES = "2020-02-12"
START_TIME = "00:00"
END_TIME = "23:59"

def getApiCredentials():
    with open("credentials.txt") as f:
        application_key = f.readline().strip()
        session_key = f.readline().strip()
        return application_key, session_key


def runnerIdToTitle(runner_id_list):
    for game in runner_id_list:
        selection_id = game[1]
        if selection_id == 1:
            game[1] = "0-0"
        if selection_id == 2:
            game[1] = "1-0"
        if selection_id == 3:
            game[1] = "1-1"
        if selection_id == 4:
            game[1] = "0-1"
        if selection_id == 5:
            game[1] = "2-0"
        if selection_id == 6:
            game[1] = "2-1"
        if selection_id == 7:
            game[1] = "2-2"
        if selection_id == 8:
            game[1] = "1-2"
        if selection_id == 9:
            game[1] = "0-2"
        if selection_id == 10:
            game[1] = "3-0"
        if selection_id == 11:
            game[1] = "3-1"
        if selection_id == 12:
            game[1] = "3-2"
        if selection_id == 13:
            game[1] = "3-3"
        if selection_id == 14:
            game[1] = "2-3"
        if selection_id == 15:
            game[1] = "1-3"
        if selection_id == 16:
            game[1] = "0-3"
        if selection_id == 9063254:
            game[1] = "H win"
        if selection_id == 9063255:
            game[1] = "A win"
        if selection_id == 9063256:
            game[1] = "Draw"
    return runner_id_list

def getMarkets(list_of_market_ids, url, header):
        css = '"' + '","'.join(list_of_market_ids) + '"'
        #Get amount of money in market
        #"1.168140579", "1.168611121"
        total_list = []
        json_req = '[{{"jsonrpc":"2.0","method":"SportsAPING/v1.0/listMarketBook","params":{{"marketIds":[{}],"priceProjection":{{"priceData":["EX_BEST_OFFERS"],"virtualise":"true"}}}},"id":1}}]'.format(css)
        response = requests.post(url, data=json_req, headers=header).json()
        counter = 0
        for game in response[0]["result"]:
            size_list = []
            market_id = game["marketId"]
            for runner in game["runners"]:
                try:
                    selectionId = runner["selectionId"]
                    available_to_lay = float((runner["ex"]["availableToLay"][0]["size"]))
                    price = float(runner["ex"]["availableToLay"][0]["price"])
                except IndexError:
                    available_to_lay = 0
                size_list.append([available_to_lay, selectionId, price])
            total_list.append([market_id, sorted(size_list, reverse=True)])
            counter += 1
        return total_list

def getBestMatches(date, application_key, session_key):
    url="https://api.betfair.com/exchange/betting/json-rpc/v1"
    header = { 'X-Application' : application_key, 'X-Authentication' : session_key ,'content-type' : 'application/json' }
    
    list_of_games = []
    list_of_market_ids = []


    #Get football events in date range
    json_req = '[{{"jsonrpc": "2.0","method": "SportsAPING/v1.0/listEvents","params": {{"filter": {{"eventTypeIds": ["1"],"marketStartTime": {{"from": "{}T{}:00Z","to": "{}T{}:00Z"}}}}}},"id": 1}}]'.format(date[0], date[1], date[0], date[2])
    response = requests.post(url, data=json_req, headers=header)
    games = response.json()

    for event in games[0]["result"]:
    #    print('{} - {}'.format(event["event"]["name"], event["event"]["id"]))
        list_of_games.append(event["event"]["id"])


    #Get correct score market ID for each game
    css = '"' + '","'.join(list_of_games) + '"'
    json_req = '[{{"jsonrpc":"2.0","method":"SportsAPING/v1.0/listMarketCatalogue","params":{{"filter":{{"textQuery":"CORRECT_SCORE","eventIds":[{}]}},"maxResults":"200"}},"id":1}}]'.format(css)
    response = requests.post(url, data=json_req, headers=header).json()

    for event in response[0]["result"]:
        list_of_market_ids.append(event["marketId"])

    if len(list_of_market_ids) > 40:
        total_list = []
        for i in range(0,100):
            total_list = total_list + getMarkets(list_of_market_ids[0+40*i:40+40*i], url, header)
            if(len(list_of_market_ids)-40*i < 40):
                break
        total_list = total_list + getMarkets(list_of_market_ids[40*i:], url, header)
    else:
        total_list = getMarkets(list_of_market_ids, url, header)

    #Find heighest per game
    final_list = []
    for game in total_list:
        game[1][0].append(game[0])
        final_list.append(game[1][0])
    final_list = sorted(final_list, reverse=True)
    final_list = runnerIdToTitle(final_list)
    return final_list

application_key, session_key = getApiCredentials()

final_list = getBestMatches([DATE_OF_MATCHES, START_TIME, END_TIME], application_key, session_key)

#Create GUI

def makeLambda(url):
    return lambda e: webbrowser.open_new(url)

def fixDate(date):
    year = date[:4]
    month = date[5:7]
    day = date[8:]
    return "{}/{}/{}".format(day, month, year)

def updateInfo(runner_labels, price_labels, size_labels, labels, date):
    #Destroy old labels
    for runner, price, size, label in zip(runner_labels, price_labels, size_labels, labels):
        runner.destroy()
        price.destroy()
        size.destroy()
        label.destroy()
    final_list = getBestMatches(date, application_key, session_key)
    labels = []
    counter = 0
    runner_labels = []
    price_labels = []
    size_labels = []

    starting_height = 0
    for game in final_list:
        runner_labels.append(Label(wn, text=game[1]))
        runner_labels[counter].place(x=0,y=starting_height+(20*counter))
        price_labels.append(Label(wn, text=game[2]))
        price_labels[counter].place(x=30,y=starting_height+(20*counter))
        size_labels.append(Label(wn, text="€" + str(round(game[0]))))
        size_labels[counter].place(x=60,y=starting_height+(20*counter))
        labels.append(Label(wn, text="link", fg="blue", cursor="hand2"))
        labels[counter].place(x=100,y=starting_height+(20*counter))
        url = "https://www.betfair.com/exchange/plus/football/market/" + game[3]
        labels[counter].bind("<Button-1>", makeLambda(url))    
        counter+=1
    

wn=Tk()
wn.geometry("300x300")

Label(wn, text="Date: ").place(x=150, y=0)
date_entry = Entry(wn, width=10)
date_entry.insert(0, DATE_OF_MATCHES)
date_entry.place(x=210,y=0)

Label(wn, text="End time: ").place(x=150, y=30)
time_entry = Entry(wn, width=5)
time_entry.insert(0, END_TIME)
time_entry.place(x=210, y=30)

update = Button(wn, text="Update", command=lambda: updateInfo(runner_labels, price_labels, size_labels, labels, [date_entry.get(), START_TIME, time_entry.get()]))
update.place(x=200, y=60)

labels = []
counter = 0
runner_labels = []
price_labels = []
size_labels = []

starting_height = 0
for game in final_list:
    runner_labels.append(Label(wn, text=game[1]))
    runner_labels[counter].place(x=0,y=starting_height+(20*counter))
    price_labels.append(Label(wn, text=game[2]))
    price_labels[counter].place(x=30,y=starting_height+(20*counter))
    size_labels.append(Label(wn, text="€" + str(round(game[0]))))
    size_labels[counter].place(x=60,y=starting_height+(20*counter))
    labels.append(Label(wn, text="link", fg="blue", cursor="hand2"))
    labels[counter].place(x=100,y=starting_height+(20*counter))
    url = "https://www.betfair.com/exchange/plus/football/market/" + game[3]
    labels[counter].bind("<Button-1>", makeLambda(url))    
    counter+=1
wn.mainloop()

