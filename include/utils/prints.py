from colorama import Fore, Style, init
import sys

init(autoreset=True)

sys.stdout.reconfigure(encoding='utf-8')

# Prints
def println(text):
    print(Fore.LIGHTYELLOW_EX + "[ VAC ] " + str(text))

def printOk(text):
    print(Fore.LIGHTGREEN_EX + "[ VAC ] " + str(text))

def printNotOk(text):
    print(Fore.LIGHTRED_EX + "[ VAC ] " + str(text))

# Inputs
def inputln(prompt):
    return input(Fore.LIGHTYELLOW_EX + "[ VAC ] " + str(prompt))

def inputOk(prompt):
    return input(Fore.LIGHTGREEN_EX + "[ VAC ] " + str(prompt))

def inputNotOk(prompt):
    return input(Fore.LIGHTRED_EX + "[ VAC ] " + str(prompt))
