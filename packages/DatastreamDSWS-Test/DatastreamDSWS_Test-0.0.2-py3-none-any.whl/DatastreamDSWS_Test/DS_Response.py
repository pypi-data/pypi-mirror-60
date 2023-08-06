# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 19:51:02 2019

@author: Vidya Dinesh
"""
import urllib3
import json
import pandas as pd
import datetime
import pytz
import traceback

from DS_Requests import TokenRequest, Instrument, Properties, DataRequest, DataType, Date

#--------------------------------------------------------------------------------------
class Datastream:
    """Datastream helps to retrieve data from DSWS web rest service"""
    url = "https://product.datastream.com/DSWSClient/V1/DSService.svc/rest/"
    username = ""
    password = ""
    token = None
    dataSource = None
    _proxy = None
    _sslCer = None
    appID = "PythonLib 1.0"
    certfile = None
   
    
#--------Constructor ---------------------------  
    def __init__(self, username, password, dataSource=None, proxy=None, sslCer= None):
        if proxy:
            self._proxy = proxy
        if sslCer:
            self._sslCer = sslCer
        self.username = username
        self.password = password
        self.dataSource = dataSource
        self.token = self._get_token()
        
#-------------------------------------------------------  
#------------------------------------------------------- 
    def post_user_request(self, tickers, fields=None, start='', end='', freq='', kind=1):
        """ This function helps to form requests for get_bundle_data. 
            Each request is converted to JSON format.
            
            Args:
               tickers: string, Dataypes 
               fields: List, default None
               start: string, default ''
               end : string, default ''
               freq : string, default '', By deafult DSWS treats as Daily freq
               kind: int, default 1, indicates Timeseries as output

          Returns:
                  Dictionary"""

            
        if fields == None:
            fields=[]
                         
        index = tickers.rfind('|')
        try:
            if index == -1:
                instrument = Instrument(tickers, None)
            else:
                #Get all the properties of the instrument
                props = []
                if tickers[index+1:].rfind(',') != -1:
                    propList = tickers[index+1:].split(',')
                    for eachProp in propList:
                        props.append(Properties(eachProp, True))
                else:
                    props.append(Properties(tickers[index+1:], True))
                    #Get the no of instruments given in the request
                    instList =  tickers[0:index].split(',')
                    if len(instList) > 40:
                        raise Exception('Too many instruments in single request')
                    else:
                        instrument = Instrument(tickers[0:index], props)
                        
            datypes=[]
            if len(fields) > 0:
                if len(fields) > 20:
                    raise Exception('Too mant datatypes in single request')
                else:
                    for eachDtype in fields:
                        datypes.append(DataType(eachDtype))
            else:
                datypes.append(DataType(fields))
                        
            date = Date(start, freq, end, kind)
            request = {"Instrument":instrument,"DataTypes":datypes,"Date":date}
            return request
        except Exception:
            print("post_user_request : Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=5))
            return None
            
    def get_data(self, tickers, fields=None, start='', end='', freq='', kind=1):
        """This Function processes a single JSON format request to provide
           data response from DSWS web in the form of python Dataframe
           
           Args:
               tickers: string, Dataypes 
               fields: List, default None
               start: string, default ''
               end : string, default ''
               freq : string, default '', By deafult DSWS treats as Daily freq
               kind: int, default 1, indicates Timeseries as output

          Returns:
                  DataFrame."""
                 

        getData_url = self.url + "GetData"
        raw_dataRequest = ""
        json_dataRequest = ""
        json_Response = ""
        
        if fields == None:
            fields = []
        
        try:
            req = self.post_user_request(tickers, fields, start, end, freq, kind)
            datarequest = DataRequest()
            if (self.token == None):
                raise Exception("Invalid Token Value")
            else:
                raw_dataRequest = datarequest.get_Request(req, self.dataSource, self.token)
            if (raw_dataRequest != ""):
                json_dataRequest = json.dumps(raw_dataRequest).encode('utf-8')
                resp = None
                hdrs = {'Content-Type': 'application/json'}
                if self._proxy:
                    https = urllib3.ProxyManager(self._proxy)
                    resp = https.request('post', getData_url, headers=hdrs, body=json_dataRequest)
                elif self._sslCer:
                    https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=self._sslCer)
                    resp = https.request('post', getData_url, headers=hdrs, body=json_dataRequest)
                else:
                    https = urllib3.PoolManager(num_pools = 2)
                    resp = https.request('post', getData_url, headers=hdrs, body=json_dataRequest)
                                          
                json_Response = json.loads(resp.data.decode('utf-8'))
                #format the JSON response into readable table
                response_dataframe = self._format_Response(json_Response['DataResponse'])
                return response_dataframe
            else:
                return None
        except json.JSONDecodeError:
            print("get_data : JSON decoder Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=5))
            return None
        except Exception:
            print("get_data : Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=5))
            return None
    
    def get_bundle_data(self, bundleRequest=None):
        """This Function processes a multiple JSON format data requests to provide
           data response from DSWS web in the form of python Dataframe.
           Use post_user_request to form each JSON data request and append to a List
           to pass the bundleRequset.
           
            Args:
               bundleRequest: List, expects list of Datarequests 
            Returns:
                  DataFrame."""

        getDataBundle_url = self.url + "GetDataBundle"
        raw_dataRequest = ""
        json_dataRequest = ""
        json_Response = ""
        
        if bundleRequest == None:
            bundleRequest = []
        
        try:
            datarequest = DataRequest()
            if (self.token == None):
                raise Exception("Invalid Token Value")
            else:
                raw_dataRequest = datarequest.get_bundle_Request(bundleRequest, 
                                                             self.dataSource, 
                                                             self.token)
            
            if (raw_dataRequest != ""):
                json_dataRequest = json.dumps(raw_dataRequest).encode('utf-8')
                resp = None
                hdrs = {'Content-Type': 'application/json'}
                #Post the requests to get response in json format
                if self._proxy:
                    https = urllib3.ProxyManager(self._proxy)
                    resp = https.request('post', getDataBundle_url, headers=hdrs, body=json_dataRequest)
                elif self._sslCer:
                    https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=self._sslCer)
                    resp = https.request('post', getDataBundle_url, headers=hdrs, body=json_dataRequest)
                else:
                    https = urllib3.PoolManager(num_pools = 2)
                    resp = https.request('post', getDataBundle_url, headers=hdrs, body=json_dataRequest)
                                          
                json_Response = json.loads(resp.data.decode('utf-8'))
                #print(json_Response)
                response_dataframe = self._format_bundle_response(json_Response)
                return response_dataframe
            else:
                return None
        except json.JSONDecodeError:
            print("get_bundle_data : JSON decoder Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=5))
            return None
        except Exception:
            print("get_bundle_data : Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=5))
            return None
    
#------------------------------------------------------- 
#-------------------------------------------------------             
#-------Helper Functions---------------------------------------------------
    def _get_token(self, isProxy=False):
        token_url = self.url + "GetToken"
        try:
            propties = []
            propties.append(Properties("__AppId", self.appID))
            if self.dataSource:
                propties.append(Properties("Source", self.dataSource))
            tokenReq = TokenRequest(self.username, self.password, propties)
            raw_tokenReq = tokenReq.get_TokenRequest()
            json_tokenReq = json.dumps(raw_tokenReq).encode('utf-8')
            resp = None
            hdrs = {'Content-Type': 'application/json'}
            if self._proxy:
                https = urllib3.ProxyManager(self._proxy, num_pools=2)
                resp = https.request('post', token_url, headers=hdrs, body=json_tokenReq)
            elif self._sslCer:
                https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=self._sslCer)
                resp = https.request('post', token_url, headers=hdrs, body=json_tokenReq)
            else:
                https = urllib3.PoolManager(num_pools=2)
                resp = https.request('post', token_url, headers=hdrs, body=json_tokenReq)
            
            json_Response = json.loads(resp.data.decode('utf-8'))
            
            if 'TokenValue' in json_Response.keys():
                return json_Response["TokenValue"]
            else:
                if 'Message' in json_Response.keys():
                    print(json_Response["Message"])
                return None
        except json.JSONDecodeError:
            print("_get_token : JSON decoder Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=2))
            return None
        except Exception:
            print("_get_token : Exception Occured")
            print(traceback.sys.exc_info())
            print(traceback.print_exc(limit=2))
            return None
    
    def _get_Date(self, jsonDate):
        d = jsonDate[6:-7]
        d = float(d)
        ndate = datetime.datetime(1970,1,1) + datetime.timedelta(seconds=float(d)/1000)
        utcdate = pytz.UTC.fromutc(ndate).strftime('%Y-%m-%d')
        return utcdate
    
    def _get_DatatypeValues(self, jsonDTValues):
        df = pd.DataFrame()
        multiIndex = False
        valDict = {"Instrument":[],"Datatype":[],"Value":[]}
       
        for item in jsonDTValues: 
           datatype = item['DataType']
           for i in item['SymbolValues']:
               instrument = i['Symbol']
               valDict["Datatype"].append(datatype)
               valDict["Instrument"].append(instrument)
               values = i['Value']
               valType = i['Type']
               colNames = (instrument,datatype)
               df[colNames] = None
               
               #Handling all possible types of data as per DSSymbolResponseValueType
               if valType in [7, 8, 10, 11, 12, 13, 14, 15, 16]:
                   #These value types return an array
                   #The array can be of double, int, string or Object
                   rowCount = df.shape[0]
                   valLen = len(values)
                   #If no of Values is < rowcount, append None to values
                   if rowCount > valLen:
                       for i in range(rowCount - valLen):
                            values.append(None)
                  #Check if the array of Object is JSON dates and convert
                   for x in range(0, valLen):
                       values[x] = self._get_Date(values[x]) if str(values[x]).find('/Date(') != -1 else values[x] 
                   #Check for number of values in the array. If only one value, put in valDict
                   if len(values) > 1:
                       multiIndex = True
                       df[colNames] = values
                   else:
                       multiIndex = False
                       valDict["Value"].append(values[0])   
               elif valType in [1, 2, 3, 5, 6]:
                   #These value types return single value
                   valDict["Value"].append(values)
                   multiIndex = False
               else:
                   if valType == 4:
                       #value type 4 return single JSON date value, which needs conversion
                       values = self._get_Date(values)
                       valDict["Value"].append(values)
                       multiIndex = False
                   elif valType == 9:
                       #value type 9 return array of JSON date values, needs conversion
                       date_array = []
                       if len(values) > 1:
                          multiIndex = True
                          for eachVal in values:
                              date_array.append(self._get_Date(eachVal))
                              df[colNames] = values
                       else:
                          multiIndex = False
                          date_array.append(self._get_Date(values))
                          valDict["Value"].append(values[0])
                   else:
                       if valType == 0:
                           #Error Returned
                           #multiIndex = False
                           valDict["Value"].append(values)
                           
               if multiIndex:
                   df.columns = pd.MultiIndex.from_tuples(df.columns, names=['Instrument', 'Field'])
                       
        if not multiIndex:
            indexLen = range(len(valDict['Instrument']))
            newdf = pd.DataFrame(data=valDict,columns=["Instrument", "Datatype", "Value"],
                                 index=indexLen)
            return newdf
        return df 
            
    def _format_Response(self, response_json):
        # If dates is not available, the request is not constructed correctly
        response_json = dict(response_json)
        if 'Dates' in response_json:
            dates_converted = []
            if response_json['Dates'] != None:
                dates = response_json['Dates']
                for d in dates:
                    dates_converted.append(self._get_Date(d))
        else:
            return 'Error - please check instruments and parameters (time series or static)'
        
        # Loop through the values in the response
        dataframe = self._get_DatatypeValues(response_json['DataTypeValues'])
        if (len(dates_converted) == len(dataframe.index)):
            if (len(dates_converted) > 1):
                #dataframe.insert(loc = 0, column = 'Dates', value = dates_converted)
                dataframe.index = dates_converted
                dataframe.index.name = 'Dates'
        elif (len(dates_converted) == 1):
            dataframe['Dates'] = dates_converted[0]
            
        return dataframe

    def _format_bundle_response(self,response_json):
       formattedResp = []
       for eachDataResponse in response_json['DataResponses']:
           df = self._format_Response(eachDataResponse)
           formattedResp.append(df)      
           
       return formattedResp
   
#-------------------------------------------------------------------------------------

