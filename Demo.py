import getpass
import os

def show(exam):
    print("+++++++++++++++++++++++++++++++++++++++++++++++")
    print("考试名称：{}\n班级排名：{}\n年级排名：{}".format(
        exam[0].exam.name,
        exam[0].class_rank,
        exam[0].grade_rank
    ))
    for subj in exam:
        print("科目：{} 分数：{}".format(
            subj.subj,
            subj.mark
        ))
def showTheFuckingProgramAndKickItsAss(user:str,password:str):
    from zhixuewang import Zhixuewang
    zxw = Zhixuewang(user,password)
    x = zxw.mark_generater()
    for i in range(10):
        show(next(x))
if __name__ == "__main__":
    user = str(input("Please input your UserID:"))
    password = str(getpass.getpass("Please input your password:"))
    showTheFuckingProgramAndKickItsAss(user,password)
    os.system("PAUSE")