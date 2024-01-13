# DaV_StillsExporter :camera_flash:
Batch export stills from timeline markers (DaV Python API)

**Python version**: 3.6
<br/>**Dependencies**: none
<br/>**Author**: [Olivier Patron](https://github.com/Luronnade)

## Installation et usage 
Le script s'appelle depuis le terminal (sous MacOs uniquement) et est écrit en Python. Il utilise l'API de DaVinci Resolve, qui dépend de Python 3.6. 
<br/>Python 3.6 se télécharge ici : https://www.python.org/downloads/release/python-368/

Pour appeler le script depuis le terminal (en étant dans le dossier où est posé le script) :
```
python3 dav_stills_out.py
```

Pour appeler le script avec un dossier de sortie spécifique <sup>(*)</sup> :
```
python3 dav_stills_out.py "DossierDeSortie"
```

Le script s'applique à la timeline Resolve actuellement ouverte.
<br/>Le fichier de config `config.ini` est à conserver à côté du script. Il permet de régler les éléments suivants :
* **MarkerColor**: Couleur des marqueurs utilisés pour identifier les stills (la liste proposée en commentaire n'est pas exhaustive, il y en a d'autres)
* **Gallery**: Le nom de la galerie Resolve dans laquelle travaillera le script. :warning: **ATTENTION** :warning: cette galerie est vidée à chaque exécution du script
* **OutputFolder**: le nom du dossier de sortie, auquel peut se concaténer le nom de dossier passé en paramètre comme expliqué au-dessus <sup>(*)</sup>
* **DeleteDRX**: si le script doit supprimer les DRX après exécution et ne garder que les images ou les conserver
* **StillResolutionOverride**: Yes pour activer l'override et appliquer la résolution définie avec StillWidth et StillHeight à la place de la résolution de la timeline

Par exemple, pour appeler le script dans un dossier de sortie `/Users/olivier/STAR WARS - THE REMAKE/STILLS/`, avec un sous-dossier à la date du jour `20240105_Jour01`, il faut :
* dans le fichier `config.ini` : `OutputFolder:"/Users/olivier/STAR WARS - THE REMAKE/STILLS/"`
* appeler le script : `python3 dav_stills_out.py "20240105_Jour01"`

> [!CAUTION]
> Faites bien des tests, en particulier si vous choisissez d'utiliser une résolution spécifique pour les stills. En effet, pour changer de résolution, la timeline entière change de résolution le temps de sortir les stills. Si le script plante en cours de route, il n'aura pas eu le temps de rétablir votre résolution de timeline initiale !

N'hésitez pas à faire des retours. Si j'ai le temps, j'améliorerai le script.

PS : Thomas Briant, avec l'aide de Théo Lopez, a aussi mis à dispo sur le Discord ADIT un script pour exporter automatiquement les stills sur certains marqueurs. Des différences de fond différencient les 2 scripts. Celui de Théo est écrit en Lua, donc exécutable tout de suite (sans installer toute la librairie Python). Il utilise le Render de Resolve alors que le mien utilise les galeries de stills et leur fonction d'export intégrée : je ne peux actuellement pas exporter les burn-in. Le sien profite aussi d'une jolie interface dans Resolve alors que le mien dépend d'un appel en ligne de commande.

