# Récupération des DECP de plateformes non publiées sur data.gouv.fr

Ce projet vise à développer un script permettant de télécharger facilement les données essentielles de la commande publique publiées sur des plateformes de marché qui ne publient pas sur data.gouv.fr.

Liste des plateformes identifiées :

- [marches.cnes.fr](https://marches.cnes.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marchespublics.paysdelaloire.fr](https://marchespublics.paysdelaloire.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marchespublics.hautsdefrance.fr](https://marchespublics.hautsdefrance.fr/?page=entreprise.EntrepriseRechercherListeMarches) (pas de données, remplacé par marchespublics596280.fr)
- [marchespublics596280.fr](https://marchespublics596280.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marchespublics.grandest.fr](https://marchespublics.grandest.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marches.departement13.fr](https://marches.departement13.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marchespublics.lenord.fr](https://marchespublics.lenord.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [alsacemarchespublics.eu](https://alsacemarchespublics.eu/?page=entreprise.EntrepriseRechercherListeMarches)
- [mpe-marseille.local-trust.com](https://mpe-marseille.local-trust.com/?page=entreprise.EntrepriseRechercherListeMarches)
- [marches.megalisbretagne.org](https://marches.megalisbretagne.org/?page=entreprise.EntrepriseRechercherListeMarches)
- [marches.maximilien.fr](https://marches.maximilien.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [marchespublics.gard.fr](https://marchespublics.gard.fr/?page=entreprise.EntrepriseRechercherListeMarches)
- [demat-ampa.fr](https://demat-ampa.fr/?page=entreprise.EntrepriseRechercherListeMarches)

## Utiliser les script fonctions de download.py
###Utiliser les script
Pour initialiser tous les sites connus
```
download.ROOT_XML_DIR = 'xml'
download.STAT_FILE_PATH = 'disponibilite-donnees.csv'
download.collects_multiple_platforms_data(download.get_all_platforms(),
                                          download.get_all_years_available(),
                                          force=False, thread_number=3,
                                          delay=0.2, should_initialize=True)
```
Le script va d'abord rechercher la liste des acheteurs connus sur chaque site, puis télécharger les DECP au format xml de ces sites et enfin aggréger le tout dans un fichier multiple_platforms.xml
Un fichier de statistiques est produit: disponibilite-donnees.csv
