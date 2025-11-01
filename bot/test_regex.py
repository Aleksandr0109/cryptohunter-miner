# test_regex.py
import re

addr = "UQABC1234567890abcdef1234567890abcdef1234567890abc"
pattern = r"^[UEQ][A-Za-z0-9_-]{47,52}$"

if re.match(pattern, addr):
    print("REGEX РАБОТАЕТ! Адрес подходит.")
else:
    print("REGEX НЕ РАБОТАЕТ! Адрес НЕ подходит.")