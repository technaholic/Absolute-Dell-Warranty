import datetime
import subprocess
import time

from absolute import absolutePython
import json

def Get_Warranty(serial):
    command = 'python3 -m dell_api -j ' + serial
    warrantyerror = 1
    output = "First Run"
    while warrantyerror == 1:
        try:
            output = str(subprocess.check_output([command], shell=True))
        except subprocess.CalledProcessError as error:
            print("ERROR!!!")
            print(error.output)
            time.sleep(5)
            return "Error"
        else:
            warrantyerror = 0


    print("Warranty output : ", output)
    output = output.replace('b"[', '')
    output = output.replace(']\\n\\x1b[0m"', '')
    output = output.replace('LookupError()', 'null')
    output = output.replace("IndexError('pop from empty list')", "null")
    output = output.replace('\'', '"')
    output = output.replace('""', 'null')
    print("Warranty output after replace : " + str(output))

    myDict = json.loads(output)
    return myDict

def Get_Machines_Absolute():

    abtAPI = absolutePython.absolutePython('<ABSAPI-Token ID>','<ABSAPI-Secret>')

    devices = abtAPI.getActiveDevices()
    index = 0

    for device in devices:
        if 'systemManufacturer' in device :
            if device['systemManufacturer'] == 'Dell':
                index += 1
                print("#### INDEX #### : " + str(index))
                if (("cdf" in device) and ("FmNM9ulnQrut7doZsFXVZA" in device['cdf']) and ("2rjsys7vTP25Ogejouc0yw" in device['cdf'])):
                    print("HAS WARRANTY!!! : " + str(device['esn']))
                    continue
                deviceCdfs = abtAPI.getDeviceCdf(device['esn'], SerialNumber=False)
                print(device)
                print(device['id'])
                currentSystem = Get_Warranty(device['serial'])
                if (currentSystem == "Error"):
                    continue
                print("currentSystem Output : " + str(currentSystem))
                if currentSystem['Start Date'] is None:
                    DellWarrantyStartDate = "01/01/1901"
                else :
                    DellWarrantyStartDate = currentSystem['Start Date'][5:7] + "/" + currentSystem['Start Date'][8:10] + "/" + currentSystem['Start Date'][0:4]
                print("Dell Warranty Start-Date : " + DellWarrantyStartDate + "  Type : " + str(type(DellWarrantyStartDate)))
                DellWarrantyStartDateCDF = GenerateWarrantyStartCDF(DellWarrantyStartDate)
                print(str(type(DellWarrantyStartDateCDF)) + " : " + str(DellWarrantyStartDateCDF))
                cdfupdateresponse = abtAPI.MakeApiReq("/v2/devices/"+device['id']+"/cdf", method='PUT', body=DellWarrantyStartDateCDF)
                print(cdfupdateresponse)
                if currentSystem['End Date'] is None:
                    DellWarrantyEndDate = "01/01/1901"
                else :
                    DellWarrantyEndDate = currentSystem['End Date'][5:7] + "/" + currentSystem['End Date'][8:10] + "/" + currentSystem['End Date'][0:4]
                print("Dell Warranty End-Date : " + DellWarrantyEndDate + "  Type : " + str(type(DellWarrantyEndDate)))
                DellWarrantyEndDateCDF = GenerateWarrantyEndCDF(DellWarrantyEndDate)
                print(str(type(DellWarrantyEndDateCDF)) + " : " + str(DellWarrantyEndDateCDF))
                cdfupdateresponse = abtAPI.MakeApiReq("/v2/devices/"+device['id']+"/cdf", method='PUT', body=DellWarrantyEndDateCDF)
                print(cdfupdateresponse)
                try :
                    deviceCdfs = abtAPI.getDeviceCdf(device['esn'], SerialNumber=False)
                except TypeError as error :
                    print(str(TypeError))
                print("CDF Values : " + str(deviceCdfs.cdfValues))
                print(deviceCdfs.deviceUid)

    print(index)

def GenerateWarrantyStartCDF(date):
    return '{"cdfValues": [{"cdsUid": "FmNM9ulnQrut7doZsFXVZA", "fieldKey": "27", "fieldValue": "' + date + '"}]}'

def GenerateWarrantyEndCDF(date):
    return '{"cdfValues": [{"cdsUid": "2rjsys7vTP25Ogejouc0yw", "fieldKey": "26", "fieldValue": "' + date + '"}]}'

def GenerateAssetNumberCDF(number):
    return '{"cdfValues": [{"cdsUid": "K65Sc6OhS8C9CtkdqMqDLA", "fieldKey": "1", "fieldValue": "' + number + '"}]}'

def TestMethod():
    abtAPI = absolutePython.absolutePython('<ABSAPI-Token ID>','<ABSAPI-Secret>')
    device = abtAPI.getDevice('666PR33', SerialNumbers=True)
    print(json.dumps(device, sort_keys=False))
    if (("FmNM9ulnQrut7doZsFXVZA" in device[0]['cdf']) and ("2rjsys7vTP25Ogejouc0yw" in device[0]['cdf'])):
        print("HAS WARRANTY!!!")
    deviceCdfs = abtAPI.getDeviceCdf('666PR33', SerialNumber = True)
    for cdf in deviceCdfs.cdfValues:
        print(cdf['fieldKey'])
        if cdf['fieldKey'] == 27:
            print("Warranty Exists : " + str(cdf))
            break
    print(deviceCdfs.cdfValues)
    print(deviceCdfs.deviceUid)
    warrantyjson = Get_Warranty('666PR33')
    print(warrantyjson)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    starttime = datetime.datetime.now()
    #Get_Warranty()
    Get_Machines_Absolute()
    #TestMethod()
    endtime = datetime.datetime.now()
    print("Start Time : " + str(starttime))
    print("End Time : " + str(endtime))
    print("Difference : " + str(endtime - starttime))