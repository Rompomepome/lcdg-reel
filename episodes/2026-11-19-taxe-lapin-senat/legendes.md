# Taxe lapin : le texte voté par le Sénat — légendes de publication

À faire par Romain avant de publier :
- remplacer `[URL-ARTICLE]` par l'adresse du dossier « PLFSS 2027 : ce que le Sénat a voté pour votre cabinet » sur le site (le site n'était pas joignable depuis la session du 19/11) ;
- relire le texte adopté n° 33 (article 23 bis) et le compte rendu du 16/11 sur senat.fr : le Sénat était hors réseau de la session, le reel s'appuie sur les citations du dossier ;
- à publier tant que la commission mixte paritaire n'a pas statué : le reel dit « le texte n'est pas définitif » ;
- étiquette « Info IA » (voix de synthèse) sur Instagram et Facebook ;
- format 4:5 : le reel 9:16 est composé pour le recadrage 4:5 du fil. Un fichier 4:5 se tire du 9:16 livré, sans rien perdre : `ffmpeg -i final/reel.mp4 -vf "crop=1080:1350:0:285" -c:a copy reel_4x5.mp4` ;
- le même jour : la story sondage, puis la story lien (`lcdg-reel-atelier/lcdg_1119/visuels/story_taxe_lapin_*.png`, textes ci-dessous).

Version publicité, après le rendu du reel complet (sa narration doit être en cache) :
`python scripts/pub.py episodes/2026-11-19-taxe-lapin-senat 0,1,4,5,6,8 --badge "Rendez-vous manqués"` puis
`python scripts/livrer.py episodes/2026-11-19-taxe-lapin-senat-pub` (environ 40 s : l'écart 5 € / prix de la consultation, les deux conditions, qui encaisse, la promesse). Attention : Meta refuse en Europe les publicités qu'il classe comme politiques (refus du reel « minimum de patients ») ; le reel cite un sénateur et « le texte voté ». Si la publicité est refusée, ne pas la reformuler pour contourner : garder le reel en organique.

## Instagram (reel)

Taxe lapin : 5 € annoncés en séance, jusqu'au prix de la consultation dans le texte voté.

Le 16 novembre, le Sénat a adopté une pénalité pour les rendez-vous non honorés. En séance, le sénateur qui défendait l'amendement a parlé d'une « pénalité limitée à 5 euros » et d'une annulation possible « jusqu'à 24 heures avant ». Le texte adopté ne contient ni ce montant ni ce délai : la pénalité « ne peut en aucun cas excéder le montant de la consultation », et l'annulation doit respecter « un délai raisonnable », qu'un décret en Conseil d'État doit fixer.

Pas de pénalité si le patient justifie d'un motif impérieux, d'ordre personnel, familial ou professionnel, ou d'un motif de santé. Et pour la réclamer, le médecin doit avoir informé le patient à la prise de rendez-vous et lui avoir rappelé la date et l'heure au moins une fois.

Qui encaisse ? Le texte prévoit un paiement à la caisse d'assurance maladie du patient, sans dire si la somme est ensuite reversée au médecin. Selon le Cercle, tant que rien ne le dit, la pénalité ne compense pas le créneau perdu.

Rien n'est définitif : le texte doit passer en commission mixte paritaire.

Et vous, si la loi passe, l'appliqueriez-vous à vos patients ? Notre analyse complète et notre recommandation sont sur le site du Cercle (inscription gratuite) : lien en bio.

#medecingeneraliste #taxelapin #plfss2027 #rendezvous #lecercledesgeneralistes

## Facebook (reel)

Titre, à placer en première ligne (pour que ce soient les médecins qui réagissent, pas les patients) :
Taxe lapin : ce que le texte voté change pour votre cabinet

Médecins libéraux : le texte voté par le Sénat le 16 novembre permet une pénalité jusqu'au prix de la consultation, pas les 5 € annoncés en séance. À une condition : avoir informé le patient à la prise de rendez-vous, et lui avoir rappelé la date et l'heure au moins une fois. Pas de pénalité si le patient justifie d'un motif impérieux, d'ordre personnel, familial ou professionnel, ou d'un motif de santé. Et le texte ne dit pas si la somme payée à la caisse du patient vous est reversée.

Texte non définitif. Notre analyse et notre recommandation pour le cabinet : [URL-ARTICLE]?utm_source=facebook&utm_medium=reel&utm_campaign=taxe-lapin

## LinkedIn (version carrée, lien dans la publication)

Le Sénat a adopté le 16 novembre 2026 les amendements identiques n° 7 rectifié octies et n° 84 rectifié quater, qui permettent à l'établissement de santé, au centre de santé ou au professionnel de santé libéral d'« exiger du patient le paiement d'une pénalité » lorsqu'il ne se présente pas ou annule « sans respecter un délai raisonnable ».

En séance, le sénateur qui a défendu l'amendement n° 7 a présenté une « pénalité limitée à 5 euros » et une « possibilité d'annuler un rendez-vous jusqu'à 24 heures avant ». Ni ce montant ni ce délai ne figurent dans le texte adopté : la pénalité « est proportionnelle au tarif de la consultation ou est fixée à une somme forfaitaire, et ne peut en aucun cas excéder le montant de la consultation ». Un décret en Conseil d'État doit fixer le délai raisonnable, les motifs d'exonération et les voies de règlement amiable des litiges.

Pour la réclamer, le professionnel doit avoir informé le patient à la prise de rendez-vous et lui avoir rappelé la date et l'horaire au moins une fois. Le paiement va à l'organisme d'assurance maladie de l'assuré, prélevé sur son compte après autorisation ou récupéré sur ses prestations à venir ; le texte ne dit pas si la somme est ensuite reversée au professionnel.

Le projet de loi de financement a été adopté par le Sénat le 18 novembre (201 voix contre 124). Rien n'est définitif : le texte doit passer en commission mixte paritaire. La pénalité votée en 2025 avait été censurée par le Conseil constitutionnel.

Notre analyse et notre recommandation pour le cabinet (inscription gratuite) : [URL-ARTICLE]?utm_source=linkedin&utm_medium=social&utm_campaign=taxe-lapin

## Publicité Meta (reel boosté)

Texte principal (les 125 premiers caractères s'affichent sans « Plus ») :
Médecins libéraux : la pénalité pour rendez-vous manqué pourrait aller jusqu'au prix de la consultation. À une condition : le rappel au patient.

Titre : Rendez-vous manqués : ce qui change au cabinet

Bouton : En savoir plus. Lien : [URL-ARTICLE]?utm_source=meta&utm_medium=paid&utm_campaign=taxe-lapin

## Stories du jour (Instagram et Facebook)

1. `story_taxe_lapin_sondage.png` : poser le sticker sondage sous la flèche. Question : « L'appliqueriez-vous ? » ; réponses : « Oui » / « Non ».
2. `story_taxe_lapin_lien.png` : poser le sticker lien sous la flèche, texte du sticker « L'analyse complète ».
   Lien : [URL-ARTICLE]?utm_source=instagram&utm_medium=story&utm_campaign=taxe-lapin

## Lien de la bio Instagram, à mettre à jour le jour de la publication

[URL-ARTICLE]?utm_source=instagram&utm_medium=reel&utm_campaign=taxe-lapin
