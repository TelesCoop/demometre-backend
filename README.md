# Site de Démocratie Ouverte

## Configuration du site

La configuration se fait depuis l'interface d'aministration, accessible à cette adresse :
http://xxx/admin/.

### Pages

### Questions
Les questions ne sont pas configurés comme des pages

### Partie expert
afin de pouvoir la tester il y a plusieurs étapes (en effet seulement les experts associés à une évaluation doivent pouvoir avoir accès à cette partie là):
- Dans le backoffice : Paramètres > Utilisateurs > Rechercher l'utilisateur que l'on veut déclarer en tant qu'expert. Aller dans l'onglet Rôles et sélectionner la case Experts puis enregistrer. La personne est alors enregistrée comme étant un expert

![](readme-images/expert-role.png)

- Dans le backoffice: Evaluations > Evaluation > Selectionner l'évaluation pour laquelle vous souhaitez ajouter un expert > Indiquez que c'est une évaluation avec experts + Selectionner l'expert dans la liste + indiquer que la redevance a été payée (sinon l'expert n'aura pas accès à cette évaluation) (NB : depuis le parcours utilisateur de la plateforme il est possible d'ajouter un expert, cependant il est possible de déclarer que la redevance a été payée seulement depuis l'admin wagtail)

![](readme-images/assessment-experts.png)

Pour terminer : connectez-vous à la plateforme du DémoMètre avec le compte que vous avez déclaré comme étant expert, depuis la page du profile il y aura un bouton qui permet d'accéder à l'espace expert "Espace animateur".

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
