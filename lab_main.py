from cfg.parser import CFG_Parser


def check_lab_3(grammar):
    print('\nГРАММАТИКА:')
    print(grammar)

    grammar = grammar.toCNF()

    print('\nГРАММАТИКА В ХНФ:')
    print(grammar)

    is_suitable = grammar.check_lab_3()
    print(is_suitable, '- подходит ли')

    for m in grammar.mureses2:
        print('\n\n-------CHECKING IDEMPOTENCY-------\n\n')
        print(m)
        m.check_idempotence()
    # print('\nНАЙДЕНЫ МЮРЕСЫ:')
    # for m in grammar.mureses2:
    #     print(m)
def main():
    with open("test.CFG", "r") as test_src:
        grammar = CFG_Parser(test_src.readlines()).parse_rules()
    
    check_lab_3(grammar)
    # if check_lab_3(grammar):
    #     print('NONREGULAR')
    # else:
    #     print('UNKNOWN')


if __name__ == "__main__":
    main()
