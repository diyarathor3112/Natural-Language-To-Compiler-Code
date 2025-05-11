import re
import io
import contextlib
from typing import Optional

#function for parsing the sentence
def parsing(command->str)->str:
    command=command.lower().strip()
    #Arithmetic Operations Handled
if "add" in command:
 nums=list(map(int, re.findall(r'\d+',command)))
 return f"print({nums[0]}+{nums[1]})"

if "subtract" in command:
 nums=list(map(int, re.findall(r'\d+',command)))
 return f"print({nums[0]}-{nums[1]})"

if "multiply" in command:
 nums=list(map(int, re.findall(r'\d+',command)))
 return f"print({nums[0]}*{nums[1]})"

if "divide" in command:
 nums=list(map(int, re.findall(r'\d+',command)))
 return f"print({nums[0]}/{nums[1]})"

#If-Else Condition Handling
if "if" in command and "print" in command and "else" in command:
 condition_match = re.search(r'if (.+?) print (.+?) else print (.+)', command)
    if condition_match:
        condition_text, out1, out2 = condition_match.groups()
        condition_text = condition_text.replace("is equal to", "==")
         condition_text = condition_text.replace("is not equal to", "!=")
        condition_text = condition_text.replace("is greater than or equal to", ">=")
        condition_text = condition_text.replace("is less than or equal to", "<=")
         condition_text = condition_text.replace("is greater than", ">")
        condition_text = condition_text.replace("is less than", "<")
        condition_text = condition_text.replace(" and ", " and ")
        condition_text = condition_text.replace(" or ", " or ")

            return (
                f"if {condition_text.strip()}:\n"
                f"    print('{out1.strip()}')\n"
                f"else:\n"
                f"    print('{out2.strip()}')"
            )

 # Loop (string)
    if "print" in command and "times" in command:
        match = re.search(r'print (.+?) (\d+) times', command)
        if match:
            text, count = match.groups()
            return f"for _ in range({count}):\n    print('{text}')"

    # Loop (integer)
    if "print numbers from" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        if len(nums) >= 2:
            return f"for i in range({nums[0]}, {nums[1]+1}):\n    print(i)"

    # Sorting Array
    if "sort" in command and "array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return (
            f"arr = {nums}\n"
            f"arr.sort()\n"
            f"print(arr)"
        )

    # Sorting String
    if "sort" in command and "string" in command:
        match = re.search(r'string (\w+)', command)
        if match:
            s = match.group(1)
            return (
                f"s = '{s}'\n"
                f"sorted_s = ''.join(sorted(s))\n"
                f"print(sorted_s)"
            )

    # Searching 
    if "search" in command:
        if "in string" in command:
            match = re.search(r'search (\w+) in string (\w+)', command)
            if match:
                word, string = match.groups()
                return f"print('{word}' in '{string}')"
        elif "in array" in command:
            match = re.search(r'search (\d+) in array (.+)', command)
            if match:
                target, arr_str = match.groups()
                arr = list(map(int, re.findall(r'\d+', arr_str)))
                return (
                    f"arr = {arr}\n"
                    f"print({target} in arr)"
                )

    # Sentence Error
    return "print('Sorry, I did not understand the command.')"

# Function for Execution (Output)
def execute_code(code: str) -> str:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code)
        return buffer.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"


#Main function where input will be taken
if __name__=="__main__":
    while True:
        sentence=input("\nEnter The Sentence In English : ")
code_gen=parsing(sentence)
result=execute(code_gen)
print("\Generated Code Is : ")
print("code_gen")
print("\nResult : ")
print(result)
