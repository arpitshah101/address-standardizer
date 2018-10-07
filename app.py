import pandas as pd
import numpy as np
import usaddress
from address_standardizer import AddressStandardizer
import address_stand_v2

import collections


def generate_str1(parsed_addr):
    """
        [AddressNumber] [StreetNamePreType/StreetNamePreDirectional] [StreetName]
        [StreetNamePostType/StreetNamePostDirectional]
    """
    addr = parsed_addr[0]
    # print(addr)
    output = ''
    for key, value in addr.items():
        if key == 'Recipient' or key == 'SubaddressType' or key == 'SubaddressIdentifier' or key == 'OccupancyIdentifier':
            # skip this one
            continue
        if key == 'OccupancyType' or key == 'city' or key == 'state' or key == 'zipcode':
            # done with street 1 box so we outt
            continue
        if key == 'USPSBoxType':
            output += 'PO BOX '
        else:
            output += str(value) + ' '
    return output


def get_subaddress(parsed_addr):
    addr = parsed_addr[0]
    output = ''
    for key, value in addr.items():
        if key == 'SubaddressType' or key == 'SubaddressIdentifier' or key == 'OccupancyType' or key == 'OccupancyIdentifier':
            output += value + ' '
    return output


def get_city(parsed_addr):
    addr = parsed_addr[0]
    for key, value in addr.items():
        if key == 'city':
            return value
    return None


def get_state(parsed_addr):
    addr = parsed_addr[0]
    for key, value in addr.items():
        if key == 'state':
            return value
    return None


def find_zip(parsed_addr):
    addr = parsed_addr[0]
    for key, value in addr.items():
        if key == 'zipcode':
            return value
    return None


def print_formatted_address(usps_result, addr_dict):
    if 'Recipient' in addr_dict.keys():
        print('%s\n' % (addr_dict['Recipient']), end='')
    print('%s\n%s, %s %s-%s' % (usps_result['addressLine1'], usps_result['city'], usps_result['state'], usps_result['zip5'], usps_result['zip4']))


def all_nums(str):
    return all(char.isdigit() for char in str)


def clean_addr(parsed_addr):
    addr = dict(parsed_addr[0])
    results = [parsed_addr]
    try:
        if 'AddressNumber' not in addr.keys() and 'OccupancyIdentifier' in addr.keys():
            # check if 2 tokens
            tkns = addr['OccupancyIdentifier'].split(' ')
            if len(tkns) > 1:
                result = collections.OrderedDict()
                result['AddressNumber'] =  tkns[1]
                for key, value in addr.items():
                    if key != 'OccupancyIdentifier':
                        result[key] = value
                    else:
                        result[key] = tkns[0]
                results.append((result, 0))
                addr = dict(result)
        if 'AddressNumber' in addr.keys() and 'OccupancyIdentifier' not in addr.keys():
            tkns = addr['AddressNumber'].split(' ')
            if len(tkns) > 1:
                result = collections.OrderedDict()
                result['AddressNumber'] = tkns[1]
                result['OccupancyIdentifier'] = tkns[0]
                for key, value in addr.items():
                    if key != 'AddressNumber':
                        result[key] = value
                results.append((result, 0))
                addr = dict(result)
        if 'StreetName' in addr.keys():
            street_split = addr['StreetName'].split(' ')
            if len(street_split) > 1 and all_nums(street_split[0]):
                # make this new addressNumber
                # if one already exists, make that occupancyIdentifier

                curr_addr_num = addr['AddressNumber']
                
                result = collections.OrderedDict()
                result['AddressNumber'] = street_split[0]
                result['StreetName'] = ' '.join(street_split[1:])
                if curr_addr_num is not None:
                    result['OccupancyIdentifier'] = curr_addr_num
                for key, value in addr.items():
                    if key != 'AddressNumber' and key != 'StreetName':
                        result[key] = value
                results.append((result, 0))
                addr = dict(result)
        if 'OccupancyIdentifier' in addr.keys():
            occ_split = addr['OccupancyIdentifier'].split(' ')
            result = collections.OrderedDict()
            if len(occ_split) > 1 and all_nums(occ_split[1]) and all_nums(occ_split[1]):
                result['AddressNumber'] = occ_split[1]
                result['OccupancyIdentifier'] = occ_split[0]
                for key, value in addr.items():
                    if key != 'AddressNumber' and key != 'PlaceName':
                        result[key] = value
            else:
                for key, value in addr.items():
                    result[key] = value
            if 'PlaceName' in addr.keys():
                result['StreetName'] = addr['PlaceName']
                del result['PlaceName']
            occ_type = result['OccupancyType']
            occ_id = result['OccupancyIdentifier']
            del result['OccupancyType']
            del result['OccupancyIdentifier']
            result['OccupancyType'] = occ_type
            result['OccupancyIdentifier'] = occ_id
            addr = dict(result)
            results.append((result, 0))
    except:
        return results[-1]
    return results[-1]


