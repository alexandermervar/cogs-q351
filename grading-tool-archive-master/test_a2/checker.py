#!/usr/bin/python3
def checked_board(tester, StudentBoard):
    class CheckedBoard(StudentBoard):
        def placeValue(self, *args, **kwargs):
            tester.set_plagiarism_flag()
            return self.makeMove(*args, **kwargs)
        def removeValue(self, *args, **kwargs):
            tester.set_plagiarism_flag()
            return self.undoMove(*args, **kwargs)
        def rcToBox(self, *args, **kwargs):
            tester.set_plagiarism_flag()
            return self.spaceToBox(*args, **kwargs)
        def solve(self, *args, **kwargs):
            tester.set_plagiarism_flag()
            return self.solveBoard(*args, **kwargs)
        def placeValue(self, *args, **kwargs):
            if not hasattr(StudentBoard, 'placeValue') and hasattr(StudentBoard, 'makeMove'):
                tester.set_plagiarism_flag()
                return StudentBoard.makeMove(self, *args, **kwargs)
            return StudentBoard.placeValue(self, *args, **kwargs)
        def removeValue(self, *args, **kwargs):
            if not hasattr(StudentBoard, 'removeValue') and hasattr(StudentBoard, 'removeMove'):
                tester.set_plagiarism_flag()
                return StudentBoard.removeMove(self, *args, **kwargs)
            return StudentBoard.removeValue(self, *args, **kwargs)
        def spaceToBox(self, *args, **kwargs):
            if not hasattr(StudentBoard, 'spaceToBox') and hasattr(StudentBoard, 'rcToBox'):
                tester.set_plagiarism_flag()
                return StudentBoard.rcToBox(self, *args, **kwargs)
            return StudentBoard.spaceToBox(self, *args, **kwargs)

        @property
        def valuesInRows(self):
            tester.set_plagiarism_flag()
            return self.valsInRows
        @valuesInRows.setter
        def valuesInRows(self, v):
            tester.set_plagiarism_flag()
            self.valsInRows = v
        @property
        def valuesInCols(self):
            tester.set_plagiarism_flag()
            return self.valsInCols
        @valuesInCols.setter
        def valuesInCols(self, v):
            tester.set_plagiarism_flag()
            self.valsInCols = v
        @property
        def valuesInBoxes(self):
            tester.set_plagiarism_flag()
            return self.valsInBoxes
        @valuesInBoxes.setter
        def valuesInBoxes(self, v):
            tester.set_plagiarism_flag()
            self.valsInBoxes = v
    return CheckedBoard
