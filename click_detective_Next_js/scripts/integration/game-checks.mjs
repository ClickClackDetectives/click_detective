import assert from 'node:assert/strict';

/** 실제 API로 자료·쟁점·추론을 모으고 진행률과 고발 점수를 확인한다.
 * @param client 쿠키와 최신 상태를 보관하는 통합 검사 클라이언트.
 * @returns 진행률·점수 확인이 끝나면 완료되는 Promise.
 */
export async function completeInvestigation(client) {
  const recordsData = (await client.readCase('evidence.json')).records,
    findings = (await client.readCase('findings.private.json')).rules,
    inferences = (await client.readCase('inferences.private.json')).rules;
  for (const phase of [1, 2]) {
    for (const record of recordsData.filter((r) => r.phase === phase)) {
      await client.act('examinations', { evidence_id: record.id });
      const detail = await client.request(
        'materials/' + encodeURIComponent('evidence:' + record.id),
      );
      assert.ok(detail.illustration, record.id + ' 이미지 주소 누락');
      const imageUrl = detail.illustration.replace(/^\/v1\/games\/[^/]+\//, '');
      await client.request(imageUrl);
    }
    for (const rule of findings)
      if (
        !client.state.revealed.includes(rule.flag) &&
        rule.need.every((id) => client.state.examined.includes(id))
      )
        for (const id of rule.need)
          await client.act('interrogations', {
            suspect_id: rule.suspectId,
            question: '제시한 자료의 경위를 설명하세요.',
            material_id: id,
          });
    if (phase === 2)
      for (const suspect of ['cha', 'baek'])
        await client.act('interrogations', {
          suspect_id: suspect,
          question: '그날 밤의 동선을 설명하세요.',
          topic_id: 'movement',
        });
    const pending = inferences.filter((r) => r.phase === phase);
    while (pending.length) {
      const index = pending.findIndex((r) =>
        r.sources.every((s) => s.kind !== 'derived' || client.state.derivedEvidence[s.id]),
      );
      assert.ok(index >= 0);
      await client.act('inferences', { sources: pending[index].sources });
      pending.splice(index, 1);
    }
    if (phase === 1) await client.act('phase-transitions', { target_phase: 2 });
  }
  assert.equal(client.state.progress.percent, 100);
  for (const source of client.state.inferenceSources)
    await client.request('materials/' + encodeURIComponent(source.ref.kind + ':' + source.ref.id));
  await client.request('findings');
  const solution = (await client.readCase('solution.private.json')).solution;
  await client.act('accusations', {
    suspect_id: solution.suspectId,
    motive: solution.motive,
    method: solution.method,
    evidence_ids: Object.keys(client.state.derivedEvidence),
  });
  assert.equal(client.state.verdict.score, 100);
  assert.equal(client.state.verdict.correct, true);
}
