# Backupper

Un simple utilitaire de backup de fichiers configurable en YAML.

Voir `./backupper.py -h` pour l'utilisation de la commande.

backupfile.yml minimal :

```
backup_dir: /racine/du/dossier/de/sauvegarde
artifacts:
    - un/fichier
    - un/dossier
    - un/autre/dossier/
    - et/caetera
```

# Référence du backupfile.yml

## `backup_dir`

* **Définition :** Spécifie le dossier dans lequel le répertoire du backup sera créé. Si le dossier n'existe pas, il sera créé.
* **Type :** chemin d'accès relatif ou absolu.
* **Obligatoire :** non, sauf si `delete_old_backups` vaut `true`.
* **Valeur par défaut :** le dossier courant.

## `delete_old_backups`

* **Définition :** Permet de supprimer les précédents backups du dossier de sauvegarde spécifié dans `backup_dir`. Si `cleaning_policy` n'est pas défini, par défaut tous les précédents backups sont supprimés.
* **Type :** booléen.
* **Obligatoire :** non.
* **Valeur par défaut :** `false`.

## `artifacts`

* **Définition :** Spécifie la liste des fichiers et dossiers à sauvegarder.
* **Type :** liste de chemins d'accès relatifs ou absolus.
* **Obligatoire :** oui.
