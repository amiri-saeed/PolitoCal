# import csv
# import requests
# import pandas as pd
# import xml.etree.ElementTree as ET




# url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/visualizzazioneStudente.aspx?idImtNumcor=203963-0/203964-0/203965-0/203966-0/204679-0&annoAccademico=2024&pd=2&xml=S"
# xml_data = requests.get(url).content
# root = ET.fromstring(xml_data)

# df = pd.DataFrame(columns=['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location'])


# # data_list = []
# for i, schedule_item in enumerate(root.findall('.//BLOCCO_ORARIO_STUDENTE')):
#     row = {
#         'Start Time': schedule_item.find('ORA_INIZIO').text,
#         'End Time': schedule_item.find('ORA_FINE').text,
#         'Event Type': schedule_item.find('TIPOLOGIA_EVENTO').text,
#         'Event Description': schedule_item.find('DESCRIZIONE_EVENTO').text,
#         'Subject Title': schedule_item.find('TITOLO_MATERIA').text,
#         'Module Title': schedule_item.find('TITOLO_MODULO').text,
#         'Last Name': schedule_item.find('COGNOME').text,
#         'First Name': schedule_item.find('NOME').text,
#         'Group Number': schedule_item.find('NUMCOR').text,
#         'Room URL': schedule_item.find('URL_MAPPA_AULA').text,
#         'Room Name': schedule_item.find('RM_NAME').text,
#         'LAT': schedule_item.find('LAT').text.replace(',', '.'),
#         'LON': schedule_item.find('LON').text.replace(',', '.'),
#     }

#     subj = row["Subject Title"]
#     start_date = row["Start Time"].split(' ')[0]
#     start_date = '/'.join([start_date.split('/')[1], start_date.split('/')[0], start_date.split('/')[2]]) # date formating changed in google api apparently!

#     start_time = row["Start Time"].split(' ')[1]
#     end_date = row["End Time"].split(' ')[0]
#     end_date = '/'.join([end_date.split('/')[1], end_date.split('/')[0], end_date.split('/')[2]])

#     end_time = row["End Time"].split(' ')[1]
#     all_day_event = False
#     map_loc = "https://www.google.com/maps/place/{}+{}".format(row["LAT"], row["LON"])
#     description = row["First Name"] + ' ' + row["Last Name"] + ', ' + row["Event Type"] + ', ' + map_loc
#     location = row["Room Name"]
#     df.loc[i] = [subj, start_date, start_time, end_date, end_time, all_day_event, description, location]

# #     # Add the dictionary to the list
# #     data_list.append(row)


# # print('/'.join([start_date.split('/')[1], start_date.split('/')[0], start_date.split('/')[2]]))


# df.to_csv("parsed.csv", index=False)




# import requests
# # import pandas as pd
# import xml.etree.ElementTree as ET

# def parse_university_calendar(url):
#     xml_data = requests.get(url).content
#     root = ET.fromstring(xml_data)

#     events = []
#     for i, schedule_item in enumerate(root.findall('.//BLOCCO_ORARIO_STUDENTE')):
#         row = {
#             'Start Time': schedule_item.find('ORA_INIZIO').text,
#             'End Time': schedule_item.find('ORA_FINE').text,
#             'Event Type': schedule_item.find('TIPOLOGIA_EVENTO').text,
#             'Event Description': schedule_item.find('DESCRIZIONE_EVENTO').text,
#             'Subject Title': schedule_item.find('TITOLO_MATERIA').text,
#             'Module Title': schedule_item.find('TITOLO_MODULO').text,
#             'Last Name': schedule_item.find('COGNOME').text,
#             'First Name': schedule_item.find('NOME').text,
#             'Group Number': schedule_item.find('NUMCOR').text,
#             'Room URL': schedule_item.find('URL_MAPPA_AULA').text,
#             'Room Name': schedule_item.find('RM_NAME').text,
#             'LAT': schedule_item.find('LAT').text.replace(',', '.'),
#             'LON': schedule_item.find('LON').text.replace(',', '.'),
#         }

#         subj = row["Subject Title"]
#         start_date = row["Start Time"].split(' ')[0]
#         start_date = '/'.join([start_date.split('/')[1], start_date.split('/')[0], start_date.split('/')[2]])

#         start_time = row["Start Time"].split(' ')[1]
#         end_date = row["End Time"].split(' ')[0]
#         end_date = '/'.join([end_date.split('/')[1], end_date.split('/')[0], end_date.split('/')[2]])

