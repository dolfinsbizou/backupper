# Backupper

Un simple utilitaire de backup de fichiers configurable en YAML.

Voir `./backupper.py -h` pour l'utilisation de la commande.

backupfile.yml d'exemple :

```
backup_dir: /racine/du/dossier/de/sauvegarde
artifacts:
    - un/fichier
    - un/dossier
    - un/autre/dossier/
    - et/caetera
```
