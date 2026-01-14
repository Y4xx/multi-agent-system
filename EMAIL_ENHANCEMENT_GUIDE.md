# Email Application System - User Guide

## Système d'Application par Email avec PDFs et Contenu Généré par IA

Ce système améliore le processus d'envoi de candidatures par email en automatisant la génération du contenu et l'ajout de pièces jointes PDF professionnelles.

---

## 📋 Fonctionnalités Principales

### 1. 📎 Pièces Jointes PDF Automatiques

Le système attache automatiquement deux PDFs à chaque email de candidature :

- **CV du candidat** : Nommé `CV_{nom_candidat}.pdf`
- **Lettre de motivation** : Nommée `Lettre_Motivation_{nom_candidat}_{entreprise}.pdf`

**Gestion automatique du CV** :
- Un dossier temporaire (`temp_cv/`) stocke le CV uploadé
- Lorsqu'un nouveau CV est uploadé, l'ancien est automatiquement supprimé
- Le CV est copié avec un nom standardisé pour garantir la cohérence

### 2. 📧 Génération Automatique de l'Objet de l'Email

L'IA génère un objet professionnel et personnalisé pour chaque candidature.

**Format** : `Candidature de [Nom Prénom] pour le poste de [Titre] - [Entreprise]`

**Exemple** :
```
Candidature de Jean Dupont pour le poste de Développeur Python Senior - TechCorp
```

**Caractéristiques** :
- Personnalisé avec les informations du candidat
- Format professionnel français
- Génération via OpenAI GPT-4
- Fallback sur template si l'IA n'est pas disponible

### 3. ✉️ Génération Automatique du Corps de l'Email

L'IA génère un email professionnel en français avec la structure suivante :

**Structure** :
1. **Salutation professionnelle** : "Madame, Monsieur,"
2. **Introduction brève** : 1-2 phrases présentant la candidature
3. **Référence aux pièces jointes** : Mentionne le CV et la lettre de motivation
4. **Appel à l'action** : Demande d'entretien
5. **Formule de politesse** : "Cordialement,"
6. **Signature** : Nom, email, téléphone du candidat

**Exemple** :
```
Madame, Monsieur,

Je vous adresse ma candidature pour le poste de Développeur Python Senior 
au sein de TechCorp.

Vous trouverez ci-joint mon CV ainsi que ma lettre de motivation détaillant 
mon parcours et mes motivations pour ce poste.

Je reste à votre disposition pour un entretien afin de discuter de ma 
candidature.

Cordialement,
Jean Dupont
jean.dupont@example.com
+33 6 12 34 56 78
```

---

## 🚀 Utilisation du Système

### Étape 1 : Téléverser le CV

```http
POST /upload-cv
Content-Type: multipart/form-data

file: [votre_cv.pdf]
```

**Résultat** :
- CV analysé et parsé
- Données structurées extraites (nom, email, téléphone, compétences, etc.)
- CV sauvegardé dans le dossier temporaire
- Ancien CV automatiquement supprimé

### Étape 2 : Sélectionner une Offre d'Emploi

```http
GET /job-offers?location=Paris&job_type=Full-time
```

Ou obtenir les offres correspondantes :

```http
POST /match-offers
Content-Type: application/json

{
  "cv_data": {...},
  "job_type": "Full-time",
  "location": "Paris",
  "top_n": 10
}
```

### Étape 3 : Générer la Lettre de Motivation

```http
POST /generate-letter
Content-Type: application/json

{
  "cv_data": {...},
  "job_id": 1,
  "custom_message": "Message personnalisé optionnel"
}
```

**Résultat** :
- Lettre de motivation générée par IA
- Analyse de correspondance compétences/poste
- Recommandations personnalisées

### Étape 4 : Soumettre la Candidature

```http
POST /apply
Content-Type: application/json

{
  "cv_data": {...},
  "job_id": 1,
  "motivation_letter": "..."
}
```

**Ce qui se passe automatiquement** :
1. ✅ Génération du PDF de la lettre de motivation
2. ✅ Récupération du CV depuis le dossier temporaire
3. ✅ Génération de l'objet de l'email par IA
4. ✅ Génération du corps de l'email par IA
5. ✅ Attachement des deux PDFs
6. ✅ Envoi de l'email via SMTP ou Gmail API