#         end_time = row["End Time"].split(' ')[1]
#         all_day_event = False
#         map_loc = f"https://www.google.com/maps/place/{row['LAT']}+{row['LON']}"
#         description = f"{row['First Name']} {row['Last Name']}, {row['Event Type']}, {map_loc}"
#         location = row["Room Name"]

#         # Prepare event dictionary in Google Calendar format
#         event = {
#             'summary': subj,
#             'location': location,
#             'description': description,
#             'start': {
#                 'dateTime': f"{start_date}T{start_time}",
#                 'timeZone': 'Europe/Rome',  # You can change the time zone according to your needs
#             },
#             'end': {
#                 'dateTime': f"{end_date}T{end_time}",
#                 'timeZone': 'Europe/Rome',
#             },
#         }
#         events.append(event)
    
#     return events

# # Example usage:
# if __name__ == "__main__":
#     # url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/visualizzazioneStudente.aspx?idImtNumcor=203963-0/203964-0/203965-0/203966-0/204679-0&annoAccademico=2024&pd=2&xml=S"
#     url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/visualizzazioneStudente.aspx?idImtNumcor=206643-0/206644-0/208074-0/208075-0/211862-0/215134-1&annoAccademico=2025&pd=1&datarif=23/09/2024&xml=S&Culture_Language=it-IT"
#     events = parse_university_calendar(url)
#     print(events)



from datetime import datetime
import requests
import xml.etree.ElementTree as ET

# def parse_university_calendar(url):
#     xml_data = requests.get(url).content
#     root = ET.fromstring(xml_data)

#     events = []
#     for i, schedule_item in enumerate(root.findall('.//BLOCCO_ORARIO_STUDENTE')):
#         start_time = schedule_item.find('ORA_INIZIO').text
#         end_time = schedule_item.find('ORA_FINE').text

#         # Convert date and time to ISO 8601 format, assuming seconds are included in the format
#         start_datetime = datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')
#         end_datetime = datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')

#         # Prepare event dictionary in Google Calendar format
#         event = {
#             'summary': schedule_item.find('TITOLO_MATERIA').text,
#             'location': schedule_item.find('RM_NAME').text,
#             'description': f"{schedule_item.find('NOME').text} {schedule_item.find('COGNOME').text}, {schedule_item.find('TIPOLOGIA_EVENTO').text}",
#             'start': {
#                 'dateTime': start_datetime.isoformat(),
#                 'timeZone': 'Europe/Rome',
#             },
#             'end': {
#                 'dateTime': end_datetime.isoformat(),
#                 'timeZone': 'Europe/Rome',
#             },
#         }
#         events.append(event)

#     return events

def parse_university_calendar(url):
    xml_data = requests.get(url).content
    root = ET.fromstring(xml_data)

    events = []
    for i, schedule_item in enumerate(root.findall('.//BLOCCO_ORARIO_STUDENTE')):
        # Extracting data from the XML
        subj = schedule_item.find('TITOLO_MATERIA').text
        start_time = schedule_item.find('ORA_INIZIO').text
        end_time = schedule_item.find('ORA_FINE').text

        # Convert date and time to ISO 8601 format
        start_datetime = datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')
        end_datetime = datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')

        # Create the description with more details
        description = (
            f"{schedule_item.find('NOME').text} {schedule_item.find('COGNOME').text}, "
            f"{schedule_item.find('TIPOLOGIA_EVENTO').text}, "
            f"https://www.google.com/maps/place/{schedule_item.find('LAT').text.replace(',', '.')},"
            f"{schedule_item.find('LON').text.replace(',', '.')}"
        )

        # Prepare the event dictionary
        event = {
            'summary': subj,
            'location': schedule_item.find('RM_NAME').text,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Europe/Rome',
            },
            # 'extendedProperties': {
            #     'private': {
            #         'start_date': start_time.split(' ')[0],
            #         'start_time': start_time.split(' ')[1],
            #         'end_date': end_time.split(' ')[0],
            #         'end_time': end_time.split(' ')[1],
            #         'all_day_event': False,
            #         'module_title': schedule_item.find('TITOLO_MODULO').text,
            #         'group_number': schedule_item.find('NUMCOR').text,
            #         'room_url': schedule_item.find('URL_MAPPA_AULA').text
            #     }
            # }
        }

        events.append(event)

    return events
