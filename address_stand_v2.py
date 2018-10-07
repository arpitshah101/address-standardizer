# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 13:49:42 2018

@author: Elaine
"""

import os
import pandas as pd
import numpy as np
import usaddress

def create_parsed_addrs(df):
    address_all = df
    address_all=address_all.iloc[:,0:5]

    address=address_all.iloc[:,0:2] ## select just the first 2 columns
    #address.insert(0, 'New_ID', range(0, len(address)))
    address = address.replace(np.nan, '', regex=True)



    #address_test=address.head(n=7)


    #import usaddress
    #addr='123 Main St. Suite 100 Chicago, IL'
    #usaddress.tag(addr)

    # print(address[adr_ln_1_txt])

    #address2 = address.assign(Stringy = address.adr_ln_1_txt.astype(str) + ' ' + address.adr_ln_2_txt.astype(str)+ ' ' + address.cty_nm.astype(str)+' ' +address.st_cd.astype(str)+' ' + address.zip_cd_txt.astype(str)+' ')
    address2= address.assign(Stringy = address.adr_ln_1_txt.astype(str) + ' ' + address.adr_ln_2_txt.astype(str))


    AddressList=list() ### list of all the address components for all 1044 entries in the sample data table
    for row in address2['Stringy']:
        AddressList.append(usaddress.tag(row))

    ##problem entries
    probs=dict() #holds the indexes of entries that are giving us problems, i.e. missing data
    probs['address']=set()
    for i in range(len(AddressList)):
        if AddressList[i][1]=='Ambiguous':
            probs['address'].add(i)
        
    cityList=list()
    for row in address_all.cty_nm.astype(str):
        cityList.append(usaddress.tag(row))

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)


    ### state/city dictionary
    address_all=address_all.replace(np.nan, 'NA', regex=True) #change NaN to "NA" so I can fetch them later
    cityStateZip=dict()
    for row in address_all.index:
        cityStateZip[row]=dict()
        if hasNumbers(address_all.iloc[:,2][row])==False:
            cityStateZip[row]['city']=address_all.iloc[:,2][row]
        elif row in probs['address']:
            catch=usaddress.tag(address_all.iloc[:,2][row])
            for item in catch[0]:
                AddressList[row][0][item]=catch[0][item]
            cityStateZip[row]['city']='NA'
            
        else:
            cityStateZip[row]['city']='NA'
            
        cityStateZip[row]['state']=address_all.iloc[:,3][row]
        
        if 'E' in  address_all.iloc[:,4][row]:
            cityStateZip[row]['zipcode']='NA'
        elif len(address_all.iloc[:,4][row])==4:
            cityStateZip[row]['zipcode']='0'+address_all.iloc[:,4][row]
        elif len(address_all.iloc[:,4][row])==8:
            cityStateZip[row]['zipcode']='0'+address_all.iloc[:,4][row][0:4]+'-'+address_all.iloc[:,4][row][4:8]
        elif len(address_all.iloc[:,4][row])==5:
            cityStateZip[row]['zipcode']=address_all.iloc[:,4][row]
        elif len(address_all.iloc[:,4][row])==10:
            if address_all.iloc[:,4][row][0:5].isdigit() and address_all.iloc[:,4][245][6:10].isdigit() and address_all.iloc[:,4][245][5]=='-':
                cityStateZip[row]['zipcode']=address_all.iloc[:,4][row]
        else:
            cityStateZip[row]['zipcode']='NA'

            
        
    ### verify that the city and State match the zipcode
    ###arpit figured out a way?


    probs['state']=set() #18
    probs['city']=set() #55
    probs['zipcode']=set() #164
    for item in cityStateZip:
        if cityStateZip[item]['state']=='NA':
            probs['state'].add(item)
        if cityStateZip[item]['city']=='NA':
            probs['city'].add(item)
        if cityStateZip[item]['zipcode']=='NA':
            probs['zipcode'].add(item)

    #superproblems=probs['state']&probs['city']&probs['zipcode'] ## actually none of these are problems because the city/state info are in the address columns
    #superproblems=probs['state']&probs['city']
    for item in probs['state']:
        try:
            cityStateZip[item]['state']=AddressList[item][0]['StateName']
        except KeyError:
            cityStateZip[item]['state']='NA'
    for item in probs['city']:
        try:
            cityStateZip[item]['city']=AddressList[item][0]['PlaceName']
        except KeyError:
            cityStateZip[item]['city']='NA'
    for item in probs['zipcode']:
        try:
            cityStateZip[item]['zipcode']=AddressList[item][0]['ZipCode']
        except KeyError:
            cityStateZip[item]['zipcode']='NA'


    probs_after=dict() #holds the indexes of entries that are giving us problems, i.e. missing data
    probs_after['state']=set() #15
    probs_after['city']=set() #51
    probs_after['zipcode']=set() #161
    for item in cityStateZip:
        if cityStateZip[item]['state']=='NA':
            probs_after['state'].add(item)
        if cityStateZip[item]['city']=='NA':
            probs_after['city'].add(item)
        if cityStateZip[item]['zipcode']=='NA':
            probs_after['zipcode'].add(item)
        
    #probs_after['state']&probs_after['city']&probs_after['zipcode'] is an empty set, so there are no rows that are missing all three (but there still might be errors in zipcode)
            
    ### need to clean up the city column

            
    #if there is no address number in the address, but there is a occupancy identifier, put this as the address number
    for i in range(len(AddressList)):
        for thing in cityStateZip[i]:
            AddressList[i][0][thing]=cityStateZip[i][thing]

    ##AddressList now has the street address info, city, state, and zipcode
    return AddressList
        