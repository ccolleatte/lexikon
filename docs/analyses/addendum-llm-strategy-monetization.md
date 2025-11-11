# 🔧 Addendum - Stratégie LLM Agnostique & Monétisation
## Use Case Principal : Writing Assistant Académique

**Date** : 2025-11-11
**Version** : v0.3.1
**Type** : Complément stratégique aux analyses UX

---

## 🎯 Insight Clé

**Lexikon n'est PAS un LLM competitor, c'est un enrichisseur sémantique**

### Use Case Principal à Garder en Tête

```
┌─────────────────────────────────────────────────┐
│ WRITING ASSISTANT ACADÉMIQUE                     │
├─────────────────────────────────────────────────┤
│ Chercheur rédige article → LLM assistance       │
│          ↓                                       │
│ Lexikon enrichit en back-office :               │
│ • Détecte termes ambigus                        │
│ • Injecte définitions contextuelles             │
│ • Suggère relations conceptuelles               │
│ • Assure cohérence terminologique               │
│          ↓                                       │
│ Sortie : Article avec terminologie rigoureuse   │
└─────────────────────────────────────────────────┘
```

**Implication** : Lexikon est un **middleware sémantique**, pas un endpoint utilisateur direct.

---

## 🔌 Architecture LLM-Agnostique

### Principe : BYOK (Bring Your Own Key)

Les utilisateurs avancés (développeurs, chercheurs avec budget) doivent pouvoir utiliser **leur propre LLM**.

#### Cas d'Usage Typiques

| Persona | LLM Préféré | Raison | Stratégie Lexikon |
|---------|-------------|--------|-------------------|
| **Chercheur avec grant** | GPT-4, Claude Opus | Qualité maximale, budget recherche | BYOK OpenAI/Anthropic |
| **Startup tech** | GPT-3.5, Mistral | Coût/performance | BYOK ou Openrouter |
| **Étudiant** | Gratuit (Llama, Mixtral) | Pas de budget | Openrouter free tier |
| **Entreprise** | On-premise (Llama fine-tuned) | Confidentialité | BYOK custom endpoint |

### Architecture Proposée

```yaml
# lexikon/config/llm_providers.yaml

providers:
  byok:
    - name: "openai"
      models: ["gpt-4", "gpt-3.5-turbo"]
      requires_user_key: true
      endpoint: "https://api.openai.com/v1"

    - name: "anthropic"
      models: ["claude-3-opus", "claude-3-sonnet"]
      requires_user_key: true
      endpoint: "https://api.anthropic.com/v1"

    - name: "custom"
      models: ["any"]
      requires_user_key: true
      endpoint: "user_provided"
      description: "On-premise ou autre provider"

  managed:
    - name: "openrouter_free"
      models: ["meta-llama/llama-3-8b", "mistralai/mixtral-8x7b"]
      requires_user_key: false
      cost: "free"
      rate_limit: "100 req/day"
      endpoint: "https://openrouter.ai/api/v1"

    - name: "lexikon_payg"
      models: ["gpt-3.5-turbo", "claude-3-haiku"]
      requires_user_key: false
      cost: "pay_as_you_go"
      pricing:
        input: "$0.002/1K tokens"
        output: "$0.006/1K tokens"
        markup: "20%"  # Marge Lexikon sur le coût LLM
```

### Interface Utilisateur - Configuration LLM

```
┌────────────────────────────────────────────────┐
│ ⚙️ CONFIGURATION LLM                            │
├────────────────────────────────────────────────┤
│ Comment voulez-vous utiliser les LLM ?         │
│                                                 │
│ ○ J'ai ma propre clé API (BYOK)                │
│   └─ Provider :                                 │
│      • OpenAI (GPT-4, GPT-3.5)                 │
│      • Anthropic (Claude)                      │
│      • Autre (endpoint custom)                 │
│   └─ Clé API : [●●●●●●●●●●●●●●●●] 🔒           │
│                                                 │
│ ○ Utiliser LLM gratuits (limité)              │
│   • Openrouter : Llama 3, Mixtral              │
│   • Limite : 100 requêtes/jour                 │
│   • Idéal pour : Tests, petits projets         │
│                                                 │
│ ○ Pay-as-you-go Lexikon                        │
│   • Pas de clé API nécessaire                  │
│   • €0.002/1K tokens entrée                    │
│   • €0.006/1K tokens sortie                    │
│   • Facturation mensuelle                      │
│   • Idéal pour : Usage variable                │
│                                                 │
│ [Sauvegarder configuration]                    │
└────────────────────────────────────────────────┘
```

---

