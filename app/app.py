import PySimpleGUI as sg
from pymongo import MongoClient
from fpdf import FPDF
import pprint as pp
import re
import datetime
import pandas as pd
import certifi

# save FPDF() class into a variable pdf
pdf = FPDF()

timeTable = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
hourTable = []
for h in range(0, 24):
    hourTable.append(str(h))
minuteTable = []
for m in range(0, 60):
    minuteTable.append(str(m))

# Load list of authorized body names and types
df = pd.read_csv("../db/ab.csv", encoding='latin-1')
authorizedBodyIDs = df["_id"]
authorizedBodyNames = df.name
authorizedBodyTypes = df.type


def formatResult(s, removeIDdata):
    result = re.search('datetime.datetime\((.*)\)', s)
    while result is not None:
        parts = result.group(1).split(", ")
        date = parts[0] + "-" + parts[1] + "-" + parts[2] + " " + parts[3] + ":" + parts[4]
        s = s.replace(result.group(0), date)
        result = re.search('datetime.datetime\((.*)\)', s)

    s = s.replace("{", "")
    s = s.replace("}", "")
    s = s.replace("[", "")
    s = s.replace("]", "")
    s = s.replace("'", "")

    if removeIDdata:
        id_to_replace = re.search('_id: (.*),', s)
        s = s.replace(id_to_replace.group(0), "")
    else:
        s = s.replace("_id:", "")
    return s


# column where user can query manually
custom_query_column = [
    [
        sg.Text("Search for your certification:", font="16"),
    ],
    [
        sg.In(key='-CF-', size=(20, 1), default_text="RCCLSN63R22E126B"),
    ],
    [
        sg.Button(button_text="Get your certification", enable_events=True, key="-GET-CERTIFICATION-")
    ],
    [
        sg.Text(""),
        sg.Button(button_text="Download", disabled=True, enable_events=True, key="-DOWNLOAD-")
    ]
]

# column with predefined queries
pred_query_column = [
    [
        sg.OptionMenu(
            values=["People with SuperGreenPass", "Number of vaccinations", "Average age of unvaccinated people",
                    "Infected people", "No. of tests for authorized body"], size=(12, 1),
            expand_x=True,
            key="-QUERY-",
            default_value="Select a predefined query",
        ),
        sg.Button(button_text="Send Query", enable_events=True, key="-SEND-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20),
            key="-QUERY-LIST-",
            horizontal_scroll=True
        )
    ]
]

# column where user can use commands
commands_query_column = [
    [
        sg.Text("Create a new test:", font="16"),
    ],
    [
        sg.In(key='-TEST-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d')
    ],
    [
        sg.Text("Hour:", font="10"),
        sg.OptionMenu(
            values=hourTable, size=(6, 1), expand_x=True, key="-TEST-HOUR-",
            default_value="10"
        ),
        sg.Text("Minute:", font="10"),
        sg.OptionMenu(
            values=minuteTable, size=(6, 1), expand_x=True, key="-TEST-MINUTE-",
            default_value="30"
        ),
    ],
    [
        sg.Text("CF:", font="10"),
        sg.In(key='-TEST-CF-', size=(20, 1), default_text="RCCLSN63R22E126B"),
    ],
    [
        sg.OptionMenu(
            values=authorizedBodyNames, size=(12, 1), expand_x=True, key="-AUTHORIZED-BODY-",
            default_value=authorizedBodyNames[0]
        ),
    ],
    [
        sg.Checkbox("Positive", enable_events=True, key="-POSITIVE-"),
        sg.Checkbox("Negative", enable_events=True, key="-NEGATIVE-")
    ],
    [
        sg.Checkbox("Molecular", enable_events=True, key="-MOLECULAR-"),
        sg.Checkbox("Antigen", enable_events=True, key="-ANTIGEN-")
    ],
    [
        sg.Button(button_text="Create test",
                  enable_events=True,
                  key="-CREATE-TEST-",
                  expand_x=True)
    ]
]

# full layout
query_layout = [
    [
        sg.Column(custom_query_column),
        sg.VSeparator(),
        sg.Column(pred_query_column),
    ]
]

