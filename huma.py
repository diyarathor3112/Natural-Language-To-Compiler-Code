import re
import io
import contextlib

# Function that will parse the sentence
def parsing(command: str) -> str:
    command = command.lower().strip()

    # Arithmetic operations
    if "add" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({'+'.join(map(str, nums))})"

    elif "subtract" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} - {nums[1]})"

    elif "multiply" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} * {nums[1]})"

    elif "divide" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        return f"print({nums[0]} / {nums[1]})"

    # Nested Conditional with else and comparison
    elif "if" in command and "else" in command and "print" in command:
        match = re.search(r'if (\d+)\s+is\s+(greater|less)\s+than\s+(\d+)\s+print\s+(\w+)\s+else\s+print\s+(\w+)', command)
        if match:
            num1, comparator, num2, out1, out2 = match.groups()
            op = ">" if comparator == "greater" else "<"
            return (
                f"if {num1} {op} {num2}:\n"
                f"    print('{out1}')\n"
                f"else:\n"
                f"    print('{out2}')"
            )

    # Print greater number among X and Y
    elif "greater number among" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
            return (
                f"if {a} > {b}:\n"
                f"    print({a})\n"
                f"else:\n"
                f"    print({b})"
            )
            # Advanced nested conditionals with logical operators
    elif "if" in command and "print" in command and "else" in command:
        # Examples:
        # "if 10 is equal to 10 and 5 is less than 6 print yes else print no"
        condition_match = re.search(r'if (.+) print (\w+) else print (\w+)', command)
        if condition_match:
            condition_text, out1, out2 = condition_match.groups()

            # Replace human words with Python operators
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
                f"    print('{out1}')\n"
                f"else:\n"
                f"    print('{out2}')"
            )


    # Loop: print "hello" 5 times
    if "print" in command and "times" in command:
     match = re.search(r'print (.+?)\s+(\d+)\s+times', command)
    if match:
        text, count = match.groups()
        return f"for _ in range({count}):\n    print('{text}')"


    # Loop: print numbers from X to Y
    elif "print the numbers from" in command or "print numbers from" in command:
        nums = list(map(int, re.findall(r'\d+', command)))
        if len(nums) >= 2:
            start, end = nums[0], nums[1]
            return f"for i in range({start}, {end + 1}):\n    print(i)"

    # Character frequency analysis
    elif "size of string" in command and ("find repeating" in command or "find non repeating" in command):
        match = re.search(r'size of string (\w+)', command)
        if match:
            word = match.group(1)
            code = (
                f"from collections import Counter\n"
                f"s = '{word}'\n"
                f"counter = Counter(s)\n"
                f"for char, count in counter.items():\n"
            )
            if "non repeating" in command and "repeating" in command:
                code += (
                    f"    if count == 1:\n"
                    f"        print(f'{{char}} is non-repeating')\n"
                    f"    elif count > 1:\n"
                    f"        print(f'{{char}} appears {{count}} times')"
                )
            elif "non repeating" in command:

                code += (
                    f"    if count == 1:\n"
                    f"        print(f'{{char}} is non-repeating')"
                )
            else:  # only repeating
                code += (
                    f"    if count > 1:\n"
                    f"        print(f'{{char}} appears {{count}} times')"
                )
            return code

    # Fallback
    return "print('Sorry, I did not understand the command.')"

# Function to execute generated code safely
def execute_code(code: str) -> str:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code)
        return buffer.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"

# Main interaction loop
if __name__ == "__main__":
    while True:
     user_input = input("Enter a natural language instruction: ")
     generated_code = parsing(user_input)
     output = execute_code(generated_code)

     print("\nGenerated Python Code:")
     print(generated_code)
     print("Output:")
     print(output)
