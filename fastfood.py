from cuisine import manager


import random
import asyncio

# import asyncio
# import random
# import sys
# from datetime import datetime
# from enum import Enum
# from dataclasses import dataclass


def main():
    random.seed()
    # nombre de commande à réaliser
    nb_cmd = 3
    # nombre de serveur
    nb_servers = 2
    # capacité de la friteuse en portion
    fryer_capacity = 4

    # simulation des arrivées clients (délai aléatoire pour chacun d'entre eux)
    delay = [random.randint(1, 50) / 10 for x in range(nb_cmd)]
    delay.sort()
    print("\n\ndélai d'arriver des clients en seconde : \n\t\t", delay)

    # initialisation de notre objet coroutine
    ffm = manager.FastFoodManager(nb_servers, fryer_capacity)

    # on passe les commandes (création des tâches dans la boucle d'événement)
    tasks = [ffm.nouvelle_commande(num_commande, delay[num_commande]) for num_commande in range(nb_cmd)]

    # ### ancienne méthode ###
    # for num_commande in range(nb_cmd):
    #     asyncio.ensure_future(ff.nv_commande(num_commande, delay[num_commande]))
    # on passe la tâche en charge de la fermeture (si pluys de commande)
    # asyncio.ensure_future(ff.on_ferme())

    try:
        # on lance la boucle

        # ### ancienne méthode ###
        # asyncio.get_event_loop().run_forever()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
        print("Plus personne ? on ferme !")
    except KeyboardInterrupt:
        print("Barrez-vous ! c'est fermé et tant pis pour vos comandes !")
    except Exception as e:
        print("OUPS", type(e), e)

if __name__ == "__main__":
    main()