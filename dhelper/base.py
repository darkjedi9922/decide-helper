import numpy as np

class Alternative:
    def __init__(self, name):
        self.setName(name)

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

class Factor(Alternative):
    pass

class Net:
    def __init__(self, alternatives=[], factors=[]):
        self._alternatives = alternatives
        self._factors = factors

        # Все сравнения хранятся в числах в промежутке [0;9].
        # compares[factor][alterntaiveA][alternativeB] или
        # compares[None][factorA][factorB], где каждый элемент - объект.
        self._compares = {}

    def addFactor(self, factor):
        self._factors.append(factor)

    def addFactors(self, factors):
        self._factors.extend(factors)

    def getFactorIterator(self):
        return iter(self._factors)

    def hasFactor(self, factor):
        return factor in self._factors

    def addAlternative(self, alternative):
        self._alternatives.append(alternative)

    def addAlternatives(self, alternatives):
        self._alternatives.extend(alternatives)

    def getAlternativeIterator(self):
        return iter(self._alternatives)

    def hasAlternative(self, alt):
        return alt in self._alternatives

    def setAltCompare(self, factor, alt1, alt2, compare, isProcent=True):
        if factor not in self._compares:
            self._compares[factor] = {}
        if alt1 not in self._compares[factor]:
            self._compares[factor][alt1] = {}
        if alt2 not in self._compares[factor]:
            self._compares[factor][alt2] = {}
        if isProcent:
            compare = self._procentToNumber(compare)
        self._compares[factor][alt1][alt2] = compare
        self._compares[factor][alt2][alt1] = 1 / compare

    def getAltCompare(self, factor, alt1, alt2, isProcent=True):
        compare = 1 # 1 - числовое представление нейтрального сравнения (по-умолчанию)
        if factor in self._compares and alt1 in self._compares[factor]: 
            if alt2 in self._compares[factor][alt1]:
                compare = self._compares[factor][alt1][alt2]
        if isProcent:
            return self._numberToProcent(compare)
        return compare

    def setFactorCompare(self, factor1, factor2, compare, isProcent=True):
        self.setAltCompare(None, factor1, factor2, compare, isProcent=isProcent)
            
    def getFactorCompare(self, factor1, factor2, isProcent=True):
        return self.getAltCompare(None, factor1, factor2, isProcent=isProcent)

    def generateAlternativeMatrixA(self, factor):
        altLen = len(self._alternatives)
        matrix = [[1 for i in range(altLen)] for i in range(altLen)]
        for i in range(altLen):
            for j in range(altLen):
                if i != j:
                    altI = self._alternatives[i]
                    altJ = self._alternatives[j]
                    matrix[i][j] = self.getAltCompare(factor, altI, altJ, False)
        return MatrixA(matrix)

    def generateFactorMatrixA(self):
        facLen = len(self._factors)
        matrix = [[1 for i in range(facLen)] for i in range(facLen)]
        for i in range(facLen):
            for j in range(facLen):
                if i != j:
                    facI = self._factors[i]
                    facJ = self._factors[j]
                    matrix[i][j] = self.getFactorCompare(facI, facJ, False)
        return MatrixA(matrix)

    def decide(self, roundDigits=5):
        """
        :raises MatrixAgreeableError
        """
        factorMatrixA = self.generateFactorMatrixA()
        if not factorMatrixA.isAgreeable():
            raise MatrixAgreeableError(factorMatrixA)
        factorMatrixW = factorMatrixA.calcMatrixN().calcMatrixW()
        
        altMatrixesW = {}
        for factor in self._factors:
            altMatrixA = self.generateAlternativeMatrixA(factor)
            if not altMatrixA.isAgreeable():
                raise MatrixAgreeableError(altMatrixA)
            altMatrixesW[factor] = altMatrixA.calcMatrixN().calcMatrixW()

        decision = {}
        for i in range(len(self._alternatives)):
            alt = self._alternatives[i]
            decision[alt] = 0
            for j in range(len(self._factors)):
                altMatrixW = altMatrixesW[self._factors[j]]
                decision[alt] += factorMatrixW[j][0] * altMatrixW[i][0]
            decision[alt] = round(decision[alt], roundDigits)

        return Decision(decision)

    def _numberToProcent(self, compare):
        """
        :param float compare: Число в пределах (0;9]
        :return float: Процент в пределах [-1;1]
        :raise Exception: Если число задано в неправильных пределах
        """
        if compare > 0 and compare < 1:
            return -self._numberToProcent(1 / compare)
        elif compare >= 1 and compare <= 9:
            return (compare - 1) / 8
        raise Exception

    def _procentToNumber(self, compare):
        """
        :param float compare: Процент в пределах [-1;1]
        :return float: Число в пределах (0;9]
        :raise Exception: Если процент задан в неправильных пределах
        """
        if compare >= -1 and compare < 0:
            return 1 / self._procentToNumber(-compare)
        elif compare >= 0 and compare <= 1:
            return 8 * compare + 1
        raise Exception

class Decision:
    def __init__(self, decision):
        """
        :param {Alternative: float} Dictionary "alternative - valuate"
        """
        self._decision = decision

    def equals(self, decision):
        """
        :param {Alternative: float} Dictionary "alternative - valuate"
        :return bool
        """
        selfKeys = self._decision.keys()
        if len(decision._decision.keys()) != len(selfKeys):
            return False
        for key in selfKeys:
            if self._decision[key] != decision._decision[key]:
                return False
        return True

    def sort(self, reverse=False):
        """
        :return [{Alternative: float}] sorted from larger to smaller
        """
        sortedAlternatives = []
        items = self._decision.items()
        sortKey = lambda args: args[1]
        for key, value in sorted(items, key=sortKey, reverse=not reverse):
            sortedAlternatives.append([key, value])
        return sortedAlternatives

class Matrix:
    def __init__(self, matrix):
        self._matrix = np.array(matrix)
        
    def sumColumn(self, index):
        result = 0
        for i in range(len(self._matrix)):
            result += self._matrix[i][index]
        return result

    def countRows(self):
        return len(self._matrix)

    def countColumns(self):
        try:
            return len(self._matrix[0])
        except Exception:
            return 0

    def __getitem__(self, key):
        return self._matrix[key]

    def equals(self, matrix):
        selfLen = len(self._matrix)
        if selfLen != len(matrix):
            return False
        for i in range(selfLen):
            if len(self._matrix[i]) != len(matrix[i]):
                return False
            for j in range(len(self._matrix[i])):
                if self._matrix[i][j] != matrix[i][j]:
                    return False
        return True

class MatrixA(Matrix):
    def calcMatrixN(self):
        result = []
        for i in range(len(self._matrix)):
            newLine = []
            for j in range(len(self._matrix[i])):
                newLine.append(self._matrix[i][j] / self.sumColumn(j))
            result.append(newLine)
        return MatrixN(result)

    def isAgreeable(self):
        n = self.countRows()
        if n <= 2:
            return True
        nMax = self.calcMatrixN().calcMatrixW().calcNMax()
        ci = (nMax - n) / (n - 1)
        ri = 1.98 * (n - 2) / n
        cr = ci / ri
        return cr <= 0.1

class MatrixN(Matrix):
    def calcMatrixW(self):
        result = []
        for line in self._matrix:
            result.append([sum(line) / len(line)])
        return MatrixW(result)

class MatrixW(Matrix):
    def calcNMax(self):
        return self.sumColumn(0)

class MatrixAgreeableError(Exception):
    def __init__(self, matrix):
        self._matrix = matrix

    def getMatrix(self):
        return self._matrix