# Site de Démocratie Ouverte

## Configuration du site

La configuration se fait depuis l'interface d'aministration, accessible à cette adresse :
http://xxx/admin/.

### Pages

### Questions
Les questions ne sont pas configurés comme des pages ............

### Traductions et multi-langue

## Pour les développeurs

### Mettre à jour la base de donnée

    python manage.py makemigrations
    python manage.py migrate

### Mettre à jour l'index pour la fonction de recherche

To update the index and make work de search function :

```bash
python manage.py update_index
```


### Mettre à jour les traductions :

- Créer ou mettre à jour un fichier de traductions :
    `django-admin makemessages -l fr`
- Renseigner à la main les traductions dans les fichiers .po autogénéré
- Compiler les fichiers de traductions:
    `django-admin compilemessages`

### Utilisation de l'app django Tweets

Cf le README correspondant à l'app Tweets


### Système de traduction utilisé

Le système de traduction utilisé est [wagtail-localize](https://www.wagtail-localize.org/)
> Attention : Si une langue est rajouté il faudra (en plus du système de base de wagtail localize) adapter le switch de langue du header



### Commit de suppression des questions avec classement

https://gitlab.com/telescoop/democratie-ouverte/back/-/commit/7a901bffae7f54ead328b4d84819fa2716b1786b