## 💰 Modèle de Monétisation Révisé

### Problème Identifié

**Lexikon a deux sources de valeur distinctes** :
1. **Création/Validation ontologie** (HITL, curation)
2. **Consommation API** (enrichissement LLM)

Actuellement, le pricing mélange les deux.

### Solution : Séparer les Plans

#### Option 1 : Pricing Décomposé

```
┌──────────────────────────────────────────────┐
│ LEXIKON PRICING                               │
├──────────────────────────────────────────────┤
│                                               │
│ 📚 ONTOLOGY CREATION                          │
│ (Création, validation, curation)              │
│                                               │
│ • Free      : 1 ontologie, 100 termes        │
│ • Pro       : €49/mois - 1k termes           │
│ • Team      : €199/mois - 10k termes         │
│                                               │
│ 🔌 API CONSUMPTION                            │
│ (Enrichissement LLM, requêtes)                │
│                                               │
│ • BYOK      : Gratuit (votre clé LLM)        │
│ • Free tier : 100 req/jour (Openrouter)      │
│ • Pay-as-go : €0.002-0.006/1K tokens         │
│ • Enterprise: Volume discount                │
│                                               │
└──────────────────────────────────────────────┘
```

**Avantages** :
- ✅ Utilisateur contrôle ses coûts LLM
- ✅ Lexikon monétise sa vraie valeur (ontologie)
- ✅ BYOK = 0€ pour API si clé propre
- ✅ Freemium viable (Openrouter gratuit)

#### Option 2 : Bundle Intelligent

```
BUNDLES LEXIKON

┌─────────────────────────────────────────────┐
│ FREE - Quick Project                         │
├─────────────────────────────────────────────┤
│ Ontology : 1 domaine, 100 termes            │
│ API : 100 req/jour (Openrouter free)        │
│ LLM : BYOK illimité (si propre clé)         │
│ Support : Community                          │
│ Prix : €0                                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PRO - Research Project                       │
├─────────────────────────────────────────────┤
│ Ontology : 5 domaines, 1k termes            │
│ API : 1k req/jour (Openrouter)              │
│ LLM : BYOK illimité + €50 crédits PAYG      │
│ Support : Email 48h                          │
│ Prix : €49/mois                              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ TEAM - Production Integration                │
├─────────────────────────────────────────────┤
│ Ontology : Unlimited domains, 10k terms     │
│ API : 50k req/jour                           │
│ LLM : BYOK illimité + €200 crédits PAYG     │
│ Support : Priority, SLA 99.9%                │
│ Prix : €199/mois                             │
└─────────────────────────────────────────────┘
```

**Principe** : Bundle inclut des crédits PAYG, mais BYOK toujours gratuit et illimité.

---

## 🎓 Use Case Principal : Writing Assistant Académique

### Architecture d'Intégration

```
┌────────────────────────────────────────────────┐
│ APPLICATION UTILISATEUR (Front-office)         │
│                                                 │
│ • Notion, Overleaf, Google Docs                │
│ • Plugin custom "Academic Writer"              │
│ • IDE (VS Code, Obsidian)                      │
└────────────────┬───────────────────────────────┘
                 │ API call
                 ↓
┌────────────────────────────────────────────────┐
│ LEXIKON (Back-office / Middleware)             │
│                                                 │
│ 1. Reçoit texte brut + domaine                 │
│ 2. Détecte termes techniques (NER + fuzzy)     │
│ 3. Enrichit avec ontologie :                   │
│    • Définitions contextuelles                 │
│    • Relations conceptuelles                   │
│    • Synonymes et variantes                    │
│ 4. Retourne contexte sémantique structuré      │
└────────────────┬───────────────────────────────┘
                 │ Enriched prompt
                 ↓
┌────────────────────────────────────────────────┐
│ LLM (User's choice - BYOK ou Lexikon PAYG)    │
│                                                 │
│ • GPT-4, Claude, Llama, etc.                   │
│ • Génère texte enrichi sémantiquement          │
└────────────────┬───────────────────────────────┘
                 │ Generated text
                 ↓
┌────────────────────────────────────────────────┐
│ RETOUR À L'UTILISATEUR                         │
│                                                 │
│ • Texte académique rigoureux                   │
│ • Terminologie cohérente                       │
│ • Citations suggérées                          │
└────────────────────────────────────────────────┘
```

### Exemple Concret

#### Scénario : Chercheur écrit introduction d'article

**Input utilisateur** :
```
"J'écris sur l'aliénation dans le travail moderne.
Aide-moi à rédiger une introduction académique."
```

