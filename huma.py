from flask import Flask, request, jsonify
import re
import io
import contextlib
import ast   


from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def format_ast(node, indent=""):
    lines = []

    def add_line(label):
        lines.append(f"{indent}{label}")

    if isinstance(node, ast.Module):
        add_line("Module")
        for stmt in node.body:
            lines.append(format_ast(stmt, indent + "  "))
    elif isinstance(node, ast.Assign):
        add_line("Assign")
        targets = ", ".join([t.id for t in node.targets if isinstance(t, ast.Name)])
        lines.append(f"{indent}  targets: [{targets}]")
        lines.append(f"{indent}  value:")
        lines.append(format_ast(node.value, indent + "    "))
    elif isinstance(node, ast.Expr):
        add_line("Expr")
        lines.append(format_ast(node.value, indent + "  "))
    elif isinstance(node, ast.Call):
        add_line("Call")
        lines.append(f"{indent}  func:")
        lines.append(format_ast(node.func, indent + "    "))
        lines.append(f"{indent}  args:")
        for arg in node.args:
            lines.append(format_ast(arg, indent + "    "))
    elif isinstance(node, ast.Name):
        add_line(f"Name: {node.id}")
    elif isinstance(node, ast.Constant):
        add_line(f"Constant: {repr(node.value)}")
    elif isinstance(node, ast.Tuple):
        add_line("Tuple")
        for elt in node.elts:
            lines.append(format_ast(elt, indent + "  "))
    elif isinstance(node, ast.For):
        add_line("For")
        lines.append(f"{indent}  target:")
        lines.append(format_ast(node.target, indent + "    "))
        lines.append(f"{indent}  iter:")
        lines.append(format_ast(node.iter, indent + "    "))
        lines.append(f"{indent}  body:")
        for stmt in node.body:
            lines.append(format_ast(stmt, indent + "    "))
    elif isinstance(node, ast.BinOp):
        add_line(f"BinOp: {type(node.op).__name__}")
        lines.append(f"{indent}  left:")
        lines.append(format_ast(node.left, indent + "    "))
        lines.append(f"{indent}  right:")
        lines.append(format_ast(node.right, indent + "    "))
    elif isinstance(node, ast.AugAssign):
        add_line("AugAssign")
        lines.append(f"{indent}  target:")
        lines.append(format_ast(node.target, indent + "    "))
        lines.append(f"{indent}  op: {type(node.op).__name__}")
        lines.append(f"{indent}  value:")
        lines.append(format_ast(node.value, indent + "    "))
    else:
        add_line(type(node).__name__)

    return "\n".join(lines)


def code_to_ast(code: str) -> str:
    try:
        tree = ast.parse(code)
        return format_ast(tree)
    except Exception as e:
        return f"Error parsing AST: {str(e)}"
    
