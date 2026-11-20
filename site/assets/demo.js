// Replays evidence/demo.json, recorded by `python -m automation.demo` against the real API and a temporary database.
const $ = id => document.getElementById(id);
const run = await (await fetch('assets/demo-run.json')).json();
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const j = o => `<pre class="cs-pre">${esc(JSON.stringify(o, null, 2))}</pre>`;
const a = run.audit;
const STEPS = [
  ['1 · Agent proposes', 'synthetic-agent', `The agent calls <code>ProposeDossierTask</code> for dossier <b>${run.initial.payload.dossier}</b>. The server stores it as <span class="pill warn">${run.initial.state}</span>; nothing is executed.`, j(run.initial), [a[0]]],
  ['2 · Execute without approval', 'synthetic-executor', `Trying to execute before a reviewer decided returns <span class="pill bad">HTTP ${run.without_approval_http}</span>. The state machine, not the chat, decides what may happen next.`, j({ request: 'POST /requests/{id}/execute', response: run.without_approval_http, detail: 'Human approval required' }), [a[0]]],
  ['3 · Reviewer approves', run.final.reviewer, `A separate reviewer key records the decision with a reason: “${esc(run.final.reason)}”. A Copilot message saying “approved” would not count.`, j({ decision: 'approve', reviewer: run.final.reviewer, reason: run.final.reason }), a.slice(0, 2)],
  ['4 · Executor runs it once', 'synthetic-executor', `The executor creates one local mock task and the request becomes <span class="pill ok">${run.final.state}</span>. External calls made: <b>${run.external_calls}</b> (no mail, Teams, Dataverse or ERP).`, j(run.final), a],
];
function show(i) {
  document.querySelectorAll('#cs-steps button').forEach((b, k) => b.setAttribute('aria-selected', k === i));
  const [t, actor, text, body, audit] = STEPS[i];
  $('cs-stage').innerHTML = `<div class="cs-two"><div><div class="small dim">Actor: <b>${esc(actor)}</b></div><p>${text}</p>${body}</div>
    <div><div class="small dim">Audit trail at this point</div><ol class="cs-audit">${audit.map(e => `<li><span class="mono">#${e.seq}</span> <b>${esc(e.action)}</b> <span class="dim">by ${esc(e.actor)}</span></li>`).join('')}</ol></div></div>`;
}
$('cs-steps').innerHTML = STEPS.map((s, i) => `<button type="button" data-i="${i}">${s[0]}</button>`).join('');
$('cs-steps').addEventListener('click', e => { const b = e.target.closest('button'); if (b) show(+b.dataset.i); });
show(0);
