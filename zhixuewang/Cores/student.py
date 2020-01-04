import hashlib
import random
import time
from json import loads
from ..Models.userModel import User
from ..Models.examModel import (
    exam_model, subject_mark_model
)
from ..Models.urlModel import (
    XTOKEN_URL, GET_EXAM_URL, INFO_URL, GET_MARK_URL, GET_PAPERID_URL, GET_ORIGINAL_URL)

class Student(User):
#class Student():
    def __init__(self, session):
        User.__init__(self, session)
        self._xtoken = ""
        self.role = "student"

    def _get_info(self) -> bool:
        r = self._session.get(INFO_URL,
                              params={"userId": self.id})
        json_data = r.json().get("student")
        if not json_data.get("clazz", False):
            return False
        return True
    
    def __get_auth_header(self, XToken: str = None) -> dict:
        def md5_encode(msg: str) -> str:
            m = hashlib.md5()
            m.update(msg.encode(encoding="utf-8"))
            return m.hexdigest()

        def get_authguid() -> str:
            strChars = ["0", "1", "2", "3", "4", "5", "6",
                        "7", "8", "9", "a", "b", "c", "d", "e", "f"]
            t = [""] * 36
            for e in range(36):
                t[e] = random.choice(strChars)
            t[14] = "4"
            if t[19].isdigit():
                t[19] = "0123456789abcdef"[3 & int(t[19]) | 8]
            else:
                t[19] = "8"
            t[8] = t[13] = t[18] = t[23] = "-"
            return "".join(t)

        auth_guid = get_authguid()
        auth_time_stamp = str(int(time.time() * 1000))
        auth_token = md5_encode(
            auth_guid + auth_time_stamp + "iflytek!@#123student")
        if XToken:
            return {
                "authbizcode": "0001",
                "authguid": auth_guid,
                "authtimestamp": auth_time_stamp,
                "authtoken": auth_token,
                "XToken": XToken
            }
        r = self._session.get(XTOKEN_URL, headers={
            "authbizcode": "0001",
            "authguid": auth_guid,
            "authtimestamp": auth_time_stamp,
            "authtoken": auth_token
        })
        if r.json()["errorCode"] != 0:
            raise Exception(r.json()["errorInfo"])
        XToken = r.json()["result"]
        self._xtoken = XToken
        return self.__get_auth_header(XToken)

    def __get_page_exam_data(self, page_num, page_size = 10):
        r = self._session.get(
            GET_EXAM_URL,
            params={
                "actualPosition": 0,
                "pageIndex": page_num,
                "pageSize": page_size
            }
        )
        try:
            json_data = r.json()
            return (json_data["examList"], True) if json_data.pop("hasNextPage") else (json_data["examList"], False)
        except Exception as e:
            print("ERROR")
            print(e)
            return ([], False)
        return (json_data["examList"], True) if json_data.pop("hasNextPage") else (json_data["examList"], False)

    def get_exam_and_rank(self, page_start = 1, page_end = 1) ->list:
        #GET EXAM ID AND NAME
        rank_data = list()
        check = True
        page = page_start
        while check and page <= page_end:
            json_data, check = self.__get_page_exam_data(page,10)
            for exam in json_data:
                now = exam_model(
                    id=exam["examId"],
                    name=exam["examName"],
                )
                r = self._session.get(GET_PAPERID_URL, params={"examId": now.id},
                            headers=self.__get_auth_header(self._xtoken))
                json_data2 = r.json()
                if json_data2["errorCode"] != 0:
                    raise Exception(json_data2["errorInfo"])
                subjects = list()
                for paper in json_data2["result"]["paperList"]:
                    subjects.append(subject_mark_model(
                        mark = float(paper["userScore"]),
                        class_rank = int(exam["customClassRank"]),
                        grade_rank = int(exam["customSchoolRank"]),
                        subj = str(paper["subjectName"]),
                        exam = now
                    ))
                rank_data.append(subjects)
            page += 1
        return rank_data
        #GET EXAM RANK
    
    def mark_generater(self):
        paper_loc = 1
        cnt = 0
        pool = self.get_exam_and_rank(paper_loc,paper_loc)
        while 1:
            if cnt < len(pool):
                yield pool[cnt]
                cnt += 1
            else:
                paper_loc += 1
                cnt = 0
                pool = self.get_exam_and_rank(paper_loc,paper_loc)
                yield pool[cnt]
        