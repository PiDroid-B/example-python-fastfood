# Fast food :

Inspiré de :  [ZestDeSavoir.com](https://zestedesavoir.com/articles/1568/decouvrons-la-programmation-asynchrone-en-python/)

On ne va pas attendre que la première commande soit servie pour prendre la deuxième

## Pour chaque commande d'un menu (définition de ZestDeSavoir) :

### burger :  
Il n'y a que 3 cuisiniers.  
On ne peut pas faire plus de 3 burgers en même temps

> Le async with BURGER_SEM veut dire que lorsqu'une commande est passée en cuisine :  
>   - soit il y a un cuisinier libre, et celui-ci commence immédiatement à préparer le hamburger,
>   - soit tous les cuisiniers sont occupés, auquel cas on attend qu'il y en ait un qui se libère pour s'occuper de notre hamburger.


```python
BURGER_SEM = asyncio.Semaphore(3)

async def get_burger(client):
    print("    > Commande du burger en cuisine pour {}".format(client))
    async with BURGER_SEM:
        await asyncio.sleep(3)
        print("    < Le burger de {} est prêt".format(client))
```

### soda :  
Il n'y a qu'une machine à soda.  
On ne peut faire qu'un soda à la fois

> Le async with SODA_LOCK signifie que lorsque le serveur arrive à la machine à soda pour y déposer un gobelet :  
>    - soit la machine est libre (déverrouillée), auquel cas il peut la verrouiller pour l'utiliser immédiatement,
>    - soit celle-ci est déjà en train de fonctionner, auquel cas il attend (de façon asynchrone, donc en rendant la main) que le soda en cours de préparation soit prêt avant de verrouiller la machine à son tour.


```python
SODA_LOCK = asyncio.Lock()

async def get_soda(client):
    # Acquisition du verrou
    # la syntaxe 'async with FOO' peut être lue comme 'with (yield from FOO)'
    async with SODA_LOCK:
        # Une seule tâche à la fois peut exécuter ce bloc
        print("    > Remplissage du soda pour {}".format(client))
        await asyncio.sleep(1)
        print("    < Le soda de {} est prêt".format(client))
```

### frites :  
Le bac à frites permet de cuire 5 portions d'un coup.
Il est nécessaire d'attendre pour chaque cuisson tous les 5 portions

> Passons enfin au bac à frites. Cette fois, asyncio ne nous fournira pas d'objet magique, donc il va nous falloir réfléchir un peu plus. Il faut que l'on puisse l'utiliser une fois pour faire les frites des 5 prochaines commandes. Dans ce cas, un compteur semble une bonne idée :
>   - Chaque fois que l'on prend une portion de frites, on décrémente le compteur ;
>   - S'il n'y a plus de frites dans le bac, il faut en refaire.
  
```python
FRIES_COUNTER = 0
FRIES_LOCK = asyncio.Lock()

async def get_fries(client):
    global FRIES_COUNTER
    async with FRIES_LOCK:
        print("    > Récupération des frites pour {}".format(client))
        if FRIES_COUNTER == 0:
            print("   ** Démarrage de la cuisson des frites")
            await asyncio.sleep(4)
            FRIES_COUNTER = 5
            print("   ** Les frites sont cuites")
        FRIES_COUNTER -= 1
        print("    < Les frites de {} sont prêtes".format(client))
```


## exemple de sortie :
```
>>> loop.run_until_complete(asyncio.wait([serve('A'), serve('B')]))
=> Commande passée par B
=> Commande passée par A
    > Remplissage du soda pour B
    > Récupération des frites pour B
   ** Démarrage de la cuisson des frites
    > Commande du burger en cuisine pour B
    > Commande du burger en cuisine pour A
    < Le soda de B est prêt
    > Remplissage du soda pour A
    < Le soda de A est prêt
    < Le burger de B est prêt
    < Le burger de A est prêt
   ** Les frites sont cuites
    < Les frites de B sont prêtes
    > Récupération des frites pour A
    < Les frites de A sont prêtes
<= B servi en 0:00:04.003111
<= A servi en 0:00:04.003093
```

# Version refaite via des classes etc... par mes soins :
Fonctionnement similaire  
exemple de sortie :
```


délai d'arriver des clients en seconde : 
		 [0.7, 2.8, 5.0]

              (B)urger  | (F)rites | (S)oda
              | 1 | 2 | 3 |
              |BFS|BFS|BFS|
              =============
  0s + 000ms  |   |   |   |
  0s + 702ms => Commande passée par 0
  0s + 702ms  |  +|   |   |
  0s + 702ms  |+ o|   |   |** Préparation du soda du client 0
  0s + 702ms  |o+o|   |   |** Préparation du burger du client 0 - 2 serveur(s) disponible(s)
  1s + 703ms  |oo-|   |   |** Démarrage de la cuisson des frites
  2s + 802ms => Commande passée par 1
  2s + 802ms  |oo |+  |   |
  2s + 802ms  |oo |o+ |   |** Préparation du burger du client 1 - 1 serveur(s) disponible(s)
  2s + 802ms  |oo |oo+|   |
  3s + 703ms  |-o |ooo|   |** Préparation du soda du client 1
  3s + 803ms  | o |oo-|   |
  4s + 704ms  | - |oo |   |** les frites du client 0 - 4 portions restantes
  4s + 704ms  |   |o- |   |** les frites du client 1 - 3 portions restantes
  4s + 704ms <= 0 servi en 0:00:04.002815
  5s + 001ms => Commande passée par 2
  5s + 001ms  |   |o  |+  |
  5s + 001ms  |   |o  |o +|** Préparation du burger du client 2 - 1 serveur(s) disponible(s)
  5s + 001ms  |   |o  |o+o|** Préparation du soda du client 2
  5s + 001ms  |   |o  |o-o|** les frites du client 2 - 2 portions restantes
  5s + 804ms  |   |-  |o o|
  5s + 804ms <= 1 servi en 0:00:03.001828
  6s + 002ms  |   |   |o -|
  8s + 002ms  |   |   |-  |
  8s + 002ms <= 2 servi en 0:00:03.000853
Plus personne ? on ferme !

Process finished with exit code 0
```