**Étape 1 : Lexikon détecte "aliénation"**
```json
{
  "term_detected": "aliénation",
  "domain": "SHS/Philosophie",
  "confidence": 0.95
}
```

**Étape 2 : Lexikon enrichit le prompt**
```json
{
  "original_prompt": "J'écris sur l'aliénation...",
  "enriched_context": {
    "term": "aliénation",
    "short_definition": "Perte de maîtrise de soi ou de sa production",
    "contextual_schools": [
      {
        "school": "Marx",
        "definition": "Dépossession quadruple du travailleur",
        "period": "1844-1867"
      },
      {
        "school": "École de Francfort",
        "definition": "Aliénation culturelle par l'industrie",
        "period": "1940-1970"
      }
    ],
    "key_relations": [
      {"type": "employs", "target": "travail"},
      {"type": "opposes", "target": "émancipation"}
    ],
    "citations": [
      "Marx, K. (1844). Manuscrits économico-philosophiques"
    ]
  }
}
```

**Étape 3 : Prompt envoyé au LLM (BYOK ou PAYG)**
```
Contexte sémantique :
- Terme : "Aliénation" (philosophie/sociologie)
- Définition Marx : Dépossession quadruple du travailleur (1844)
- Relations : emploie concept de "travail", opposé à "émancipation"
- École de Francfort : Extension culturelle (1940-1970)

Requête utilisateur :
"J'écris sur l'aliénation dans le travail moderne.
Aide-moi à rédiger une introduction académique."

Consignes :
- Utiliser la terminologie rigoureuse fournie
- Citer les sources appropriées
- Distinguer les écoles de pensée
- Ton : académique, précis
```

**Étape 4 : LLM génère introduction enrichie**
```
Introduction générée :

Le concept d'aliénation, tel que formalisé par Marx dans ses
Manuscrits de 1844, désigne le processus de dépossession du
travailleur au sein du mode de production capitaliste. Cette
notion, centrale en philosophie sociale, s'oppose dialectiquement
au concept d'émancipation. L'École de Francfort (1940-1970) a
étendu cette analyse au domaine culturel, montrant comment
l'industrie culturelle reproduit les mécanismes d'aliénation...

[Citer : Marx, K. (1844). Manuscrits économico-philosophiques]
```

### Valeur Ajoutée Lexikon

Sans Lexikon :
```
"L'aliénation au travail est un problème..."
→ Vague, pas de rigueur terminologique
→ Pas de distinction Marx/Hegel/École de Francfort
→ LLM génère du contenu générique
```

Avec Lexikon :
```
"Le concept d'aliénation (Marx, 1844) désigne
la dépossession quadruple..."
→ Précis, contextualisé, sourcé
→ Distinctions école de pensée claires
→ LLM génère contenu académiquement rigoureux
```

**ROI utilisateur** :
- Temps économisé : 2-3h recherche biblio
- Qualité améliorée : Citations justes, terminologie précise
- Réduction erreurs : -30% erreurs conceptuelles

---

## 🆓 Stratégie Freemium Révisée

### Que Limiter en Free Tier ?

#### ❌ À NE PAS Limiter (Sinon perte use case principal)
- ✅ Enrichissement sémantique de base (détection + définitions)
- ✅ BYOK illimité (si user a sa clé LLM)
- ✅ API read-only (consultation ontologie)
- ✅ Export ontologie (JSON-LD, RDF)

**Raison** : Writing assistant académique doit fonctionner en free tier avec BYOK.

#### ✅ À Limiter en Free Tier

| Fonctionnalité | Free | Pro | Team |
|----------------|------|-----|------|
| **Création ontologie** | 100 termes | 1k termes | 10k termes |
| **Domaines** | 1 public | 5 privés | Unlimited |
| **Validation HITL** | Self-serve | Queue priorité | Experts dédiés |
| **API write** (création termes) | 10 termes/jour | 100/jour | Unlimited |
| **Relations suggérées (AI)** | 3/terme | 10/terme | Unlimited |
| **Enrichissement avancé** | Niveau 1 (minimal) | Niveau 2 (balanced) | Niveau 3 (full) |
| **LLM calls (managed)** | 100 req/jour (Openrouter) | 1k req/jour + €50 | 50k + €200 |
| **BYOK (propre clé)** | ✅ Illimité | ✅ Illimité | ✅ Illimité |
| **Support** | Community | Email 48h | Priority SLA |
| **Export formats** | JSON | JSON, JSON-LD | All (RDF, OWL, SKOS) |
| **Versioning** | Dernier only | 10 versions | Unlimited |
| **Collaboration** | Solo | 3 users | Unlimited |

