def vulnerable_function():
    user_input = input("math: ") 

    result = eval(user_input)#vul 
    print("result:", result)

if __name__ == "__main__":
    vulnerable_function()
    