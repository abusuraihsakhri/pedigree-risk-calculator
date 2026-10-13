"""Mendelian recurrence probabilities for *known parental genotypes*.

Assumes single-locus inheritance, equal transmission of parental alleles,
complete penetrance, no de novo variants or mosaicism, and a 1:1 sex ratio.
It does not infer genotype probabilities from an ungenotyped pedigree.
"""
from collections import Counter

AUTOSOMAL = ("autosomal_dominant", "autosomal_recessive")
XLINKED = ("x_linked_dominant", "x_linked_recessive")
MODES = AUTOSOMAL + XLINKED


def _gametes(alleles):
    return {allele: alleles.count(allele) / len(alleles) for allele in set(alleles)}


def _summarize(genotypes, mode, sex):
    affected = carrier = 0.0
    for genotype, probability in genotypes.items():
        if mode == "autosomal_dominant":
            is_affected = "A" in genotype
            is_carrier = False
        elif mode == "autosomal_recessive":
            is_affected = genotype == "aa"
            is_carrier = genotype == "Aa"
        elif sex == "sons":
            is_affected = genotype == "XaY"
            is_carrier = False
        elif mode == "x_linked_dominant":
            is_affected = "a" in genotype
            is_carrier = False
        else:
            is_affected = genotype == "XaXa"
            is_carrier = genotype == "XAXa"
        if is_affected:
            affected += probability
        elif is_carrier:
            carrier += probability
    return {"affected": round(affected, 12),
            "unaffected_carrier": round(carrier, 12),
            "unaffected_noncarrier": round(1 - affected - carrier, 12)}


def calculate_recurrence_risk(inheritance, mother, father):
    """Return sex-stratified recurrence probabilities for known parent genotypes.

    Autosomal: AA/Aa/aa for each parent, with AD disease allele A and AR a.
    X-linked: maternal XAXA/XAXa/XaXa, paternal XAY/XaY; disease allele a.
    """
    if inheritance not in MODES:
        raise ValueError("inheritance must be one of: " + ", ".join(MODES))
    if inheritance in AUTOSOMAL:
        valid = ("AA", "Aa", "aa")
        if mother not in valid or father not in valid:
            raise ValueError("Autosomal parent genotypes must be AA, Aa, or aa")
        maternal, paternal = _gametes(mother), _gametes(father)
        results = Counter()
        for m, pm in maternal.items():
            for f, pf in paternal.items():
                genotype = "".join(sorted((m, f), key=lambda a: (a.islower(), a)))
                results[genotype] += pm * pf
        ordered = {g: round(results[g], 12) for g in valid if results[g]}
        genotype_probs = {"sons": ordered.copy(), "daughters": ordered.copy()}
    else:
        mothers = {"XAXA": "AA", "XAXa": "Aa", "XaXa": "aa"}
        fathers = {"XAY": "A", "XaY": "a"}
        if mother not in mothers or father not in fathers:
            raise ValueError("X-linked genotypes: mother XAXA/XAXa/XaXa; father XAY/XaY")
        maternal = _gametes(mothers[mother])
        sons = {f"X{a}Y": round(p, 12) for a, p in maternal.items()}
        daughters = Counter()
        for a, p in maternal.items():
            pair = "".join(sorted((a, fathers[father]), key=lambda x: x.islower()))
            daughters["X" + pair[0] + "X" + pair[1]] += p
        genotype_probs = {
            "sons": {g: sons[g] for g in ("XAY", "XaY") if g in sons},
            "daughters": {g: round(daughters[g], 12)
                          for g in ("XAXA", "XAXa", "XaXa") if daughters[g]},
        }

    s = _summarize(genotype_probs["sons"], inheritance, "sons")
    d = _summarize(genotype_probs["daughters"], inheritance, "daughters")
    overall = {key: round((s[key] + d[key]) / 2, 12) for key in s}
    return {
        "inheritance": inheritance,
        "mother": mother,
        "father": father,
        "risk": {"overall": overall, "sons": s, "daughters": d},
        "genotypes": genotype_probs,
        "assumptions": "Known genotypes; one locus; complete penetrance; equal Mendelian segregation; equal probability of male/female offspring; no new variants, mosaicism, or linked loci.",
    }