### Principe Clé

```
┌─────────────────────────────────────────────┐
│ FREEMIUM PHILOSOPHY                          │
├─────────────────────────────────────────────┤
│                                              │
│ ✅ Use case "writing assistant" fonctionne  │
│    en FREE avec BYOK                         │
│                                              │
│ ✅ Limites sur :                             │
│    • Volume création (10 termes/jour)       │
│    • Profondeur enrichissement (niveau 1)   │
│    • Fonctions avancées (validation HITL)   │
│                                              │
│ ❌ PAS de paywall sur :                      │
│    • Consultation ontologie publique        │
│    • Enrichissement sémantique de base      │
│    • BYOK illimité                          │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 🏗️ Implémentation Technique

### API Endpoint : LLM-Agnostic Enrichment

```python
# POST /api/v1/enrich
{
  "text": "J'écris sur l'aliénation...",
  "domain": "SHS",
  "enrichment_level": "minimal" | "balanced" | "full",
  "llm_config": {
    "mode": "byok" | "openrouter_free" | "lexikon_payg",
    "provider": "openai" | "anthropic" | "openrouter" | "custom",
    "model": "gpt-4" | "claude-3-opus" | "llama-3-8b",
    "api_key": "sk-..." | null,  # Si BYOK
    "endpoint": "https://..." | null  # Si custom
  }
}
```

### Response

```json
{
  "enriched_context": {
    "terms_detected": [...],
    "semantic_context": {...},
    "tokens_used": {
      "input": 342,
      "enrichment": 89
    }
  },
  "llm_response": {
    "generated_text": "...",
    "model_used": "gpt-4",
    "tokens": {
      "input": 431,  # 342 original + 89 enrichment
      "output": 567
    },
    "cost": {
      "llm_provider": "$0.012",  # Si BYOK, c'est user qui paie
      "lexikon_fee": "$0.003"    # Si PAYG, markup 20%
    }
  },
  "user_balance": {
    "credits_remaining": 47.50,  # Si PAYG
    "req_remaining_today": 89    # Si free tier
  }
}
```

### Architecture Backend

```python
# lexikon/services/llm_router.py

class LLMRouter:
    """Route requests to appropriate LLM provider"""

    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'openrouter': OpenRouterProvider(),
            'custom': CustomProvider()
        }

    async def enrich_and_generate(
        self,
        text: str,
        domain: str,
        llm_config: LLMConfig,
        user: User
    ):
        # 1. Enrichissement Lexikon (toujours gratuit sauf limites tier)
        enrichment = await self.enrich_semantic(text, domain, user.tier)

        # 2. Check user entitlement
        if llm_config.mode == "byok":
            # User provided API key → unlimited, Lexikon doesn't bill
            provider = self.get_provider(llm_config.provider)
            api_key = llm_config.api_key
            cost_to_user = None  # User billed directly by provider

        elif llm_config.mode == "openrouter_free":
            # Free tier with rate limit
            if not user.check_rate_limit(100, "daily"):
                raise RateLimitError("100 req/day exceeded")
            provider = self.providers['openrouter']
            api_key = settings.OPENROUTER_KEY
            cost_to_user = 0

        elif llm_config.mode == "lexikon_payg":
            # Lexikon bills with markup
            if user.credits_balance < 0.01:
                raise InsufficientCreditsError()
            provider = self.get_provider(llm_config.provider)
            api_key = settings.LEXIKON_LLM_KEY  # Lexikon's key
            cost_to_user = "calculated"  # Bill to user balance

        # 3. Build enriched prompt
        prompt = self.build_prompt(text, enrichment)

        # 4. Call LLM
        response = await provider.generate(
            prompt=prompt,
            model=llm_config.model,
            api_key=api_key
        )

        # 5. Bill if PAYG
        if cost_to_user == "calculated":
            cost = self.calculate_cost(response.tokens, llm_config.model)
            await user.debit_credits(cost)

        return {
            'enriched_context': enrichment,
            'llm_response': response,
            'cost': cost_to_user
        }
```

---

## 📊 Revised Metrics by Adoption Level

### Quick Project (with BYOK or Free Tier)

```
Activation :
- Sign-up to first enrichment: < 30 min
- BYOK setup success: > 80%
- Openrouter fallback: < 10s

Engagement :
- Enrichments/day: 10-50 (free tier OK)
- Documents processed: 5-20
- Active period: 1-6 months

Conversion :
- BYOK users → Paid (ontology): 15%
  (Reason: Want to create custom ontology)
- Free tier → PAYG: 5%
  (Reason: Rate limit hit, no own key)