def print_regular_addr(parsed_addr):
    addr = parsed_addr[0]
    output = ''
    for key, value in addr.items():
        output += value + ' '
    print(output[:-1])


if __name__ == '__main__':
    filepath = 'HackRu 2018 Challenge - Addresses.tsv'
    data = pd.read_csv(filepath, sep='\t')
    parsed_addrs = address_stand_v2.create_parsed_addrs(data)
    # [x] Get needed fields from Elaine

    # print(generate_str1(parsed_addrs[245]))
    # print(parsed_addrs[245])

    total_issues = 0
    without_subaddr = 0
    addr_count = 0

    addr_util = AddressStandardizer()
    for addr in parsed_addrs:
        addr_count += 1

        addr = clean_addr(addr)
        addr_dict = dict(addr[0])
        if 'StreetName' not in addr_dict and 'USPSBoxType' not in addr_dict:
            print_regular_addr(addr)
            continue
        street1 = generate_str1(addr)
        subaddr = get_subaddress(addr)
        city = get_city(addr)
        state = get_state(addr)
        zip_code = find_zip(addr)
        if city == 'NA':
            city = None
        if state == 'NA':
            state = None
        usps_result = addr_util.find_usps_addr(street1, city, state, zip_code, subaddr)
        if usps_result is None:
            usps_result = addr_util.find_usps_addr(street1, city, state, zip_code)
            if usps_result is None:
                print('something went wrong')
                # print_regular_addr(addr)
                # print(addr_dict)
                total_issues += 1
                print('Problem: %d' % addr_count)
                continue
            else:
                # print_formatted_address(usps_result, addr_dict)
                total_issues += 1
                without_subaddr += 1
                print('Problem: %d' % addr_count)
        # print_formatted_address(usps_result, addr_dict)

        # try:
        #     print_formatted_address(usps_result, addr_dict)
        #     print('\n\n')
        # except:
        #     print('something went wrong with printing...')
        #     # print(addr)
        #     print_regular_addr(addr)
        #     print('\n\n')
        #     # print(usps_result)
        #     break
    print("Total issues: %d" % total_issues)
    print("Without subaddress: %d" % without_subaddr)

    # print(generate_str1(parsed_addrs[150]))
    # print(parsed_addrs[150])
    

    # zip_code = addr_util.find_zip("8016 LEDGEFERN CIRCLE", "SAN RAMONO", "CA")
    # zip_code = addr_util.find_zip("# 1", "SLEEPY HOLLOW", "NY")
    # zip_code = addr_util.find_zip()
    # if zip_code is not None:
    #     print(zip_code)
    # else:
    #     print('found error')
    
    # city, state = addr_util.find_city_by_zip("94582")

    # print('city: %s\nstate: %s\n' % (city, state))
    
    # # Reconstruct address based on Elaine's fields and zip code response

    # # Fix casing to be combined rather than all-caps