from cfg.parser import CFG_Parser
import uuid


def parse():
    with open("test.CFG", "r") as test_src:
        return CFG_Parser(test_src.readlines()).parse_rules()

    regular_approximation(grammar)


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


def regular_approximation(grammar):
    print('ИСХОДНАЯ ГРАММАТИКА')
    print(grammar)
    grammar = grammar.toCNF().clean()
    print('В НФХ') 
    print(grammar)
    grammar = grammar.remove_all_right_productions(debug=True)
    print('ПОСЛЕ УДАЛЕНИЯ ВСЕХ ПРАВЫХ ПЕРЕХОДОВ')
    print(grammar)
    grammar.clean()
    print('И ЕЩЕ УПРОСТИТЬ МОЖНО')
    print(grammar)
    return grammar



def main():
    grammar = parse()
    
    regular_approximation(grammar)

    # for m in grammar.mureses2:
    #     name_appendix = '_' + uuid.uuid4().hex[:3].upper()
    #     print(m.get_fresh_renamed_copy_of_mn_transformation(name_appendix=name_appendix))
    
    # check_lab_3(grammar)
    # if check_lab_3(grammar):
    #     print('NONREGULAR')
    # else:
    #     print('UNKNOWN')


if __name__ == "__main__":
    main()