```

### Research Project (with BYOK + Pro Plan)

```
Value proposition :
- BYOK unlimited (own GPT-4 key)
- Lexikon Pro (€49) for ontology creation
- Total cost: €49 + personal LLM budget

Metrics :
- Ontology creation: 100-500 terms
- Enrichments/day: 100-200
- LLM budget control: User manages directly
- Lexikon value: Ontology + enrichment, not LLM cost
```

### Production Integration (BYOK + Team Plan)

```
Architecture :
- BYOK for production (cost control, compliance)
- Lexikon Team (€199) for unlimited ontology
- Optional PAYG for variable workloads

Metrics :
- API calls/day: 1k-100k
- 95% use BYOK (own LLM budget)
- 5% use PAYG (variable, testing)
- Lexikon revenue: €199 subscription (not LLM fees)
```

---

## 🎯 Strategic Recommendations

### 1. Position Lexikon Comme Middleware, Pas LLM Provider

**Message marketing** :
```
"Lexikon enrichit vos LLM avec contexte sémantique expert.
Utilisez le LLM de votre choix (GPT, Claude, Llama, etc.)."
```

**Pas** :
```
"Lexikon is an AI assistant powered by..."
```

### 2. BYOK = Free Forever (Unlimited)

- Zero friction pour développeurs avancés
- Pas de compétition avec OpenAI/Anthropic
- Monétisation sur vraie valeur ajoutée (ontologie)

### 3. Freemium Généreux pour Writing Assistant

```
Étudiant peut :
✅ Utiliser writing assistant avec sa clé GPT-3.5 (BYOK)
✅ Enrichir 100 termes/jour (suffisant pour thèse)
✅ Exporter ontologie finale (JSON-LD)

Étudiant ne peut pas :
❌ Créer ontologie privée >100 termes (→ Pro €49)
❌ Validation HITL experte (→ Pro €49)
❌ Enrichissement avancé niveau 3 (→ Team €199)
```

### 4. PAYG = Convenience, Pas Obligation

- Pour users sans clé API propre
- Pour workloads variables (test/dev)
- Markup raisonnable (20%, pas 200%)

### 5. Transparence Coûts LLM

```
Dashboard utilisateur :

┌────────────────────────────────────┐
│ VOS COÛTS (30 derniers jours)      │
├────────────────────────────────────┤
│ Lexikon Pro : €49.00               │
│   • Ontology creation & hosting    │
│                                     │
│ LLM (BYOK - GPT-4) : €87.50       │
│   • 2.3M tokens (votre compte)     │
│   • Facturé par OpenAI             │
│                                     │
│ Total : €136.50                    │
│   • Lexikon : €49.00 (36%)        │
│   • LLM : €87.50 (64%)            │
└────────────────────────────────────┘

💡 Astuce : Passez à GPT-3.5 pour réduire
   vos coûts LLM de 90% (€87.50 → €8.75)
```

---

## 🏁 Bottom Line

### Nouvelle Philosophie Produit

```
┌──────────────────────────────────────────┐
│ LEXIKON = SEMANTIC ENRICHMENT LAYER      │
│                                           │
│ Pas un competitor LLM                    │
│ Pas un wrapper LLM                       │
│                                           │
│ Un middleware sémantique universel       │
│ Compatible avec TOUS les LLM             │
│ Monétisé sur l'ontologie, pas les tokens│
└──────────────────────────────────────────┘
```

### Use Case Driving Design

**Writing Assistant Académique** (back-office) :
- User écrit dans son outil (Notion, Overleaf, etc.)
- Lexikon enrichit en arrière-plan
- LLM génère avec contexte ontologique
- Output : Texte académiquement rigoureux

→ BYOK must be free & unlimited
→ Freemium doit permettre ce flow
→ Monétisation sur création ontology, pas consommation

### Next Steps

1. **Valider architecture LLM-agnostic** avec 2-3 early adopters
2. **POC BYOK** : OpenAI + Anthropic + Openrouter
3. **Dashboard transparence coûts** (mockup)
4. **Revoir pricing tiers** selon nouvelle stratégie
5. **Messaging** : "Semantic middleware" pas "AI assistant"

---

**Status** : Strategic pivot, requires validation workshop
**Impact** : High - Changes monetization model & positioning
**Risk** : Low - Increases flexibility, reduces LLM competition
**Next Action** : 2-hour workshop to validate BYOK-first strategy

*Ce document reformule Lexikon comme middleware sémantique LLM-agnostic, avec BYOK gratuit illimité et monétisation sur l'ontologie (vraie valeur ajoutée).*
