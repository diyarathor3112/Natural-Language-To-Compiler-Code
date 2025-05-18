from flask import Flask, request, jsonify
import re
import io
import contextlib
from flask_cors import CORS
                          
app = Flask(__name__)
CORS(app)   

def parsing(command: str) -> str:
    command = command.lower().strip()

    # print statement
    if "print" in command:
      msg = command[6:].strip()
      return f'print("{msg}")'

    # Arithmetic
    if "add" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} + {nums[1]})"

    elif "subtract" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} - {nums[1]})"

    elif "multiply" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} * {nums[1]})"

    elif "divide" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} / {nums[1]})"

    # If-Else Condition
    if "if" in command and "print" in command and "else" in command:
        condition_match = re.search(r'if (.+?) print (.+?) else print (.+)', command)
        if condition_match:
            condition_text, out1, out2 = condition_match.groups()
            condition_text = condition_text.replace("is equal to", "==").replace("is not equal to", "!=")
            condition_text = condition_text.replace("is greater than or equal to", ">=").replace("is less than or equal to", "<=")
            condition_text = condition_text.replace("is greater than", ">").replace("is less than", "<")
            return (
                f"if {condition_text.strip()}:\n"
                f"    print('{out1.strip()}')\n"
                f"else:\n"
                f"    print('{out2.strip()}')"
            )

    # Print text multiple times
    if "print" in command and "times" in command:
        match = re.search(r'print (.+?) (\d+) times', command)
        if match:
            text, count = match.groups()
            return f"for _ in range({count}):\n    print('{text}')"

    # Print numbers in range
    if "print numbers from" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        if len(nums) >= 2:
            return f"for i in range({nums[0]}, {nums[1] + 1}):\n    print(i)"

    # Sort array
    if "sort" in command and "array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"arr = {nums}\narr.sort()\nprint(arr)"

    # Sort string
    if "sort" in command and "string" in command:
        match = re.search(r'string (\w+)', command)
        if match:
            s = match.group(1)
            return f"s = '{s}'\nsorted_s = ''.join(sorted(s))\nprint(sorted_s)"

    # Search
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
                return f"arr = {arr}\nprint({target} in arr)"

    # Sum of array
    if "sum" in command and "array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"arr = {nums}\nprint(sum(arr))"

    # Reverse array
    if "reverse" in command and "array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"arr = {nums}\narr.reverse()\nprint(arr)"

    # Armstrong number
    if "armstrong" in command and re.search(r'\d+', command):
        num = int(re.search(r'\d+', command).group())
        return (
            f"num = {num}\n"
            f"def is_armstrong(n):\n"
            f"    digits = [int(d) for d in str(n)]\n"
            f"    power = len(digits)\n"
            f"    return sum([d ** power for d in digits]) == n\n"
            f"print(is_armstrong(num))"
        )

    # Palindrome number
    if "palindrome" in command and re.search(r'\d+', command):
        num = int(re.search(r'\d+', command).group())
        return (
            f"num = {num}\n"
            f"def is_palindrome(n):\n"
            f"    return str(n) == str(n)[::-1]\n"
            f"print(is_palindrome(num))"
        )

    # Replace in array
    if ("replace" in command or "update" in command) and "array" in command:
        m = re.search(r'(?:replace|update) (-?\d+) (?:with|to) (-?\d+) in array (.+)', command)
        if m:
            old, new, arr_str = m.groups()
            old, new = int(old), int(new)
            arr = list(map(int, re.findall(r'-?\d+', arr_str)))
            return (
                f"arr = {arr}\n"
                f"arr = [{new} if x == {old} else x for x in arr]\n"
                f"print(arr)"
            )
            
    # Delete from array
    if "delete" in command and "array" in command:
        match = re.search(r'delete (-?\d+) from array (.+)', command)
        if match:
            val_str, arr_str = match.groups()
            val = int(val_str)
            arr = list(map(int, re.findall(r'-?\d+', arr_str)))
            filtered_arr = [x for x in arr if x != val]
            return (
                f"arr = {filtered_arr}\n"
                f"print(arr)"
            )

    # Fallback
    return "print('Sorry, I did not understand the command.')"

def execute_code(code: str) -> str:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code)
        return buffer.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/parse_execute', methods=['POST'])
def parse_execute():
    data = request.json
    command = data.get('command', '')
    generated_code = parsing(command)
    output = execute_code(generated_code)
    return jsonify({
        'generated_code': generated_code,
        'output': output
    })

if __name__ == "__main__":
    app.run(debug=True)
