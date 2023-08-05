import allure

@allure.title(" Тестируем  test_t2")
def test_t2(rais):
    r = rais.get_paths_sw()
    for rx in r:
        print('rx=', rx)
    print('r=', r)
    r2 = rais.get()
    print('r2=', r2.cookies)
    response_user = rais.get(paths='/interface/orange/user/get')
    print('response_user=', response_user.cookies, response_user.json())
