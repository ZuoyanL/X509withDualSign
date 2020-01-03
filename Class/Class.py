class Class:
    def __init__(self, scores=[], comments=[]):
        self.scores = scores
        self.comments = comments

    def get_avg_score(self):
        if len(self.scores) > 0:
            return sum(self.scores) / float(len(self.scores))
        else:
            return -1

    def print_comments(self):
        if len(self.comments) == 0:
            print('This class has\'nt been rated...')
        con = 1
        for i in self.comments:
            print(con, ".", i)
            con+=1

    def set_score(self, score):
        self.scores.append(score)

    def set_comment(self, comment):
        self.comments.append(comment)