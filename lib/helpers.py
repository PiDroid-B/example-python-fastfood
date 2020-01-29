import sys


def print_headers(tick, nb_cmd):
    """
    # Etnete de état de la commande pour chaque client
    """
    # taille d'une ligne (hors préfixe d'horodatage)
    raw_len = nb_cmd * 4 + 1
    # espace qui sera utilisé pour afficher les temps d'exécution
    prefix_time = "\n" + " " * 14
    # legende
    legende = "(B)urger  | (F)rites | (S)oda | + Ask | o In Progress | - Get"
    # header 1 : colonnes de 3 chr : id par client
    hd1 = "|" + "|".join(map(str, [f"{x:^3}" for x in range(0, nb_cmd )])) + "|"
    # header 2 : sous-colonnes Burger/Frites/Soda par client
    hd2 = "|BFS" * nb_cmd + "|"
    # header 3 : ligne vide pour timer
    hd3 = "  |" + "|".join(map(str, [f"   "] * nb_cmd)) + "|"
    # concat header
    raw = prefix_time + f"{legende:^{raw_len}}" + \
        prefix_time + hd1 + \
        prefix_time + hd2 + \
        prefix_time + "=" * raw_len + \
        "\n" + tick + hd3

    print(raw)


def print_line(tick, cmd_clients, last_comment=""):
    # Etat de la commande pour chaque client
    # en colonnes : (B)urger  | (F)rites | (S)oda
    try:
        raw = tick + "  |" + "|".join(map(str, cmd_clients)) + '|' + last_comment
    except Exception as e:
        print(type(e), e)
        raise e

    print(raw)
