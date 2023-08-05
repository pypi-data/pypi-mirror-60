"""Este é o módulo "fraimundnester1982.py.py", e fornece uma função chamada print_lol()
que impreme lista que podem ou não incluir listas aninhadas"""

def print_lol(the_list, level):
    """Está função requer um argumento posicional chamado "the_list", que  é
    qualquer lista Python (de possíveis listas aninhadas). Cada item de dados na
    list fornecida é (recursivamente) impresso na tela em sua própria linha
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end="")
            print(each_item)
