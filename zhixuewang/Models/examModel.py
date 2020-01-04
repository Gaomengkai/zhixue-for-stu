class exam_model(object):
    def __init__(self, id: str, name: str):
        self.id: str = id
        self.name: str = name

    def __repr__(self):
        return f"examModel(id={self.id}, name={self.name})"

class subject_mark_model(object):
    def __init__(self, subj: str, mark: float, class_rank: int, grade_rank: int, exam):
        '''
        Single subject mark model
        :param subj:
            Subject_Name such as 数学 or 英语
        :param mark:
            its mark
        :param class_rank:
            Your rank in your class
        :param grade_rank:
            Your rank in your grade
        :return:
        '''
        self.subj = subj
        self.mark = mark
        self.class_rank = class_rank
        self.grade_rank = grade_rank
        self.exam = exam
