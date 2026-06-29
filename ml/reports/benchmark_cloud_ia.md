# Benchmark Cloud IA — ObRail Europe
**Comparaison : Azure ML vs AWS SageMaker vs Google Vertex AI vs HuggingFace AutoTrain**

---

## Tableau comparatif

| Critère | Azure ML | AWS SageMaker | Google Vertex AI | HuggingFace AutoTrain |
|---------|----------|---------------|------------------|-----------------------|
| **Hébergement** | Microsoft Azure | Amazon AWS | Google Cloud | Cloud HuggingFace |
| **Entraînement automatique (AutoML)** | Oui (Azure AutoML) | Oui (Autopilot) | Oui (AutoML Tables) | Oui (No-code) |
| **Frameworks supportés** | scikit-learn, XGBoost, PyTorch, TensorFlow | scikit-learn, XGBoost, PyTorch, TensorFlow | scikit-learn, XGBoost, TensorFlow, PyTorch | Transformers, scikit-learn |
| **Déploiement endpoint REST** | Oui (ACI/AKS) | Oui (SageMaker Endpoints) | Oui (Vertex Endpoints) | Oui (Inference API) |
| **Tarif entraînement** | ~0.10–0.50 €/h (CPU) | ~0.05–0.50 $/h (CPU) | ~0.04–0.40 $/h (CPU) | Gratuit (modèles petits) |
| **Tarif inférence** | ~0.001 €/requête | ~0.0002 $/requête | ~0.0001 $/requête | Gratuit (limite) |
| **MLflow intégré** | Oui (natif) | Partiellement | Non (Vertex Experiments) | Non |
| **Pipeline CI/CD ML** | Azure Pipelines + ADF | CodePipeline + Step Functions | Cloud Build + Vertex Pipelines | GitHub Actions |
| **Monitoring modèle** | Application Insights | CloudWatch | Vertex Model Monitoring | Limité |
| **Intégration PostgreSQL** | Oui (Azure Database) | Oui (RDS) | Oui (Cloud SQL) | Non natif |
| **Conformité RGPD** | Oui (datacenters EU) | Oui (régions EU) | Oui (régions EU) | Oui |
| **Courbe d'apprentissage** | Modérée | Élevée | Modérée | Faible |
| **Documentation FR** | Bonne | Moyenne | Bonne | Bonne |

---

## Analyse par cas d'usage ObRail

### Régression (prédire duree_h)
| Plateforme | Approche recommandée | Avantage |
|-----------|---------------------|---------|
| **Azure ML** | Azure AutoML Regression | S'intègre avec ADF (déjà utilisé pour l'ETL) |
| AWS SageMaker | XGBoost built-in container | Déploiement rapide, scalable |
| Google Vertex AI | AutoML Tables | Bonne gestion des données tabulaires |
| HuggingFace | Non adapté | Orienté NLP/vision, pas tabular |

### Classification (substituabilité avion→train)
| Plateforme | Approche recommandée | Avantage |
|-----------|---------------------|---------|
| **Azure ML** | Azure AutoML Classification | Pipeline unifié avec notre infra Azure |
| AWS SageMaker | Linear Learner / XGBoost | Gestion native du déséquilibre de classes |
| Google Vertex AI | AutoML Tables | Explicabilité SHAP intégrée |
| HuggingFace | Non adapté | — |

### Clustering (K-Means familles)
| Plateforme | Approche recommandée | Avantage |
|-----------|---------------------|---------|
| **Azure ML** | Azure ML SDK + K-Means | Logging automatique avec MLflow |
| AWS SageMaker | K-Means built-in algorithm | Optimisé pour gros volumes |
| Google Vertex AI | Custom training job | Flexible |
| HuggingFace | Non adapté | — |

---

## Recommandation pour ObRail Europe

**Azure ML est le choix optimal** pour ce projet, pour 3 raisons :

1. **Cohérence avec l'infrastructure existante** : on utilise déjà Azure Data Factory (ETL), Azure Container Instances (API), et Azure Database for PostgreSQL. Ajouter Azure ML reste dans le même écosystème.

2. **MLflow natif** : tracking automatique des expériences (métriques, paramètres, artefacts) sans configuration supplémentaire.

3. **Pipeline de bout en bout** : ADF peut déclencher les jobs d'entraînement Azure ML directement après le chargement des données ETL → pipeline entièrement automatisé.

### Estimation des coûts (production légère)
| Poste | Azure ML | AWS SageMaker |
|-------|----------|---------------|
| Entraînement quotidien (30 min, CPU) | ~0.05 €/jour | ~0.04 $/jour |
| Endpoint inférence (1000 req/jour) | ~1 €/mois | ~0.20 $/mois |
| Stockage modèles (1 GB) | ~0.02 €/mois | ~0.02 $/mois |
| **Total mensuel** | **~2–5 €** | **~1–3 $** |

---

## Conclusion

Pour une mise en production réelle d'ObRail Europe :
- **Court terme** : Azure ML (intégration native avec l'infra Azure existante)
- **Long terme** : envisager Google Vertex AI pour l'explicabilité SHAP et la surveillance des dérives de modèle
- **NLP futur** (analyse d'avis voyageurs) : HuggingFace AutoTrain + modèle CamemBERT (French BERT)

---

*Benchmark réalisé dans le cadre du MSPR E6.4 — EPSI — Juin 2026*
