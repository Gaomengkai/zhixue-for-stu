import requests
import random
import json
from .Models.urlModel import (
    SSO_URL, TEST_PASSWORD_URL, SERVICE_URL)

from .Models.exceptionsModel import (
    LoginError, UserDefunctError, UserNotFound, UserOrPassError, ArgError)
from .Cores.student import Student

def login_id(user_id: str, password: str) -> requests.session:
    """
    通过用户id和密码登录
    :param user_id: 用户id
    :param password: 密码
    :return
        返回session
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    msg = session.get(SSO_URL).text
    json_obj = json.loads(
        msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1000:
        raise LoginError(json_obj["data"])
    data = json_obj["data"]
    msg = session.get(SSO_URL,
                      params={
                          "username": user_id,
                          "password": password,
                          "sourceappname": "tkyh,tkyh",
                          "key": "id",
                          "_eventId": "submit",
                          "lt": data["lt"],
                          "execution": data["execution"],
                          "encode": False
                      }).text
    json_obj = json.loads(
        msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1001:
        if json_obj["code"] == 1002:
            raise UserOrPassError()
        elif json_obj["code"] == 2009:
            raise UserNotFound()
        raise LoginError(json_obj["data"])
    session.post(SERVICE_URL, data={
        "action": "login",
        "username": user_id,
        "password": password,
        "ticket": json_obj["data"]["st"],
    })
    return session

def get_user_id(user_name: str, password: str) -> str:
    """
    返回用户id
    :param username: 智学网用户名
    :param password: 智学网密码
    :return:
        成功则返回session和user_id
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    data = session.post(TEST_PASSWORD_URL, data={
        "loginName": user_name,
        "password": password,
        "code": ""
    }).json()
    if data.get("data"):
        return data["data"]
    elif data["result"] != "success":
        raise UserOrPassError()
    return None

def Zhixuewang(user_name: str = None, password: str = None, user_id: str = None):
    """
    通过(用户id, 密码)或(用户名, 密码)登录智学网
    :param user_name: 用户名
    :param password: 密码
    :param user_id: 用户id
    :return 

    """
    if not (password and any([user_name, user_id])):
        raise ArgError("请检查参数.")
    session = requests.Session()
    if user_name:
        session = login_id(get_user_id(user_name, password), password)
    else:
        session = login_id(user_id, password)
    user = Student(session)
    if not user._get_info():
        raise UserDefunctError("帐号已失效")
    return user