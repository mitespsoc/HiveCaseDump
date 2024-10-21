import sys

import requests
import datetime
import pandas as pd
import argparse
import configparser

def configPar():
    config = configparser.ConfigParser()
    config.read('configfile.ini')
    url = config['hive']['url']
    key = config['api']['token']
    return url,key

def get_args():
    paser = argparse.ArgumentParser()
    paser.add_argument('startId', help='start ID')
    paser.add_argument("endId", help="End ID")
    paser.add_argument("status", type=str, help="Case Status")
    arg = paser.parse_args()
    return arg.startId, arg.endId, arg.status

startId, endId, status = get_args()
url, key = configPar()

def unix_millis_to_readable(unix_millis):
    unix_seconds = int(unix_millis) / 1000
    date_time = datetime.datetime.fromtimestamp(unix_seconds)
    readable_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return readable_date

if len(sys.argv) != 4:
    print("Please provide start and end case ids")
else:
    startId=int(sys.argv[1])
    endId=int(sys.argv[2])
    status=str(sys.argv[3])


    caseArray = []
    notFoundArray = []
    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}

    
    for caseId in range(startId, endId+1):
        case = requests.get(url+str(caseId), headers=headers).json()
        try:
            formattedCase = {
                "CreatedDate": unix_millis_to_readable(case['createdAt']),
                "CreatedBy": case['createdBy'],
                "CaseID": case['caseId'],
                "Title": case['title'],
                "Description": case['description'],
                "StartedDate": unix_millis_to_readable(case['startDate']),
                "EndDate": unix_millis_to_readable(case['endDate']) if case['endDate'] is not None else "None",
                "ImpactStatus": case['impactStatus'],
                "ResolutionStatus": case['resolutionStatus'],
                "Flag": case['flag'],
                "TLP": case['tlp'],
                "PAP": case['pap'],
                "Status": case['status'],
                "Owner": case['owner'],
                "Severity": case['severity'],
                "DetectionTechnique": case['customFields']['detection-technique']['string'],
                "DetectedTime": unix_millis_to_readable(case['customFields']['event-detected-time']['date']) if case['customFields']['event-detected-time']['date'] is not None else "None",
                "EscalationStatus": case['customFields']['escalation-status']['string'],
                "Customer": case['customFields']['customer']['string']
            }
            if status == "Open":
                if formattedCase['Status'] == "Open":
                    caseArray.append(formattedCase)
                    print("[+] Case {0} Added".format(case['caseId']))
                else:
                    pass
            else:
                caseArray.append(formattedCase)
                print("[+] Case {0} Added".format(case['caseId']))

                
        except Exception as Error:
            print("[+] Case {0} Not Found, Continuing...".format(caseId))
            notFoundCase = {
                    "CaseID": caseId,
                    "Status": "NotFound"
                }
            notFoundArray.append(notFoundCase)
            pass
    
    df = pd.DataFrame(caseArray)
    dfNotFound = pd.DataFrame(notFoundArray)

    fileName="CaseList-{0}-{1}.csv".format(startId, endId)
    df.to_csv(fileName, encoding='utf-8', index=False)

    fileNameMissing="MissngCaseList-{0}-{1}.csv".format(startId, endId)
    dfNotFound.to_csv(fileNameMissing, encoding='utf-8', index=False)
    
    print("[+] Case list written to file {0}".format(fileName))
    print("[+] Missing case list written to file {0}".format(fileNameMissing))





