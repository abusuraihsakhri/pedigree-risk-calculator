import assert from 'node:assert/strict';
import test from 'node:test';
import { calculateRisk, genotypeOptions } from './risk.mjs';

test('autosomal dominant Aa × aa: half affected', () => {
  const r = calculateRisk('autosomal_dominant', 'Aa', 'aa');
  assert.equal(r.risk.overall.affected, 0.5);
});
test('recessive carrier × carrier: quarter affected', () => {
  const r = calculateRisk('autosomal_recessive', 'Aa', 'Aa');
  assert.deepEqual(r.risk.overall, { affected: 0.25, unaffected_carrier: 0.5, unaffected_noncarrier: 0.25 });
});
test('XLR carrier mother, unaffected father: sons 50% affected, daughters 50% carrier', () => {
  const r = calculateRisk('x_linked_recessive', 'XAXa', 'XAY');
  assert.equal(r.risk.sons.affected, 0.5);
  assert.equal(r.risk.daughters.affected, 0);
  assert.equal(r.risk.daughters.unaffected_carrier, 0.5);
  assert.equal(r.risk.overall.affected, 0.25);
});
test('XLD affected father to all daughters, no sons', () => {
  const r = calculateRisk('x_linked_dominant', 'XAXA', 'XaY');
  assert.equal(r.risk.daughters.affected, 1);
  assert.equal(r.risk.sons.affected, 0);
});
test('rejects invalid mode and genotypes', () => {
  assert.throws(() => genotypeOptions('other'));
  assert.throws(() => calculateRisk('autosomal_dominant', 'XAXa', 'aa'));
  assert.throws(() => calculateRisk('x_linked_recessive', 'XAY', 'XAXa'));
});
test('all distributions sum to 1', () => {
  for (const [mode, mother, father] of [
    ['autosomal_dominant', 'Aa', 'Aa'],
    ['autosomal_recessive', 'aa', 'Aa'],
    ['x_linked_recessive', 'XaXa', 'XaY'],
    ['x_linked_dominant', 'XAXa', 'XaY'],
  ]) {
    const r = calculateRisk(mode, mother, father);
    for (const sex of ['overall', 'sons', 'daughters'])
      assert.ok(Math.abs(Object.values(r.risk[sex]).reduce((a,b)=>a+b,0) - 1) < 1e-12);
    for (const sex of ['sons', 'daughters'])
      assert.ok(Math.abs(Object.values(r.genotypes[sex]).reduce((a,b)=>a+b,0) - 1) < 1e-12);
  }
});
