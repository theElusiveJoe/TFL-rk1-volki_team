from cfg.parser import CFG_Parser

def check_1(grammar):
    pass
    g1 = grammar.toCNF()
    print('G!:', g1)
    return g1.check_task_1()

def check_2(grammar):
    pass
    grammar.clean()
    return grammar.check_task_2()

def main():
    input_file = open("test.CFG", "r")
    output_file = open("result", "w")

    test = ""
    for line in input_file.readlines():
        test += line
    


    # grammar = CFG_Parser(test).parse_rules()
    # print(grammar)
    # grammar = grammar.clean()
    # print(grammar)
    # return

    try:
        grammar = CFG_Parser(test).parse_rules()
    except Exception as e:
        print(e)
        output_file.write('syntax error') 
        print('SYNTAX ERROR')
    else:
        # print(grammar)
        if check_1(grammar):
            output_file.write('regular')   
            print('REGULAR')
            return 
        elif check_2(grammar):
            output_file.write('non-regular')    
            print('NONREGULAR')     
            return
        else:
            output_file.write('unknown')    
            print('UNKNOWN')
            

if __name__ == "__main__":
    main()