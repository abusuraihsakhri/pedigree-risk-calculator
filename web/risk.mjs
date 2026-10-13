/** Known-genotype Mendelian model; no network, storage or personal data. */
export const modes = {
  autosomal_dominant: 'Autosomal dominant',
  autosomal_recessive: 'Autosomal recessive',
  x_linked_dominant: 'X-linked dominant',
  x_linked_recessive: 'X-linked recessive',
};

export const genotypeOptions = (mode) => {
  if (!(mode in modes)) throw new Error('Invalid inheritance mode');
  return mode.startsWith('autosomal')
    ? { mother: ['AA', 'Aa', 'aa'], father: ['AA', 'Aa', 'aa'] }
    : { mother: ['XAXA', 'XAXa', 'XaXa'], father: ['XAY', 'XaY'] };
};

function gametes(alleles) {
  const result = {};
  for (const allele of alleles) result[allele] = (result[allele] || 0) + 1 / alleles.length;
  return result;
}

function outcomes(genotypes, mode, sex) {
  let affected = 0, unaffected_carrier = 0;
  for (const [genotype, p] of Object.entries(genotypes)) {
    const hasDisease = mode.startsWith('autosomal') ? genotype.includes('A') : genotype.includes('a');
    let isAffected, isCarrier = false;
    if (mode === 'autosomal_dominant') isAffected = hasDisease;
    else if (mode === 'autosomal_recessive') {
      isAffected = genotype === 'aa';
      isCarrier = genotype === 'Aa';
    } else if (sex === 'sons') isAffected = genotype === 'XaY';
    else if (mode === 'x_linked_dominant') isAffected = hasDisease;
    else {
      isAffected = genotype === 'XaXa';
      isCarrier = genotype === 'XAXa';
    }
    if (isAffected) affected += p;
    else if (isCarrier) unaffected_carrier += p;
  }
  return { affected, unaffected_carrier,
    unaffected_noncarrier: 1 - affected - unaffected_carrier };
}

export function calculateRisk(mode, mother, father) {
  const options = genotypeOptions(mode);
  if (!options.mother.includes(mother) || !options.father.includes(father))
    throw new Error('Invalid parental genotype for selected inheritance mode');

  const genotypes = {};
  if (mode.startsWith('autosomal')) {
    const crosses = {};
    for (const [m, mp] of Object.entries(gametes(mother))) {
      for (const [f, fp] of Object.entries(gametes(father))) {
        const geno = [m, f].sort((a, b) => a === b ? 0 : a === 'A' ? -1 : 1).join('');
        crosses[geno] = (crosses[geno] || 0) + mp * fp;
      }
    }
    const ordered = Object.fromEntries(['AA', 'Aa', 'aa'].filter(g => crosses[g]).map(g => [g, crosses[g]]));
    genotypes.sons = { ...ordered };
    genotypes.daughters = { ...ordered };
  } else {
    const maternal = { XAXA: 'AA', XAXa: 'Aa', XaXa: 'aa' }[mother];
    const paternal = { XAY: 'A', XaY: 'a' }[father];
    const sons = {}, daughters = {};
    for (const [allele, p] of Object.entries(gametes(maternal))) {
      sons['X' + allele + 'Y'] = p;
      const pair = [allele, paternal].sort((a, b) => a === b ? 0 : a === 'A' ? -1 : 1);
      const daughter = 'X' + pair[0] + 'X' + pair[1];
      daughters[daughter] = (daughters[daughter] || 0) + p;
    }
    genotypes.sons = Object.fromEntries(['XAY', 'XaY'].filter(g => sons[g]).map(g => [g, sons[g]]));
    genotypes.daughters = Object.fromEntries(['XAXA', 'XAXa', 'XaXa'].filter(g => daughters[g]).map(g => [g, daughters[g]]));
  }
  const sons = outcomes(genotypes.sons, mode, 'sons');
  const daughters = outcomes(genotypes.daughters, mode, 'daughters');
  const overall = Object.fromEntries(Object.keys(sons).map(k => [k, (sons[k] + daughters[k]) / 2]));
  return { inheritance: mode, mother, father, genotypes,
    risk: { overall, sons, daughters },
    assumptions: 'Known genotypes; one locus; complete penetrance; equal Mendelian segregation; equal probability of male/female offspring; no new variants, mosaicism, or linked loci.' };
}
