from .dhelper import *
import pytest

class TestMatrix:
    @pytest.fixture
    def matrix(self):
        return MatrixA([
            [1, 0, 3],
            [-4, 5, 0.1]
        ])

    def testEqual(self, matrix):
        assert matrix.equals([
            [1, 0, 3],
            [-4, 5, 0.1]
        ])

    def testNotEqual(self, matrix):
        assert not matrix.equals([
            [1, 0, 3, 0],
            [-4, 5, 0.1, 2]
        ])

class TestMatrixA:
    @pytest.fixture
    def matrix1(self):
        return MatrixA([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])

    def testAgreeable(self, matrix1):
        assert matrix1.isAgreeable()

    #TODO: стоило бы придумать несогласованную матрицу и проверить ее
    @pytest.mark.skip     
    def testNotAgreeable(self, matrix2):
        pass

class TestNet:
    @pytest.fixture
    def facA(self):
        return Factor("Price")

    @pytest.fixture
    def facB(self):
        return Factor("Power")
    
    @pytest.fixture
    def altA(self):
        return Alternative('Executor')
    
    @pytest.fixture
    def altB(self):
        return Alternative('Emperor II')

    @pytest.fixture
    def altC(self):
        return Alternative('Venator')

    @pytest.fixture
    def net(self, facA, facB, altA, altB, altC):
        net = Net(alternatives=[altA, altB, altC], factors=[facA, facB])
        
        net.setFactorCompare(facA, facB, 0)

        net.setAltCompare(facA, altA, altB, 2, False)
        net.setAltCompare(facA, altA, altC, 4, False)
        net.setAltCompare(facA, altB, altC, 2, False)

        net.setAltCompare(facB, altA, altB, 1 / 3, False)
        net.setAltCompare(facB, altA, altC, 1 / 5, False)
        net.setAltCompare(facB, altB, altC, 1 / 3, False)

        return net

    def testGenerateAlternativeMatrixA(self, net, facA):
        matrix = net.generateAlternativeMatrixA(facA)
        assert matrix.equals([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])

    def testGenerateFactorMatrixA(self, net):
        matrix = net.generateFactorMatrixA()
        assert matrix.equals([
            [1, 1],
            [1, 1]
        ])

    def testDecide(self, net, altA, altB, altC):
        expected = Decision({
            altA: 0.339,
            altB: 0.273,
            altC: 0.388
        })
        real = net.decide(roundDigits=3)
        assert real.equals(expected)

    def testAlternativeIterator(self, net, altA, altB, altC):
        it = net.getAlternativeIterator()
        count = 0
        for item in it:
            count += 1
            assert item == altA or item == altB or item == altC
        assert count == 3

    def testFactorIterator(self, net, facA, facB):
        it = net.getFactorIterator()
        count = 0
        for item in it:
            count += 1
            assert item == facA or item == facB
        assert count == 2

class TestNetCompareConverting:
    @pytest.fixture
    def factor1(self):
        return Factor("Price")

    @pytest.fixture
    def factor2(self):
        return Factor("Power")

    @pytest.fixture
    def alt1(self):
        return Alternative("Executor")

    @pytest.fixture
    def alt2(self):
        return Alternative("Emperor II")

    @pytest.fixture
    def net(self, factor1, alt1, alt2):
        return Net(alternatives=[alt1, alt2], factors=[factor1])

    def testNumberToProcent(self, net):
        start = net._numberToProcent(1/9)
        middle = net._numberToProcent(1)
        end = net._numberToProcent(9)
        assert start == -1 and middle == 0 and end == 1

    def testProcentToNumber(self, net):
        start = net._procentToNumber(-1)
        middle = net._procentToNumber(0)
        end = net._procentToNumber(1)
        assert start == 1 / 9 and middle == 1 and end == 9

    def testIncorrectLimitedNumberThrowsException(self, net):
        with pytest.raises(Exception):
            net._numberToProcent(0)

    def testNormalNumberCompare(self, net, factor1, alt1, alt2):
        net.setAltCompare(factor1, alt1, alt2, 7, isProcent=False)
        normalCompare = net.getAltCompare(factor1, alt1, alt2, isProcent=False)
        invertedCompare = net.getAltCompare(factor1, alt2, alt1, isProcent=False)
        assert normalCompare == 7 and invertedCompare == 1 / 7

    def testInvertedNumberCompare(self, net, factor1, alt1, alt2):
        net.setAltCompare(factor1, alt1, alt2, 1 / 7, isProcent=False)
        normalCompare = net.getAltCompare(factor1, alt1, alt2, isProcent=False)
        invertedCompare = net.getAltCompare(factor1, alt2, alt1, isProcent=False)
        assert normalCompare == 1 / 7 and invertedCompare == 7

    def testPositiveProcentCompare(self, net, factor1, alt1, alt2):
        net.setAltCompare(factor1, alt1, alt2, 0.7)
        normalCompare = net.getAltCompare(factor1, alt1, alt2)
        invertedCompare = net.getAltCompare(factor1, alt2, alt1)
        assert normalCompare == 0.7 and invertedCompare == -0.7

    def testNegativeProcentCompare(self, net, factor1, alt1, alt2):
        net.setAltCompare(factor1, alt1, alt2, -0.4)
        normalCompare = net.getAltCompare(factor1, alt1, alt2)
        invertedCompare = net.getAltCompare(factor1, alt2, alt1)
        assert normalCompare == -0.4 and invertedCompare == 0.4

    def testMixedCompare(self, net, factor1, alt1, alt2):
        net.setAltCompare(factor1, alt1, alt2, -0.25)
        normalNumberCompare = net.getAltCompare(factor1, alt1, alt2, isProcent=False)
        invertedProcentCompare = net.getAltCompare(factor1, alt2, alt1)
        assert normalNumberCompare == 1 / 3 and invertedProcentCompare == 0.25

    def testFactorCompare(self, net, factor1, factor2):
        net.setFactorCompare(factor1, factor2, 7, isProcent=False)
        procentNumberCompare = net.getFactorCompare(factor1, factor2)
        procentInvertedCompare = net.getFactorCompare(factor2, factor1)
        assert procentNumberCompare == 0.75 and procentInvertedCompare == -0.75
        
class TestDecision:
    @pytest.fixture
    def altA(self):
        return Alternative('Executor')
    
    @pytest.fixture
    def altB(self):
        return Alternative('Emperor II')

    @pytest.fixture
    def altC(self):
        return Alternative('Venator')

    @pytest.fixture
    def decision(self, altA, altB, altC):
        return Decision({
            altA: 0.339,
            altB: 0.273,
            altC: 0.388
        })

    def testSort(self, decision, altA, altB, altC):
        expected = [
            [altC, 0.388],
            [altA, 0.339],
            [altB, 0.273] 
        ]
        real = decision.sort()
        assert real == expected

    def testReverseSort(self, decision, altA, altB, altC):
        expected = [
            [altB, 0.273], 
            [altA, 0.339], 
            [altC, 0.388]
        ]
        real = decision.sort(reverse=True)
        assert real == expected