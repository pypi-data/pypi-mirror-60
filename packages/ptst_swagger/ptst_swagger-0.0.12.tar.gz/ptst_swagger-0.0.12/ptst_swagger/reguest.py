__author__ = 'v.denisov'

import requests
import allure


class RegustsHelper:

    def __init__(self):
        pass

    @allure.step('Execute "GET" request ')
    def get(url, data=None, params=None, headers=None, cookies=None):
        response = None
        try:
            response = requests.request(
                "GET", url, data=data, headers=headers, params=params,
                cookies=cookies, timeout=20,  verify=False)
        except requests.exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except requests.exceptions.ReadTimeout:
            print('Oops. Read timeout occured')
        except requests.exceptions.ConnectionError:
            print('Seems like dns lookup failed..')
        except requests.exceptions.HTTPError as err:
            print('Oops. HTTP Error occured')
            print('Response is: {content}'.format(content=err.response.content))
        else:
            print('Success!')
        return response

    @allure.step('Execute "POST" request ')
    def post(url, data=None, params=None, headers=None, cookies=None):
        response = None
        try:
            response = requests.request(
                "POST", url, data=data, headers=headers, params=params,
                cookies=cookies, timeout=20,  verify=False)
        except requests.exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except requests.exceptions.ReadTimeout:
            print('Oops. Read timeout occured')
        except requests.exceptions.ConnectionError:
            print('Seems like dns lookup failed..')
        except requests.exceptions.HTTPError as err:
            print('Oops. HTTP Error occured')
            print('Response is: {content}'.format(content=err.response.content))
        else:
            print('Success!')
        return response