---

## ⚙️ Configuration

### Variables d'Environnement Requises

```bash
# IA pour génération de contenu
OPENAI_API_KEY=sk-xxxx
MODEL_NAME=gpt-4o-mini

# Email SMTP (optionnel)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre-email@gmail.com
SENDER_PASSWORD=votre-mot-de-passe-app

# Ou Gmail API (optionnel)
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxx
```

**Note** : Si aucune configuration email n'est fournie, le système simule l'envoi pour démonstration.

---

## 🎯 Avantages du Système

### Pour les Candidats
- ✅ **Gain de temps** : Plus besoin d'écrire chaque email manuellement
- ✅ **Professionnalisme** : Contenu généré par IA, toujours professionnel
- ✅ **Cohérence** : Format standardisé pour toutes les candidatures
- ✅ **Pièces jointes automatiques** : CV et lettre toujours inclus
- ✅ **Personnalisation** : Chaque email adapté à l'offre et l'entreprise

### Pour les Développeurs
- ✅ **API simple** : Intégration facile via REST API
- ✅ **Fallback intelligent** : Fonctionne même sans IA
- ✅ **Double support email** : SMTP et Gmail API
- ✅ **Gestion automatique des fichiers** : Cleanup et organisation
- ✅ **Pas de dépendances supplémentaires** : Utilise les bibliothèques existantes

---

## 📁 Structure des Fichiers

```
backend/
├── temp_cv/              # Dossier temporaire pour CVs (auto-cleanup)
│   └── CV_Nom_Prenom.pdf
├── exports/              # PDFs de lettres de motivation générés
│   └── Lettre_Motivation_Nom_Prenom_Entreprise.pdf
├── uploads/              # CVs uploadés originaux
│   └── cv_original.pdf
└── data/
    └── parsed_cv.json    # Données CV parsées
```

---

## 🔍 Exemples de Prompts

### Pour générer l'objet de l'email :
```
Génère un objet d'email professionnel en français pour une candidature au poste de 
[TITRE] chez [ENTREPRISE] pour le candidat [NOM].
Format : "Candidature de [Nom Prénom] pour le poste de [Titre] - [Entreprise]"
```

### Pour générer le corps de l'email :
```
Génère un email professionnel en français pour une candidature avec :
- Salutation professionnelle
- Introduction brève (1-2 phrases)
- Mention des pièces jointes (CV + lettre de motivation)
- Demande d'entretien
- Signature avec nom, email et téléphone du candidat
Ton : professionnel mais chaleureux, concis (8-10 lignes maximum)
```

---

## 🛠️ Dépannage

### L'email n'est pas envoyé
- Vérifiez les variables d'environnement (SMTP ou Gmail API)
- En mode démo (sans credentials), l'email est simulé

### Les PDFs ne sont pas attachés
- Vérifiez que le CV a été uploadé via `/upload-cv`
- Vérifiez que le dossier `temp_cv/` existe et est accessible

### Le contenu IA n'est pas généré
- Vérifiez `OPENAI_API_KEY` dans `.env`
- Le système utilise des templates de fallback si l'IA n'est pas disponible

### Ancien CV pas supprimé
- Vérifiez les permissions sur le dossier `temp_cv/`
- Le cleanup se fait automatiquement lors du prochain upload

---

## 📊 Métriques de Succès

Le système garantit :
- 📎 **100% des emails** incluent les deux PDFs attachés
- 🤖 **Génération IA** pour objet et corps (avec fallback)
- 🧹 **Cleanup automatique** du dossier temporaire
- 📧 **Support dual** SMTP et Gmail API
- 🔄 **Compatibilité ascendante** avec le code existant

---

## 📞 Support

Pour toute question ou problème, consultez :
- Documentation API : `/docs` (Swagger UI)
- Logs backend : Vérifiez la console pour les messages d'erreur
- Tests : Exécutez `/tmp/test_email_enhancements.py` et `/tmp/test_integration.py`

---

**Version** : 1.0.0
**Dernière mise à jour** : Janvier 2024
**Langue** : Français 🇫🇷
