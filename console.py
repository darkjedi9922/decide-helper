#!/usr/bin/python3

import dhelper.base as dhelper
import itertools

def inputNumber(min=None, max=None, message=""):
    try:
        number = int(input(message))
        while min != None and number < min or max != None and number > max:
        #while number not in rangeObj:
            return inputNumber(min, max, "Некорректный номер. Введите снова: ")
    except Exception:
        return inputNumber(min, max, "Некорректный номер. Введите снова: ")
    return number

def menuAction():
    print("---- МЕНЮ ----")
    print("1. Добавить альтернативы")
    print("2. Добавить факторы")
    print("3. Показать список альтернатив")
    print("4. Показать список факторов")
    print("5. Установить отношения факторов")
    print("6. Установить отношения альтернатив")
    print("7. Расчитать")
    print("8. Выйти")
    try:
        number = inputNumber(1, 8, "Выберите действие (введите его номер): ")
        if number == 1:
            alternativeInputAction()
        elif number == 2:
            factorInputAction()
        elif number == 3:
            showAlternativesAction()
        elif number == 4:
            showFactorsAction()
        elif number == 5:
            setupFactors()
        elif number == 6:
            setupAlternatives()
        elif number == 7:
            decideAction()
        else:
            exitAction()
    except KeyboardInterrupt:
        exitAction()

def alternativeInputAction():
    print("---- ДОБАВЛЕНИЕ АЛЬТЕРНАТИВ ----")
    try:
        amount = inputNumber(0, message="Количество: ")
        for i in range(amount):
            name = input("Имя альтернативы " + str(i + 1) + ": ")
            net.addAlternative(dhelper.Alternative(name))
    except KeyboardInterrupt:
        pass
    finally:
        menuAction()

def factorInputAction():
    print("---- ДОБАВЛЕНИЕ ФАКТОРОВ ----")
    try:
        amount = inputNumber(0, message="Количество: ")
        for i in range(amount):
            name = input("Имя фактора " + str(i + 1) + ": ")
            net.addFactor(dhelper.Factor(name))
    except KeyboardInterrupt:
        pass
    finally:
        menuAction()

def showAlternativesAction():
    print("---- СПИСОК АЛЬТЕРНАТИВ ----")
    for alt in net.getAlternativeIterator():
        print(alt.getName())
    menuAction()

def showFactorsAction():
    print("---- СПИСОК ФАКТОРОВ ----")
    for factor in net.getFactorIterator():
        print(factor.getName())
    menuAction()

def setupFactors():
    print("---- ОТНОШЕНИЯ ФАКТОРОВ ----")
    try:
        message = "Для ввода в процентах (от 0 до 1) введите 1, для ввода в числах введите 0: "
        isProcent = bool(inputNumber(0, 1, message))
        combinations = itertools.combinations(net.getFactorIterator(), 2)
        for comb in combinations:
            message = comb[0].getName() + " vs " + comb[1].getName() + ": "
            compare = float(input(message))
            net.setFactorCompare(comb[0], comb[1], compare, isProcent)
    except KeyboardInterrupt:
        pass
    finally:
        menuAction()    

def setupAlternatives():
    print("---- ОТНОШЕНИЯ АЛЬТЕРНАТИВ ----")
    try:
        message = "Для ввода в процентах (от 0 до 1) введите 1, для ввода в числах введите 0: "
        isProcent = bool(inputNumber(0, 1, message))
        for factor in net.getFactorIterator():
            alterCombinations = itertools.combinations(net.getAlternativeIterator(), 2)
            for comb in alterCombinations:
                message = comb[0].getName() + " vs " + comb[1].getName()
                message += " по фактору " + factor.getName() + ": "
                compare = float(input(message))
                net.setAltCompare(factor, comb[0], comb[1], compare, isProcent)
    except KeyboardInterrupt:
        pass
    finally:
        menuAction()    

def decideAction():
    print("---- РЕШЕНИЕ ----")
    decision = net.decide()
    print("Список альтернативв от лучшей к худшей с вычисленной оценкой:")
    for item in decision.sort():
        print(item[0].getName() + ": " + str(item[1]))
    menuAction()

def exitAction():
    print("---- ВЫХОД ----")
    exit()

net = dhelper.Net()
menuAction()