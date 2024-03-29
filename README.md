# DaV_StillsExporter :camera_flash:
Batch export stills from timeline markers (DaV Python API)

**Host:** DaVinci Resolve<br/>
**Python version:** 3.6<br/>
**Dependencies:** none<br/>
**Author:** [Olivier Patron](https://github.com/Luronnade)

## Installation et usage 
Le script s'appelle depuis le terminal (sous MacOs uniquement) et est écrit en Python. Il utilise l'API de DaVinci Resolve, qui dépend de Python 3.6. 
<br/>Python 3.6 se télécharge ici : https://www.python.org/downloads/release/python-368/

Pour appeler le script depuis le terminal (en étant dans le dossier où est posé le script) :
```
python3 davstills.py
```
Usage complet :
```
davstills.py [-h] [-o OUTPUT] [-g GALLERY]
	-h, --help            	show this help message and exit
  	-o OUTPUT, --output OUTPUT
                        	stills output folder (will follow output path defined
                        	in config.ini)
  	-g GALLERY, --gallery GALLERY
                        	stills gallery name (must exist in Resolve project)
```
Pour appeler le script avec un dossier de sortie spécifique <sup>(*)</sup> :
```
python3 davstills.py --output "DossierDeSortie"
python3 davstills.py -o "DossierDeSortie"
```

Pour appeler le script avec un nom de galerie spécifique :
```
python3 davstills.py --gallery "NomDeLaGalerie"
python3 davstills.py -g "NomDeLaGalerie"
```

Le script s'applique à la timeline Resolve actuellement ouverte.
<br/>Le fichier de config `config.ini` est à conserver à côté du script. Il permet de régler les éléments suivants :
* **MarkerColor**: couleur des marqueurs utilisés pour identifier les stills (la liste proposée en commentaire n'est pas exhaustive, il y en a d'autres)
* **LimitInOut**: si réglé à `Yes`, seuls les marqueurs à l'intérieur des points in et out de la timeline seront considérés
* **Gallery**: le nom de la galerie Resolve dans laquelle travaillera le script. :warning: **ATTENTION** :warning: cette galerie est vidée à chaque exécution du script
* **OutputPath**: le chemin de sortie, auquel peut se concaténer le nom de dossier passé en paramètre comme expliqué au-dessus <sup>(*)</sup>
* **TimelineNamedFolder**: un dossier sera automatiquement généré et concaténé au chemin de sortie, qui prendra le même nom que la timeline. :warning: **ATTENTION** :warning: ce nom de dossier est écrasé si vous passez un nom de dossier dans l'appel de commande
* **DeleteDRX**: si le script doit supprimer les DRX après exécution et ne garder que les images ou les conserver
* **StillResolutionOverride**: `Yes` pour activer l'override et appliquer la résolution définie avec `StillWidth` et `StillHeight` à la place de la résolution de la timeline

Par exemple, pour appeler le script dans un dossier de sortie `/Users/olivier/STAR WARS - THE REMAKE/STILLS/`, avec un sous-dossier à la date du jour `20240105_Jour01`, et une galerie de stills Resolve nommée `J01` il faut :
* dans le fichier `config.ini` : `OutputFolder:"/Users/olivier/STAR WARS - THE REMAKE/STILLS/"`
* appeler le script : `python3 davstills.py --output "20240105_Jour01" --gallery "J01"`  ou `python3 davstills.py -o "20240105_Jour01" -g "J01"`

> [!CAUTION]
> Faites bien des tests, en particulier si vous choisissez d'utiliser une résolution spécifique pour les stills. En effet, pour changer de résolution, la timeline entière change de résolution le temps de sortir les stills. Si le script plante en cours de route, il n'aura pas eu le temps de rétablir votre résolution de timeline initiale !

N'hésitez pas à faire des retours. Si j'ai le temps, j'améliorerai le script.

PS : Thomas Briant, avec l'aide de Théo Lopez, a aussi mis à dispo sur le Discord ADIT un script pour exporter automatiquement les stills sur certains marqueurs. Des différences de fond différencient les 2 scripts. Celui de Théo est écrit en Lua, donc exécutable tout de suite (sans installer toute la librairie Python). Il utilise le Render de Resolve alors que le mien utilise les galeries de stills et leur fonction d'export intégrée : je ne peux actuellement pas exporter les burn-in. Le sien profite aussi d'une jolie interface dans Resolve alors que le mien dépend d'un appel en ligne de commande.

