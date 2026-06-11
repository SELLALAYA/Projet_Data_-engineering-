# Price Intelligence : Pipeline d'Analyse et de Pricing Data-Driven

> README technique — Version pour soutenance et documentation projet 📊

Checklist (contenu de ce document)
- [x] Résumé analytique
- [x] Architecture
- [x] KPIs & Insights
- [x] Perspectives & prochaines étapes
- [x] Conclusion

---

## Résumé Analytique

Ce projet met en place un pipeline reproductible pour produire des KPIs de pricing fiables et auditables. L'approche combine des transformations SQL industrielle (dbt) pour construire des marts KPI, suivies d'une validation statistique approfondie réalisée dans des notebooks Python. Les modèles dbt standardisent et agrègent les séries de prix par SKU / retailer / période, puis les notebooks appliquent des tests inférentiels (ANOVA, tests t), des régressions (OLS, modèles panel) et du modeling prédictif pour confirmer la robustesse des indicateurs. L'objectif métier est d'alimenter des décisions de pricing et des alertes opérationnelles basées sur des métriques data‑driven. ✅

## Architecture

- `dbt/models/marts/` : contiendra les modèles SQL qui calculent les KPIs métier (ex. `mart_volatility_analysis.sql`, `mart_price_trends.sql`, `mart_retailer_comparison.sql`). Ces marts fournissent des tables agrégées par date, SKU et retailer, prêtes pour consommation BI et analyse.
- `notebooks/` : ensemble de notebooks d'analyse et de validation statistique :
  - `01_data_audit_and_profiling.ipynb` — audits de qualité et profilage.
  - `02_exploratory_data_analysis.ipynb` — EDA et détection de patterns/saisonnalités.
  - `03_inferential_statistics.ipynb` — tests inférentiels (ANOVA, tests t), régressions (OLS, modèles panel) pour valider différences inter‑groupes et facteurs explicatifs.
  - `04_predictive_modeling.ipynb` — modèles de prévision (SARIMA, XGBoost/LightGBM) et backtesting.

Le flux logique : collecte → staging (nettoyage) → transformations dbt (marts KPI) → validation statistique (notebooks) → consommation (dashboards / processus de pricing).

## Validation Statistique

Cette section décrit comment les notebooks valident scientifiquement les KPIs produits par les modèles dbt :

- `01_data_audit_and_profiling.ipynb` : contrôles de qualité (missingness, duplicate, ranges), détection d'outliers (IQR, z‑score) et préparation des jeux de données pour analyses formelles.
- `02_exploratory_data_analysis.ipynb` : analyses descriptives et diagnostics (ACF/PACF, décomposition STL, visualisations) pour vérifier saisonnalité, trend et patterns structurels pouvant biaiser les KPIs.
- `03_inferential_statistics.ipynb` : tests inférentiels et modèles explicatifs appliqués aux KPIs :
  - Comparaisons de moyennes : ANOVA et Kruskal–Wallis pour différences multi‑groupes ; tests t (avec corrections de type Bonferroni/Holm) pour comparaisons pair à pair.
  - Analyse de variance des dispersions : tests de Levene pour comparer volatilités entre groupes.
  - Régressions : régressions linéaires OLS avec variables dummy (effets retailers), estimation d'effets fixes (panel regression) si jeu de données panel disponible, et correction d'erreurs standards (robust / clustered SE).
  - Diagnostics : tests d'hétéroscédasticité (Breusch‑Pagan), multicolinéarité (VIF), et intervales de confiance pour quantifier précision des estimations.
- `04_predictive_modeling.ipynb` : validation prédictive via backtesting et cross‑validation temporelle (metrics : MAPE, RMSE, MAE) ; interprétabilité (feature importance, SHAP) pour expliquer drivers des KPIs.

Pour chaque test/estimation, les notebooks produisent des artefacts (= tables / figures) réutilisables en production : p‑values, intervalles de confiance, coefficients estimés et rapports de diagnostic. Les conclusions statistiques sont traduites en seuils opérationnels (ex. CV > X déclenche revue produit).

## Workflow

Procédure recommandée pour exécuter le pipeline depuis la racine du projet :

