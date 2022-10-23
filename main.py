from cfg.parser import CFG_Parser

def main():
    input_file = open("test.CFG", "r")
    output_file = open("result", "w")

    test = ""
    for line in input_file.readlines():
        test += line
    
    try:
        grammar = CFG_Parser(test).parse_rules()
    except Exception as e:
        print(e)
        output_file.write('syntax error') 
        print('SYNTAX ERROR')
    else:
        grammar.clean()

        # проверяю первый
        g1 = grammar.toCNF()

        # print(g1)
        if g1.check_task_1():
            output_file.write('regular')    
            print('REGULAR')
        
        else:
            output_file.write('unknown')    
            print('UNKNOWN')

if __name__ == "__main__":
    main()