import requests
import urllib.parse
import json

class AddressStandardizer:
    """ Tool to standardize U.S. mailing addresses """

    def __init__(self):
        pass

    def find_usps_addr(self, addr1=None, city=None, state=None, zip_code=None, subaddr=None):
        """ Find the Zip5 and +4 portions of the zip code for a given address """
        
        url = 'https://tools.usps.com/tools/app/ziplookup/zipByAddress'
        address = {
            'address1': addr1
        }
        if city is not None:
            address['city'] = city
        if state is not None:
            address['state'] = state
        if zip_code is not None:
            address['zip'] = zip_code
        if subaddr is not None:
            address['address2'] = subaddr
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        address = urllib.parse.urlencode(address)
        req = requests.Request(method='POST', url=url, headers=headers, data=address)
        session = requests.Session()
        session.max_redirects = 160
        r = session.send(req.prepare())
        resp = r.json()
        if resp['resultStatus'] != 'SUCCESS' or len(resp['addressList']) == 0:
            return None
        top_result = resp['addressList'][0]
        session.close()
        return top_result


    def find_city_by_zip(self, zip_code):
        """ Find the corresponding City/State info based on the zip code provided
        
        Params:
        `zip_code`: Must be a string of the zip code
        """

        if type(zip_code) is not str:
            raise TypeError('Zip code was not provided as a string')



        url = 'https://tools.usps.com/tools/app/ziplookup/cityByZip'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {'zip': zip_code}
        data = urllib.parse.urlencode(data)

        req = requests.Request(method="POST", url=url, headers=headers, data=data)
        session = requests.Session()
        session.max_redirects = 160
        r = session.send(req.prepare())
        resp = r.json()
        if resp['resultStatus'] != 'SUCCESS':
            return None
        city = resp['defaultCity']
        state = resp['defaultState']
        session.close()
        return city, state


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))