1) Se positionner à la racine

```powershell
Set-Location -Path "D:\Projet_Data_-engineering-"
```

2) Préparer l'environnement (Python, dépendances, profiles dbt)

```powershell
# installer dépendances Python
python -m pip install -r requirements.txt

# vérifier configuration dbt (profiles.yml) et variables d'environnement
# Exemples : setx DBT_PROFILES_DIR "C:\Users\<user>\.dbt"; setx REDSHIFT_USER "..."
```

3) Exécuter les transformations dbt (marts KPI)

```powershell
# exécuter les modèles marts uniquement
dbt run --models path:dbt/models/marts

# exécuter les tests de schéma et tests singuliers sur les marts
dbt test --models path:dbt/models/marts
```

4) Lancer les notebooks de validation (interactive ou non‑interactive)

```powershell
# interactive
jupyter lab

# exécution non interactive et enregistrement des sorties (papermill)
papermill notebooks/01_data_audit_and_profiling.ipynb outputs/01_data_audit_out.ipynb
papermill notebooks/02_exploratory_data_analysis.ipynb outputs/02_eda_out.ipynb
papermill notebooks/03_inferential_statistics.ipynb outputs/03_inferential_out.ipynb
papermill notebooks/04_predictive_modeling.ipynb outputs/04_predictive_out.ipynb
```

5) Intégration & automatisation

- Orchestration : packager les étapes dbt + exécution notebooks dans un DAG Airflow pour runs planifiés et notifications en cas d'échec.
- CI : exécuter `dbt run` + `dbt test` + notebooks via pipeline CI (GitHub Actions / GitLab CI) avant merging en production.

Notes pratiques :
- Versionnez les notebooks ou exportez‑les en scripts pour traçabilité (nbdime ou conversion en .py).
- Documentez la configuration `profiles.yml` et stockez les secrets via un vault/secret manager en environnement CI.


## KPIs & Insights

Principaux KPIs calculés et leur intérêt business 🔍 :

- Prix moyen
  - Définition : moyenne arithmétique des observations de prix sur la période.
  - Importance : suit la tendance de marché et sert de baseline pour la stratégie tarifaire.

- Volatilité
  - Définition : mesure de dispersion (écart‑type, variance, coefficient de variation) d'une série de prix sur fenêtre rolling.
  - Importance : identifie l'instabilité tarifaire ; utile pour surveiller risques de marge, arbitrage et besoin d'alerting automatisé.

- Price Gap (écart inter‑plateformes)
  - Définition : différence (absolue ou relative) de prix entre retailers/platformes pour un même SKU.
  - Importance : détection d'opportunités d'arbitrage, alignement des prix, ou ciblage de promotions.

- Taux de remise (discount rate)
  - Définition : (list_price - sale_price) / list_price.
  - Importance : quantifie la profondeur des promotions, impact sur marge et fréquence des offres commerciales.

Chaque KPI est produit avec granularité configurable (jour, 7j, 30j, mois) et accompagné de métriques de qualité (taux de missing, outliers) pour garantir fiabilité.

## Perspectives & Prochaines Étapes

1. Automatisation & orchestration 🔁
   - Orchestrer ingestion → dbt → notebooks via Airflow (ou orchestrateur équivalent) pour runs planifiés et audits automatisés.

2. Monitoring de qualité des données et KPIs 📈
   - Mettre en place des alertes (Prometheus/Grafana) sur dérives : hausse de volatilité inhabituelle, taux d'observations manquantes, ou ruptures de série.

3. Enrichissement des modèles prédictifs et features engineering 🤖
   - Ajouter signaux externes (stock, campagnes marketing, événementiel), utiliser modèles de séries temporelles avancés et expliquer les prédictions (SHAP) pour adoption métier.

## Conclusion

Ce pipeline fournit une base rigoureuse et reproductible pour piloter le pricing de façon data‑driven : production de KPIs métier robustes, validation statistique formelle et roadmap claire pour industrialisation et monitoring. 🚀

---

Pour toute question technique ou besoin d'adaptation pour la soutenance, indiquer le notebook ou le modèle dbt concerné (`dbt/models/marts/*` ou `notebooks/*`).


