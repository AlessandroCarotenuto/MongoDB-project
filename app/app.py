import PySimpleGUI as sg
from pymongo import MongoClient
from fpdf import FPDF
import pprint as pp
import re
import datetime

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


def substituteDates(s):
    result = re.search('datetime.datetime\((.*)\)', s)
    while result != None:
        parts = result.group(1).split(", ")
        date = parts[0] + "-" + parts[1] + "-" + parts[2] + " " + parts[3] + ":" + parts[4]
        s = s.replace(result.group(0), date)
        result = re.search('datetime.datetime\((.*)\)', s)
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
                    "Vaccinated in last month", "People without Greenpass"], size=(12, 1),
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
        sg.Text("Create a new meeting:", font="16"),
    ],
    [
        sg.In(key='-MEETING-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d')
    ],
    [
        sg.Text("Hour:", font="10"),
        sg.OptionMenu(
            values=hourTable, size=(6, 1), expand_x=True, key="-MEETING-HOUR-",
            default_value="10"
        ),
        sg.Text("Minute:", font="10"),
        sg.OptionMenu(
            values=minuteTable, size=(6, 1), expand_x=True, key="-MEETING-MINUTE-",
            default_value="30"
        ),
    ],
    [
        sg.Text("First person CF:", font="10"),
        sg.In(key='-FIRST-PERSON-', size=(20, 1), default_text="DGSMRC50A10F205I"),
    ],
    [
        sg.Text("Second person CF:", font="10"),
        sg.In(key='-SECOND-PERSON-', size=(20, 1), default_text="SNNFRC32E03F205E"),
    ],
    [
        sg.Button(button_text="Create meeting",
                  enable_events=True,
                  key="-CREATE-MEETING-",
                  expand_x=True)
    ],
    [
        sg.HorizontalSeparator()
    ],
    [
        sg.Text("Create a new visit:", font="16"),
    ],
    [
        sg.In(key='-VISIT-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d'),
    ],
    [
        sg.Text("Hour in:", font="10"),
        sg.OptionMenu(
            values=hourTable, size=(6, 1), expand_x=True, key="-VISIT-HOUR-IN",
            default_value="10"
        ),
        sg.Text("Minute in:", font="10"),
        sg.OptionMenu(
            values=minuteTable, size=(6, 1), expand_x=True, key="-VISIT-MINUTE-IN",
            default_value="30"
        ),
        sg.VerticalSeparator(),
        sg.Text("Hour out:", font="10"),
        sg.OptionMenu(
            values=hourTable, size=(6, 1), expand_x=True, key="-VISIT-HOUR-OUT",
            default_value="11"
        ),
        sg.Text("Minute out:", font="10"),
        sg.OptionMenu(
            values=minuteTable, size=(6, 1), expand_x=True, key="-VISIT-MINUTE-OUT",
            default_value="30"
        )
    ],
    [
        sg.Text("Visitor person CF:", font="10"),
        sg.In(key='-VISITOR-', size=(20, 1), default_text="DGSMRC50A10F205I"),
        sg.Text("Select the place:", font="10")
    ],
    [
        sg.Button(button_text="Create visit",
                  enable_events=True,
                  key="-CREATE-VISIT-",
                  expand_x=True)
    ],
    [
        sg.HorizontalSeparator()
    ],
    [
        sg.Text("Flush all public place visits older than 1 year", font="10"),
        sg.Button(button_text="Delete",
                  enable_events=True,
                  key="-FLUSH-",
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
# init database
client = MongoClient("mongodb+srv://root:smbud@cluster0.xgxor.mongodb.net/test?retryWrites=true&w=majority")
db = client.admin
collection = db.certifications
# nine_month_ago = datetime.datetime.today() - datetime.timedelta(days=270)
#
# query1 = {
#   "vaccination":{"$exists": True},
#   "vaccination.datetime":{"$gte": nine_month_ago}
# }
# query2 = {
#   "vaccination.datetime":1
# }
#
# for person in collection.find(query1, query2):
#     print(person)

# event loop
certification = None
cf = ""
while True:
    event, values = window.read()

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
        string = string.replace("{", "")
        string = string.replace("}", "")
        string = string.replace("[", "")
        string = string.replace("]", "")
        string = string.replace("'", "")
        string = substituteDates(string)

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
                "vaccination.datetime": 1
            }
            certification = collection.find(query1, query2)
            for person in certification:
                string = pp.pformat(certification)
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
            certification = collection.aggregate(query1, query2, query3)
            for person in certification:
                string = pp.pformat(certification)
                pretty_data.append(string)
        if values["-QUERY-"] == "Average age of unvaccinated people":
            query1 = {"$match": {
                "person.birthdate": {"$exists": True},
                "vaccine": {"$exists": False}
            }}
            query2 = {"$project": {"ageInMillis": {"$subtract": ["new Date()", "$person.birthdate"]}}}
            query3 = {"$project": {"age": {"$divide": ["$ageInMillis", 31558464000]}}}
            #DA CAPIRE ORA
        if values["-QUERY-"] == "Vaccinated in last month":
            query = ""
            # data = graph.run(query).data()
            # pretty_data = pretty_people(data, "n")
        if values["-QUERY-"] == "People without Greenpass":
            query = ""
            # data = graph.run(query).data()
            # pretty_data = pretty_people(data, "noTest")

        window["-QUERY-LIST-"].update(pretty_data)

    if event == "-CREATE-MEETING-":
        date = values["-MEETING-DATE-"]
        hour = values["-MEETING-HOUR-"]
        minute = values["-MEETING-MINUTE-"]
        cf1 = values["-FIRST-PERSON-"]
        cf2 = values["-SECOND-PERSON-"]
        datetime = date + "T" + hour + ":" + minute + ":00"
        query = ""
        # data = graph.run(query).data()
        # if data:
        #     sg.Popup('Successfully created!', keep_on_top=True)
        # else:
        #     sg.Popup('Error! Entry not created!', keep_on_top=True)

    if event == "-CREATE-VISIT-":
        date = values["-VISIT-DATE-"]
        hour_in = values["-VISIT-HOUR-IN"]
        minute_in = values["-VISIT-MINUTE-IN"]
        hour_out = values["-VISIT-HOUR-OUT"]
        minute_out = values["-VISIT-MINUTE-OUT"]
        place = values["-VISITED-PLACE-"]
        cf = values["-VISITOR-"]
        datetime_in = date + "T" + hour_in + ":" + minute_in + ":00"
        datetime_out = date + "T" + hour_out + ":" + minute_out + ":00"
        query = ""
        # data = graph.run(query).data()
        # if data:
        #     sg.Popup('Successfully created!', keep_on_top=True)
        # else:
        #     sg.Popup('Error! Entry not created!', keep_on_top=True)

    if event == "-FLUSH-":
        query1 = ""
        query2 = ""
        # graph.run(query1)
        # data = graph.run(query2).data()
        # if not data:
        #     sg.Popup('Successfully deleted!', keep_on_top=True)
        # else:
        #     sg.Popup('Error! Entries not deleted!', keep_on_top=True)

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