def parsing(command: str) -> str:
    command = command.lower().strip()


    # Print statement
    if "print" in command:
           # Special case: "print X N times"
        m = re.search(r'print\s+(.+?)\s+(\d+)\s+times', command)
        if m:
         text, count = m.groups()
         text = text.strip('"\'')  # Remove existing quotes if any
         return f'print(",".join(["{text}"] * {count}))'
        m = re.search(r'print\s+(.+)', command)
        if m:
            text = m.group(1)
            if not text.startswith(("'", '"')):  # Add quotes if not string literal
                text = f'"{text}"'
            return f'print({text})'

    # Arithmetic operations
    if any(op in command for op in ["add", "subtract", "multiply", "divide"]):
        m = re.search(r'(add|subtract|multiply|divide)\s+(-?\d+)\s+(?:and|from|by)?\s*(-?\d+)', command)
        if m:
            op, a, b = m.groups()
            a, b = int(a), int(b)
            if op == "add":
                return f"result = {a} + {b}\nprint(result)"
            elif op == "subtract":
                return f"result = {a} - {b}\nprint(result)"
            elif op == "multiply":
                return f"result = {a} * {b}\nprint(result)"
            elif op == "divide":
                return f"result = {a} / {b}\nprint(result)"

    # Palindrome check
    if "palindrome" in command:
        m = re.search(r'palindrome(?:\s+check)?\s+(?:for\s+)?(.+)', command)
        if m:
            text = m.group(1)
            return f"text = '{text}'\nprint('Palindrome' if text == text[::-1] else 'Not Palindrome')"

    # Armstrong number
    if "armstrong" in command:
        m = re.search(r'armstrong(?:\s+number)?(?:\s+check)?(?:\s+for)?\s*(\d+)', command)
        if m:
            num = int(m.group(1))
            return (
                f"num = {num}\n"
                f"sum = sum(int(d)**3 for d in str(num))\n"
                f"print('Armstrong' if num == sum else 'Not Armstrong')"
            )

    # Factorial
    if "factorial" in command:
        m = re.search(r'factorial\s+of\s+(\d+)', command)
        if m:
            n = int(m.group(1))
            return (
                f"n = {n}\n"
                f"fact = 1\n"
                f"for i in range(1, n+1):\n"
                f"    fact *= i\n"
                f"print(fact)"
            )

    # Prime number
    if "prime" in command:
        m = re.search(r'(?:is\s+)?(\d+)\s+(?:a\s+)?prime', command)
        if m:
            n = int(m.group(1))
            return (
                f"n = {n}\n"
                f"if n < 2:\n"
                f"    print('Not Prime')\n"
                f"else:\n"
                f"    for i in range(2, int(n**0.5)+1):\n"
                f"        if n % i == 0:\n"
                f"            print('Not Prime')\n"
                f"            break\n"
                f"    else:\n"
                f"        print('Prime')"
            )


    # Search in array
    if "search" in command and "array" in command:
        m = re.search(r'search\s+(-?\d+)\s+in\s+array\s+(.+)', command)
        if m:
            target, arr_str = m.groups()
            arr = list(map(int, re.findall(r'-?\d+', arr_str)))
            return (
                f"arr = {arr}\n"
                f"target = {target}\n"
                f"print('Found' if target in arr else 'Not Found')"
            )

    # Replace in array
    if ("replace" in command or "update" in command) and "array" in command:
        m = re.search(r'(?:replace|update)\s+(-?\d+)\s+(?:with|to)\s+(-?\d+)\s+in\s+array\s+(.+)', command)
        if m:
            old, new, arr_str = m.groups()
            arr = list(map(int, re.findall(r'-?\d+', arr_str)))
            return (
                f"arr = {arr}\n"
                f"arr = [{new} if x == {old} else x for x in arr]\n"
                f"print(arr)"
            )



    # If-Else Condition
    if "if" in command and "print" in command and "else" in command:
        condition_match = re.search(r'if (.+?) print (.+?) else print (.+)', command)
        if condition_match:
            condition_text, out1, out2 = condition_match.groups()
            replacements = {
                "is equal to": "==",
                "is not equal to": "!=",
                "is greater than or equal to": ">=",
                "is less than or equal to": "<=",
                "is greater than": ">",
                "is less than": "<"
            }

            for phrase, operator in sorted(replacements.items(), key=lambda x: -len(x[0])):
                condition_text = condition_text.replace(phrase, operator)

            return (
                f"if {condition_text.strip()}:\n"
                f"    print('{out1.strip()}')\n"
                f"else:\n"
                f"    print('{out2.strip()}')"
            )

    # Print statement
    if command.startswith("print"):
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
    
      # Modulo operation
    if "modulo" in command:
     match = re.search(r'find (\-?\d+)\s*(?:modulo|mod)\s*(\-?\d+)', command)
     if match:
        a, b = map(int, match.groups())
        return (
            f"result = {a} % {b}\n"
            f"print('Result:', result)"
        )
     
     #divisibility
     
    if "divisible by both" in command:
       match = re.search(r'check if (\d+) is divisible by both (\d+) and (\d+)', command)
    if match:
        num, div1, div2 = map(int, match.groups())
        return f"print({num} % {div1} == 0 and {num} % {div2} == 0)"

    if re.search(r'print numbers starting from (\d+) up to (\d+)', command):
      m = re.search(r'print numbers starting from (\d+) up to (\d+)', command)
      start, end = map(int, m.groups())
      return f"for i in range({start}, {end+1}):\n    print(i)"

