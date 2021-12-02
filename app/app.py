import PySimpleGUI as sg
from pymongo import MongoClient

timeTable = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
hourTable = []
for h in range(0, 24):
    hourTable.append(str(h))
minuteTable = []
for m in range(0, 60):
    minuteTable.append(str(m))


def pretty_people(result, name):
    new_data = []
    i = 1
    for person in result:
        new_data.append(str(i) + ") Name: " + person[name + ".name"] +
                        " - Surname: " + person[name + ".surname"] +
                        " - CF: " + str(person[name + ".cf"]))
        i = i + 1
    return new_data


# column where user can query manually
custom_query_column = [
    [
        sg.Text("Search for partecipants:", font="16"),
    ],
    [
        sg.In(key='-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d')
    ],
    [
        sg.Text("Starting time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-START-TIME-",
            default_value="00:00"
        ),
        sg.Text("Ending time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-END-TIME-",
            default_value="23:00"
        ),
    ],
    [
        sg.Text("Select the place:", font="10"),
    ],
    [
        sg.Checkbox("Unvaccinated", enable_events=True, key="-UNVACCINATED-"),
        sg.Checkbox("Vaccinated", enable_events=True, key="-VACCINATED-"),
        sg.Checkbox("Tested Negative", enable_events=True, key="-TESTED-"),
        sg.Button(button_text="Send Query", enable_events=True, key="-CUSTOM-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(55, 20),
            key="-CUSTOM-LIST-",
            horizontal_scroll=True
        )
    ]
]

# column with predefined queries
pred_query_column = [
    [
        sg.OptionMenu(
            values=["People whose last test was positive", "Cohabitants of infected", "Infection Statistics",
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
client = MongoClient("mongodb+srv://root:smbud@smbud.icy9p.mongodb.net/test?retryWrites=true&w=majority")
db = client.smbud_data
collection = db.smbud

# event loop
while True:
    event, values = window.read()

    if event == "-VACCINATED-":
        if values["-VACCINATED-"]:
            window["-UNVACCINATED-"].update(disabled=True)
        else:
            window["-UNVACCINATED-"].update(disabled=False)

    if event == "-UNVACCINATED-":
        if values["-UNVACCINATED-"]:
            window["-VACCINATED-"].update(disabled=True)
        else:
            window["-VACCINATED-"].update(disabled=False)

    if event == "-CUSTOM-QUERY-":
        date = window["-DATE-"].get().split("-")
        start_time = values["-START-TIME-"].split(":")
        end_time = values["-END-TIME-"].split(":")
        place = values["-PLACE-"]
        a1 = ""
        a2 = ""
        a3 = ""
        a4 = ""
        a5 = ""

        if values["-VACCINATED-"]:
            pass
        if values["-TESTED-"]:
            pass
        if values["-UNVACCINATED-"]:
            pass

        query = ""
        # data = graph.run(query).data()
        # pretty_data = pretty_people(data, "p")
        # window["-CUSTOM-LIST-"].update(pretty_data)
        # if not data:
        #     sg.Popup('No result', keep_on_top=True)

    if event == "-SEND-QUERY-":
        pretty_data = []
        base_query = ""
        if values["-QUERY-"] == "People whose last test was positive":
            query = ""
            # data = graph.run(query).data()
            # pretty_data = pretty_people(data, "illPeople")
        if values["-QUERY-"] == "Cohabitants of infected":
            query = base_query + ""
            # data = graph.run(query).data()
            # pretty_data = pretty_people(data, "p")
        if values["-QUERY-"] == "Infection Statistics":
            query = ""
            # data = graph.run(query).data()
            # print(data)
            # for attribute in data[0]:
            #     pretty_data.append(str(attribute) + ": " + str(data[0][attribute]))
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
