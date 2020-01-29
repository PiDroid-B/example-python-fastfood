from cuisine import manager


import random
import asyncio
import logging


def get_logger():
    local_log = logging.getLogger()
    local_log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        '%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    local_log.addHandler(handler)

    return local_log


def main():
    random.seed()
    # nombre de commande à réaliser
    nb_cmd = 10
    # nombre de serveur
    nb_servers = 2
    # capacité de la friteuse en portion
    fryer_capacity = 4

    log.debug(f"Parameters : nb_cmd({nb_cmd}) nb_servers({nb_servers}) fryer_capacity({fryer_capacity})")

    # simulation des arrivées clients (délai aléatoire pour chacun d'entre eux)
    delay = [random.randint(1, 50) / 10 for x in range(nb_cmd)]
    delay.sort()
    print("\n\ndélai d'arriver des clients en secondes : \n\t\t", delay)

    # initialisation de notre objet coroutine
    ffm = manager.FastFoodManager(nb_servers, fryer_capacity, nb_cmd)

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
        log.info(f"Run event loop with {nb_cmd} commands")
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
        print("Plus personne ? on ferme !")
    except KeyboardInterrupt:
        print("Barrez-vous ! c'est fermé et tant pis pour vos comandes !")
    except Exception as e:
        print("OUPS", type(e), e)
        raise e


if __name__ == "__main__":
    log = get_logger()

    log.info("FastFood is opened !")
    main()
    log.info("FastFood is closed !")
