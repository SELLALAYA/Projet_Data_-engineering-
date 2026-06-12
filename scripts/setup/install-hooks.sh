#!/bin/bash

echo ""
echo "================================================"
echo "Installation des hooks Git..."
echo "================================================"
echo ""

# Vérifier que le fichier hook existe
if [ ! -f "scripts/setup/commit-msg-hook" ]; then
  echo "ERREUR : fichier scripts/setup/commit-msg-hook introuvable"
  echo "Assure-toi d'etre dans le dossier racine du projet"
  exit 1
fi

# Copier le hook dans .git/hooks/
cp scripts/setup/commit-msg-hook .git/hooks/commit-msg

# Donner la permission d'execution
chmod +x .git/hooks/commit-msg

echo "Hook installe avec succes !"
echo ""
echo "Tes commits doivent maintenant avoir ce format :"
echo "   type: description"
echo ""
echo "Types valides : feat, fix, chore, ci, docs, test, refactor"
echo ""
echo "Exemples :"
echo "   feat: add amazon price scraper"
echo "   fix: correct airflow dag timeout"
echo "   chore: update docker dependencies"
echo "================================================"
echo ""