crud_layout = [
    [
        sg.Column(commands_query_column),
    ]
]

# Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(query_layout, key='-COLQueries-'), sg.Column(crud_layout, visible=False, key='-COLCommands-')],
          [sg.Button('Queries'), sg.Button('Commands'), sg.Button('Exit')]]

window = sg.Window("CertificationsManager 1.0", layout)
layout_page = "Queries"
ca = certifi.where()
# init database
# TO CHANGE DEPENDING ON YOUR DATABASE ADDRESS
client = MongoClient("mongodb+srv://root:smbud@smbud.icy9p.mongodb.net/test?retryWrites=true&w=majority", tlsCAFile=ca)
db = client.smbud_data
collection = db.certifications

# event loop
certification = None
cf = ""
while True:
    event, values = window.read()

    if event == "-POSITIVE-":
        if values["-POSITIVE-"]:
            window["-NEGATIVE-"].update(disabled=True)
        else:
            window["-NEGATIVE-"].update(disabled=False)

    if event == "-NEGATIVE-":
        if values["-NEGATIVE-"]:
            window["-POSITIVE-"].update(disabled=True)
        else:
            window["-POSITIVE-"].update(disabled=False)

    if event == "-MOLECULAR-":
        if values["-MOLECULAR-"]:
            window["-ANTIGEN-"].update(disabled=True)
        else:
            window["-ANTIGEN-"].update(disabled=False)

    if event == "-ANTIGEN-":
        if values["-ANTIGEN-"]:
            window["-MOLECULAR-"].update(disabled=True)
        else:
            window["-MOLECULAR-"].update(disabled=False)

    if event == "-CF-":
        if values["-CF-"] != "":
            window["-GET-CERTIFICATION-"].update(disabled=False)
        else:
            window["-GET-CERTIFICATION-"].update(disabled=True)

    if event == "-GET-CERTIFICATION-":
        cf = values["-CF-"]
        query = {
            "person.codice_fiscale": cf,
        }
        certification = collection.find_one(query)
        if certification is not None:
            window["-DOWNLOAD-"].update(disabled=False)

    if event == "-DOWNLOAD-":
        pdf.add_page()

        pdf.set_font("Arial", size=15)
        pdf.set_title("Your Certification")

        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, "Your Certification", ln=1, align='C')
        pdf.set_text_color(0, 0, 0)

        string = pp.pformat(certification)
        string = formatResult(string, True)

        pdf.multi_cell(200, 10, string)

        pdf.set_author("Polytechnic of Milan")
        # save the pdf with name .pdf
        pdf.output(cf + "_certification.pdf")
        pdf.close()
        pdf = FPDF()

    if event == "-SEND-QUERY-":
        pretty_data = []
        base_query = ""
        if values["-QUERY-"] == "People with SuperGreenPass":
            nine_month_ago = datetime.datetime.today() - datetime.timedelta(days=270)

            query1 = {
                "vaccination": {"$exists": True},
                "vaccination.datetime": {"$gte": nine_month_ago}
            }
            query2 = {
                "person.name": "$person.name",
                "person.surname": "$person.surname",
                "person.codice_fiscale": "$person.codice_fiscale"
            }
            data = collection.find(query1, query2)
            for person in data:
                string = pp.pformat(person)
                string = formatResult(string, True)
                pretty_data.append(string)
        if values["-QUERY-"] == "Number of vaccinations":
            query1 = {
                "$unwind": "$vaccination"
            }
            query2 = {"$group": {
                "_id": {"month": {"$month": "$vaccination.datetime"}, "year": {"$year": "$vaccination.datetime"}},
                "count": {"$sum": 1}
            }}
            query3 = {
                "$sort": {"count": -1}
            }
            pipeline = [query1, query2, query3]
            data = collection.aggregate(pipeline)
            for person in data:
                string = pp.pformat(person)
                string = formatResult(string, False)
                pretty_data.append(string)
        if values["-QUERY-"] == "Average age of unvaccinated people":
            query1 = {"$match": {
                "person.birthdate": {"$exists": True},
                "vaccine": {"$exists": False}
            }}
            query2 = {"$project": {"ageInMillis": {"$subtract": [datetime.datetime.today(), "$person.birthdate"]}}}
            query3 = {"$project": {"age": {"$divide": ["$ageInMillis", 31558464000]}}}
            query4 = {"$project": {"age": {"$subtract": ["$age", {"$mod": ["$age", 1]}]}}}
            query5 = {"$group": {"_id": True, "avgAge": {"$avg": "$age"}}}
            query6 = {"$project": {"avgAge": {"$round": ["$avgAge", 2]}}}
            pipeline = [query1, query2, query3, query4, query5, query6]
            data = collection.aggregate(pipeline)
            for person in data:
                string = pp.pformat(person)
                string = formatResult(string, True)
                pretty_data.append(string)
        if values["-QUERY-"] == "Infected people":
            query1 = {"$addFields": {"test": {"$reduce": {
                "input": "$test",
                "initialValue": {"datetime": datetime.datetime(2000, 1, 1)},
                "in": {"$cond": [{"$gte": ["$$this.datetime", "$$value.datetime"]}, "$$this", "$$value"]}}
            }}}
            query2 = {"$match": {"test.result": "Positive"}}
            query3 = {"$project": {
                "person.name": "$person.name",
                "person.surname": "$person.surname",
                "person.codice_fiscale": "$person.codice_fiscale",
            }}
            pipeline = [query1, query2, query3]
            data = collection.aggregate(pipeline)
            for person in data:
                string = pp.pformat(person)
                string = formatResult(string, True)
                pretty_data.append(string)
        if values["-QUERY-"] == "No. of tests for authorized body":
            query1 = {"$unwind": "$test"}
            query2 = {"$group": {
                "_id": "$test.id_authorized_body",
                "count": {"$sum": 1}
            }}
            query3 = {
                "$lookup": {
                    "from": "authorizedBodies",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "authorizedBodyInfo"
                }
            }
            query4 = {
                "$project": {"_id": 0, "count": 1
                             }
            }
            pipeline = [query1, query2, query3, query4]
            data = collection.aggregate(pipeline)
            i = 0
            for body in data:
                string = pp.pformat(body)
                string = formatResult(string, False)
                string = authorizedBodyNames[i] + " (" + authorizedBodyTypes[i] + ") " + string
                pretty_data.append(string)
                i = i + 1

        window["-QUERY-LIST-"].update(pretty_data)

    if event == "-CREATE-TEST-":
        authorizedBody = values["-AUTHORIZED-BODY-"]
        date = values["-TEST-DATE-"]
        hour = values["-TEST-HOUR-"]
        minute = values["-TEST-MINUTE-"]
        cf = values["-TEST-CF-"]
        result = ""
        test_type = ""
        if values["-POSITIVE-"]:
            result = "Positive"
        else:
            result = "Negative"
        if values["-MOLECULAR-"]:
            test_type = "Molecular"
        else:
            test_type = "Antigen"

        i = 0
        for name in authorizedBodyNames:
            if name == authorizedBody:
                break
            i = i + 1

        authorizedBodyID = authorizedBodyIDs[i]

        split_date = date.split("-")
        datetime = datetime.datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]),
                                     int(hour), int(minute))
        print(datetime)
        print(authorizedBodyID)

        query1 = {
            "person.codice_fiscale": cf
        }
        query2 = {
            "$push": {
                "test": {
                    "$each": [{
                        "datetime": datetime,
                        "id_authorized_body": authorizedBodyID,
                        "result": result,
                        "type": test_type
                    }]
                }
            }
        }

        data = collection.update_one(query1, query2)
        print(data)
        if data:
            sg.Popup('Successfully created!', keep_on_top=True)
        else:
            sg.Popup('Error! Entry not created!', keep_on_top=True)

    if event == "Queries" or event == "Commands":
        window[f'-COL{layout_page}-'].update(visible=False)
        if event == "Commands":
            layout_page = "Commands"
        else:
            layout_page = "Queries"
        window[f'-COL{layout_page}-'].update(visible=True)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
