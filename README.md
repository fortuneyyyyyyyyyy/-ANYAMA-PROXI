# ANYAMA PROXI

Annuaire de proximité pour trouver rapidement un artisan à Anyama. Cette version remplace le tableau JavaScript en mémoire par une vraie application Flask persistante : les inscriptions sont enregistrées dans PostgreSQL, notamment Neon.

## Architecture choisie

Le projet est volontairement monolithique : Flask + Jinja + SQLAlchemy + PostgreSQL. C'est le bon niveau de simplicité pour un petit annuaire public. **SQLite est autorisé uniquement pour les tests et le développement local ; PostgreSQL/Neon est obligatoire en production.** Le frontend reste en HTML/CSS vanilla, donc le déploiement est léger et ne demande aucun build Node.

## Déploiement recommandé : Render + Neon

Netlify héberge très bien le HTML statique, mais pas ce serveur Flask persistant tel quel. Pour un seul service gratuit et simple :

1. Créer une base PostgreSQL sur [Neon](https://neon.tech), choisir la **pooled connection string** et ajouter `sslmode=require` si Neon ne l'a pas déjà fourni.
2. Pousser ce dossier dans un dépôt GitHub privé ou public.
3. Sur Render, créer un **Web Service** depuis le dépôt. Render détectera `render.yaml`, sinon utiliser `pip install -r requirements.txt` en build et `gunicorn --workers 2 --threads 2 --timeout 30 wsgi:app` en start.
4. Ajouter `DATABASE_URL` avec l'URL Neon et laisser Render générer `SECRET_KEY`. Garder `FLASK_ENV=production` et `COOKIE_SECURE=1`.
5. Après le premier déploiement, ouvrir `/health/ready`. Le résultat doit indiquer `{"status":"ready"}`.
6. Pour ajouter les trois contacts du prototype, exécuter une fois `python seed.py` dans un environnement connecté à la même base, ou les saisir via le formulaire public.

Le palier gratuit Render peut mettre le service en veille ; le premier accès après inactivité peut donc être plus lent. Neon peut également mettre une base en veille sur les paliers gratuits. Les données restent persistantes dans Neon, contrairement à un fichier SQLite placé sur un hébergeur éphémère.

## Lancer en local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export SECRET_KEY='dev-secret-change-me'
export DATABASE_URL='sqlite:///anyama-proxi.db'
export FLASK_ENV=development
flask --app wsgi run --debug
```

Puis ouvrir http://127.0.0.1:5000. Pour utiliser Neon en local, remplacez simplement `DATABASE_URL` par la chaîne Neon ; ne commitez jamais cette valeur.

## Protections incluses

- Validation serveur stricte des longueurs, caractères et numéro de téléphone.
- SQLAlchemy avec paramètres liés, aucun SQL interpolé pour les données utilisateur.
- Protection CSRF sur l'inscription, cookies HttpOnly/SameSite et Secure en production.
- Limitation à 5 inscriptions par heure et par adresse IP, plus une limite globale.
- Honeypot anti-robots, taille maximale de requête et réponses 413/429 propres.
- Échappement Jinja par défaut contre XSS, politique CSP, anti-clickjacking, `nosniff`, HSTS et Permissions-Policy.
- Logs rotatifs côté serveur sans enregistrer le numéro de téléphone.
- Health checks `/health/live` et `/health/ready`.

## Évolutions conseillées avant une vraie campagne publique

Ajouter une validation manuelle par un administrateur, une fonction de retrait/modification d'un contact, une page de politique de confidentialité et un mécanisme de signalement. Pour plusieurs instances, remplacer le rate limiter mémoire par Redis partagé. Les numéros de téléphone sont des données personnelles : demander le consentement et prévoir leur suppression sur demande.

## Tests

```bash
pytest -q
```

git add .
git commit -m "v1.1 ANYAMA PROXI"

git push -u origin main