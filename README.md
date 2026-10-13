# Pedigree Risk Calculator

A Mendelian recurrence-probability calculator for **known parental genotypes**, with a self-contained browser application, a Python CLI, CSV batch processing, and an optional FastAPI endpoint.

The calculator models **autosomal dominant (AD)**, **autosomal recessive (AR)**, **X-linked dominant (XLD)** and **X-linked recessive (XLR)** inheritance. It reports offspring genotype frequencies and affected/unaffected probabilities for sons, daughters, and all births.

> **Scope:** This is conditional single-locus Mendelian arithmetic, **not** a generalized pedigree-analysis engine. It does not infer genotypes from family history, calculate Bayesian carrier probabilities, or estimate clinical disease penetrance. Educational/research use only; genetic counselling is required for patient-specific interpretation.

## Browser application

Serve the static folder with any local HTTP server (ES modules require HTTP rather than opening the HTML directly):

\`\`\`bash
python -m http.server 8080 --directory web
\`\`\`

Open http://localhost:8080/ and select an inheritance pattern and both parental genotypes. Results update immediately. The JSON export contains the selected genotypes, sex-specific genotype and risk distributions, and model assumptions.

The browser calculation needs **no server-side Python, API keys, Pyodide, external fonts, or network calls**. GitHub Pages deployment is defined in \`.github/workflows/pages.yml\`; publishing depends on Pages being enabled and a successful deployment.

## Python CLI

Requires Python 3.10+; the inheritance engine itself uses only the standard library.

\`\`\`bash
python pedigree.py risk --inheritance autosomal_recessive --mother Aa --father Aa
python pedigree.py risk --inheritance autosomal_dominant --mother Aa --father aa
python pedigree.py risk --inheritance x_linked_recessive --mother XAXa --father XAY
python pedigree.py risk --inheritance x_linked_dominant --mother XAXA --father XaY
python pedigree.py batch --input sample_pedigrees.csv --output results.csv
\`\`\`

The AR \`Aa × Aa\` cross yields 25% affected, 50% unaffected carriers, and 25% unaffected noncarriers per pregnancy. The XLR \`XAXa × XAY\` cross yields 50% affected sons and 50% unaffected-carrier daughters, corresponding to 25% affected across all births when a 1:1 sex ratio is assumed.

The batch CSV has \`inheritance,mother,father\` columns and exports flattened probability columns plus genotype distributions. See [sample_pedigrees.csv](sample_pedigrees.csv). Invalid genotypes raise an error in the \`risk\` command or produce an \`error\` field per CSV row.

### Allele conventions

| Inheritance | Mother | Father | Disease allele |
| --- | --- | --- | --- |
| AD | AA, Aa, aa | AA, Aa, aa | A (dominant) |
| AR | AA, Aa, aa | AA, Aa, aa | a (recessive) |
| XLD | XAXA, XAXa, XaXa | XAY, XaY | Xa (dominant) |
| XLR | XAXA, XAXa, XaXa | XAY, XaY | Xa (recessive) |

Here \`XAXa\` represents a female heterozygote, while \`XaY\` represents a male hemizygote for the disease variant. **Unaffected carrier** is used only where the modeled variant is recessive.

## Optional backend and legacy tools

Install the bounded dependencies and launch the local API:

\`\`\`bash
python -m pip install -r requirements.txt
python cli.py serve --host 127.0.0.1 --port 8000
\`\`\`

The UI is available at http://127.0.0.1:8000/, and \`POST /api/risk\` accepts \`{"inheritance":"autosomal_recessive","mother":"Aa","father":"Aa"}\`. Interactive API documentation is at \`/docs\`.

The repository also retains its pre-existing clinical calculations (\`pedigree.py single\`) and separate prototype \`cli.py\` audit/agent workflows. These are **not validated clinical decision-support models**. In particular, its pediatric BMI z-score is only an approximation, and its generic score is not a clinical recurrence model. The audit component requires \`AUDIT_SECRET_KEY\` (at least 16 characters); see \`.env.example\`. Its PHI-pattern filter is not comprehensive de-identification, and the mock chat service performs no real model inference. Do not expose the optional audit API publicly or send patient identifiers to it without an independent security/privacy review.

## Model assumptions and privacy

Calculations assume a single independent locus, complete penetrance, equal parental allele segregation and a 1:1 male/female birth ratio. No de novo mutations, gonadal mosaicism, variable expressivity, linkage, selection or genotype uncertainty are modeled. Sex-specific probabilities are conditional on offspring sex; all-birth probabilities weight sons and daughters equally.

The browser version does not request identifiers, use browser storage, or transmit inputs to a server. Export files are generated locally. In contrast, the optional API processes submitted data in the Python server process and its audit component retains an in-memory trail.

## Testing and development

\`\`\`bash
python -m pip install -r requirements.txt
python -m pytest -q
node --test web/test-risk.mjs
python -m compileall -q agents cli.py pedigree.py inheritance.py
\`\`\`

CI runs the Python test suite on Python 3.10–3.12 and Node's browser-math tests. The frontend uses modern HTML/CSS and standard JavaScript ES modules (current Chromium, Firefox and Safari).

**License:** [MIT](LICENSE).