# Power operation
    if "power" in command:
     match = re.search(r'find (\-?\d+)\s*(?:to the power of|to the power|power)\s*(\-?\d+)', command)
     if match:
        base, exp = map(int, match.groups())
        return (
            f"result = {base} ** {exp}\n"
            f"print('Result:', result)"
        )
    if re.search(r'(print|say|output) \'(.+?)\' (?:\d+|ten|five|six|seven|eight|nine|eleven|twelve) times?', command):
     match = re.search(r'(?:print|say|output) \'(.+?)\' (\w+) times?', command)
    if match:
        text, count = match.groups()
        num_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12
        }
        count = num_words.get(count, count)
        return f"for _ in range({count}):\n    print('{text}')"


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
    # Defensive check: if no numbers found, handle gracefully
     if not nums:
        return "print('No numbers found to sort.')"
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
    
    # While loop
    if "while" in command and "print" in command:
        match = re.search(r'while (.+?) print (.+)', command)
        if match:
            condition_text, out = match.groups()
            replacements = {
                "is equal to": "==",
                "is not equal to": "!=",
                "is greater than or equal to": ">=",
                "is less than or equal to": "<=",
                "is greater than": ">",
                "is less than": "<"
            }
            for phrase, op in sorted(replacements.items(), key=lambda x: -len(x[0])):
                condition_text = condition_text.replace(phrase, op)

            var_match = re.search(r'([a-zA-Z_]\w*)\s*[<>=!]', condition_text)
            var = var_match.group(1) if var_match else "i"

            increment_match = re.search(r'increment by (\d+)', command)
            decrement_match = re.search(r'decrement by (\d+)', command)
            step = int(increment_match.group(1)) if increment_match else -int(decrement_match.group(1)) if decrement_match else 1
            op = '+' if step > 0 else '-'

            return (
                f"{var} = 0\n"
                f"while {condition_text.strip()}:\n"
                f"    print('{out.strip()}')\n"
                f"    {var} {op}= {abs(step)}"
            )

#if-elif-else block
    if "if" in command and "elif" in command and "else" in command and "print" in command:
        match = re.search(r'if (.+?) print (.+?) elif (.+?) print (.+?) else print (.+)', command)
        if match:
            cond1, out1, cond2, out2, out3 = match.groups()
            replacements = {
                "is equal to": "==",
                "is not equal to": "!=",
                "is greater than or equal to": ">=",
                "is less than or equal to": "<=",
                "is greater than": ">",
                "is less than": "<"
            }
            for phrase, op in sorted(replacements.items(), key=lambda x: -len(x[0])):
                cond1 = cond1.replace(phrase, op)
                cond2 = cond2.replace(phrase, op)

            return (
                f"if {cond1.strip()}:\n"
                f"    print('{out1.strip()}')\n"
                f"elif {cond2.strip()}:\n"
                f"    print('{out2.strip()}')\n"
                f"else:\n"
                f"    print('{out3.strip()}')"
            )
        
        #even-odd block
    if "check if" in command and "is even" in command:
        num = int(re.search(r'\d+', command).group())
        return f"print({num} % 2 == 0)"

    if "check if" in command and "is odd" in command:
        num = int(re.search(r'\d+', command).group())
        return f"print({num} % 2 != 0)"
    
    if re.search(r'if (.+?) print \'(.+?)\';? if (.+?) print \'(.+?)\'', command):
     match = re.search(r'if (.+?) print \'(.+?)\';? if (.+?) print \'(.+?)\'', command)
     cond1, out1, cond2, out2 = match.groups()
     return (
        f"if {cond1.strip()}:\n"
        f"    print('{out1.strip()}')\n"
        f"elif {cond2.strip()}:\n"
        f"    print('{out2.strip()}')"
    )

    
    #factorial block
    if "factorial" in command:
        num = int(re.search(r'\d+', command).group())
        return (
            f"def factorial(n):\n"
            f"    return 1 if n == 0 else n * factorial(n - 1)\n"
            f"print(factorial({num}))"
        )

#fibonacci series block
    if "fibonacci" in command and "terms" in command:
        num = int(re.search(r'\d+', command).group())
        return (
            f"a, b = 0, 1\n"
            f"for _ in range({num}):\n"
            f"    print(a)\n"
            f"    a, b = b, a + b"
        )

#occurence
    if "count" in command and "in array" in command:
        match = re.search(r'count (\d+) in array (.+)', command)
        if match:
            target, arr_str = match.groups()
            arr = list(map(int, re.findall(r'\d+', arr_str)))
            return f"arr = {arr}\nprint(arr.count({target}))"
        
#min-max block
    if "find max in array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"arr = {nums}\nprint(max(arr))"

    if "find min in array" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"arr = {nums}\nprint(min(arr))"
    
    #string length block
    if "find length of string" in command:
        match = re.search(r'string (\w+)', command)
        if match:
            s = match.group(1)
            return f"print(len('{s}'))"

#replace in string block
    if "replace" in command and "in string" in command:
        match = re.search(r'replace (\w) with (\w) in string (\w+)', command)
        if match:
            old, new, s = match.groups()
            return f"s = '{s}'\nprint(s.replace('{old}', '{new}'))"


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
            arr = list(map(int, re.findall(r'-?\d+', arr_str)))
            return (
                f"arr = {arr}\n"
                f"arr = [ {new} if x == {old} else x for x in arr ]\n"
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
    ast_output = code_to_ast(generated_code)
    
    return jsonify({
        'generated_code': generated_code,
        'output': output,
        'ast': ast_output
    })

if __name__ == "__main__":
    app.run(debug=True)  
