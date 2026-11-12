# Subtask evidence — design

Date: 2026-11-08
Status: approved
Scope: the `ai-daridev` skills repo. No Odoo schema changes.

## Problem

A step can flip to `1_done` because the tests passed, but the subtask carries no
human-verifiable proof. A user or admin opening the card sees a state and a detail line, not the
thing that actually worked. The evidence has to live on the step's subtask:

- a screenshot for a UI, page or metric check;
- the curl and its response in a code block for an API check;
- screenshots of the process plus the exported file for an export.

## Decisions

- Every completed step carries at least one evidence artifact. No artifact → no `1_done` unless the
  user records an explicit waiver.
- `pair` infers the evidence type from the step when the step completes and asks once only when it
  is ambiguous.
- Screenshots are attached and embedded in the subtask description.
- Browser work uses the `playwright-cli` skill. If it is unavailable, `pair` asks for the screenshot
  and leaves the step open.
- `ir.attachment` is allowed read/create only, scoped to `project.task` attachments. The suite never
  deletes an attachment.
- Secrets are always redacted; client data is masked unless the step is about that data.
- `review` fails a `1_done` step with no evidence, and `archive` refuses to close a card with such
  a step.
- `story` and `check-plan` preserve the evidence block when they rewrite a step.

## Evidence contract

| Step looks like | Evidence |
|---|---|
| UI, page, metric, visual change | Screenshot via `playwright-cli`, embedded |
| API, endpoint, curl, HTTP | Command plus response in a `<pre><code>` block |
| Export, download, document | Process screenshots plus the file attached |
| Code-only, refactor | The relevant diff hunk, or the command output |
| Infra, n8n, server | Command output plus a screenshot of the result |

Ambiguous → one question to the user. No artifact possible → a waiver, recorded in the subtask, never
silent.

The subtask description becomes:

```html
<p>{detail}</p>
<h3>Evidence</h3>
<p><b>2026-11-08 18:45:12 UTC</b></p>
<ul>
  <li><b>screenshot</b><br/><img src="/web/image/{attachment_id}" alt="evidence" style="max-width:100%"/></li>
  <li><b>curl</b><pre><code>curl -s ...\nHTTP/1.1 200 OK\n{"ok": true}</code></pre></li>
  <li><b>file</b> <a href="/web/content/{attachment_id}?download=true">export.xlsx</a></li>
</ul>
```

One `Evidence` section per subtask. Each attempt appends one date paragraph and one `<ul>`; a second
attempt appends another `<p><b>{UTC}</b></p>` plus its `<ul>` after the previous entry. The date is
`YYYY-MM-DD HH:MM:SS UTC`, so two attempts in the same minute remain distinct. Previous entries are
never overwritten. An attempt is appended only after the capture and upload succeed, or when a
waiver is recorded; a failed retry appends nothing.

Labels are `screenshot`, `curl`, `output`, `diff`, `file` and `waiver`; each `<li>` starts with
`<b>{label}</b>`. `screenshot` and `file` carry an attachment id that must resolve. `curl`, `output`
and `diff` carry a non-empty `<pre><code>` block. `waiver` carries the reason, who and date. Escape
`<`, `>`, `&` in commands, responses, file names and the waiver reason.

A waiver is an `<li>` in the attempt's `<ul>`:

```html
<li><b>waiver</b> — no visual artifact available — user, 2026-11-08 19:02:40 UTC</li>
```

`pair` records it after the user says it in the conversation, including for a `[you]` step. A
`[agent]` step also needs an artifact or a waiver; the user's instruction is the only source of a
waiver. `review` treats a `1_done` step as valid when the latest attempt has at least one artifact or
a waiver.

## Pair flow

1. Tests green, or the non-code verification is shown.
2. Infer the evidence type. Ask once if ambiguous.
3. Capture with `playwright-cli` for anything that opens a page; otherwise run the command or read
   the file.
4. Redact secrets; mask client data; compress the screenshot.
5. Upload to `ir.attachment`: `name`, `datas` base64, `res_model=project.task`, `res_id=<subtask>`,
   `mimetype`. Read back the id.
6. Append the evidence HTML to the subtask description; keep the detail above it.
7. Re-read the subtask: the attachment exists and the description contains `Evidence`.
8. Flip the step to `1_done` only after step 7 passes. On failure, stop; the step stays open.
9. `[you]` steps: the user provides the artifact or the waiver; pair uploads and records it the same
   way.
10. Without Odoo: print the evidence and the exact place to paste it; no upload.

Evidence is written in the step's stop, not batched to the close gate: pair reports the attachment
and the description in that stop, and the MCP write approval (or your yes on that stop when the MCP
does not prompt) is the only approval. The close gate only summarises the evidence already
recorded. The `ir.attachment` model exception is a manual edit to
`~/.config/opencode/AGENTS.md`; `install.sh` and `--check` do not manage that block.

### Screenshot pipeline

Captures go to `/tmp/opencode/evidence/<slug>/<sanitized-step>/`; the step segment is kebab-case, with
no spaces or slashes. Pair never writes captures into the repo. After the subtask re-read (step 7)
succeeds, `rm -rf` that directory; if the cleanup fails, report the directory. On a description
failure the files stay for the retry.

1. `playwright-cli resize 1600 1000` — width never exceeds 1600.
2. `playwright-cli screenshot --filename="$dir/shot.png"`.
3. `convert "$dir/shot.png" -resize '1600x>' -strip -quality 82 "$dir/shot.jpg"`.
4. If the JPEG is still over 500 KB, `convert "$dir/shot.jpg" -resize '1280x>' -quality 75 "$dir/shot2.jpg"` then `mv "$dir/shot2.jpg" "$dir/shot.jpg"`.
5. If it is still over 500 KB, stop and ask for a smaller screenshot.
6. Redact before upload: prefer a test account or test data; when the real page is required, crop or
   blur the sensitive region with `convert` before uploading. Never upload first and redact later.
7. No `convert` on the machine → use the viewport cap and ask for a smaller screenshot when the file
   exceeds 500 KB.

### Attachment failure and orphans

If the upload succeeds and the description write fails, the step stays open. Report the attachment
id and leave the orphan in place (the suite never deletes). On retry, reuse the same id when the
recorded name and byte size match the file; otherwise create a new attachment and report the old
orphan.

## Preservation and review

- `story` and `check-plan` split the subtask description at `<h3>Evidence</h3>`. They update the
  detail above it and keep everything below byte-for-byte. Rename, reorder and drop never wipe
  evidence or a waiver.
- `review` reads the latest attempt. It is valid when its `<ul>` has at least one artifact `<li>`:
  `screenshot`/`file` ids resolve to an `ir.attachment` with `res_model=project.task`,
  `res_id=<subtask>`, a non-empty `mimetype` and `file_size > 0`; `curl`/`output`/`diff` have a
  non-empty `<pre><code>`. A `waiver` `<li>` with the reason, who and date is also valid. No artifact
  and no waiver → fail. It does not fetch `/web/image/<id>`; the URL is assumed reachable under the
  task ACL, and the verdict says the link was not fetched. A `1_done` step with no valid attempt is a
  fail, even when the test passed; the step goes to `02_changes_requested`.
- `archive` also gates: every child `1_done` step needs a valid attempt (artifact or waiver) before
  the card's done write. A legacy `1_done` child without evidence blocks the archive until an
  artifact or waiver is added.

## Policy, privacy and limits

- `~/.config/opencode/AGENTS.md`: add `ir.attachment` with read and create only, scoped to
  `project.task` attachments; never delete. The suite never deletes an attachment.
- Redaction: tokens, cookies, passwords and API keys are always stripped. Emails, names and IDs are
  masked unless the step is about them. Use a test account when the real one would expose a client.
- Caps: screenshot ≤1600px wide and ≤500 KB; inline command output ≤40 lines / 4 KB, longer output
  attached as a `.txt` with the `file` label; file ≤2 MB, otherwise the user attaches it manually and
  pair locates it by `res_model`/`res_id` plus name to write the `file` `<li>`.
- Failure: no browser tool, no attachment permission, oversized file or a failed upload → stop and
  report. The step stays open; the user supplies the artifact or waives it.
- Visibility: subtasks are `display_in_project=False`, and an attachment inherits read access on the
  linked `project.task`. A portal user may not see a hidden subtask or its evidence; the audience is
  the internal team. For portal-visible projects, the redaction rule is mandatory; the task ACL still
  governs the attachment.
- The `pair` Always block adds “subtask evidence” to the list of what the agent writes. “Never write
  the card description” still holds; evidence is written to the subtask description.

## Files

- `skills/ai-daridev-pair/SKILL.md` — the evidence step in the cycle, the close gate, the `[you]`
  path, the non-code path, the Always bookkeeping and the `/tmp/opencode/evidence/` carve-out to the
  Root rule.
- `skills/ai-daridev-review/SKILL.md` — evidence in the verdict; missing evidence fails.
- `skills/ai-daridev-archive/SKILL.md` — the evidence check in the done gate.
- `skills/ai-daridev-story/SKILL.md` — preserve the evidence block on update.
- `skills/ai-daridev-check-plan/SKILL.md` — preserve the evidence block on rename, reorder and drop.
- `docs/workflow.md` — the evidence contract in the pair and review sections, and the subtask HTML
  sample with `<h3>Evidence</h3>`.
- `README.md` — evidence in the “what the agent writes” list.
- `docs/setup.md` — `ir.attachment` permission, `playwright-cli`, optional ImageMagick `convert`,
  size and redaction notes.
- `~/.config/opencode/AGENTS.md` — the `ir.attachment` exception, manual and local.

No schema change, no new config keys, no evidence subtasks, no evidence files in the repo.

## Out of scope

- No custom Odoo field or new model.
- No evidence subtasks or one child per artifact.
- No evidence files committed to the repo.
- No HTTP fetch of `/web/image` in review; the record check is the review's proof.

## Acceptance

- A PageSpeed step shows an embedded screenshot in its subtask.
- An API step shows the curl and its response in a code block.
- An Excel step shows the process screenshots and the attached file.
- A `1_done` step without evidence fails review; a step with a recorded waiver passes.
- The archive refuses a card whose `1_done` child has no artifact and no waiver; a waiver unblocks
  it.
- A code-only step can close with a diff hunk as its artifact.
- A retry appends a second dated evidence entry without overwriting the first.
- Re-running `story` or `check-plan` keeps the evidence and the waiver.
- Review confirms the attachment records and reports the URL as not fetched.
- No secret or unmasked client record reaches Odoo.
- No `convert` on the machine, or a screenshot still over 500 KB after two resizes: pair asks for a
  smaller screenshot instead of uploading it.
- A file name or waiver reason containing `<`, `>`, `&` is escaped.
- A manually attached oversized file is picked up by `res_model`/`res_id` plus name and appears as a
  `file` entry.
- A failed description write leaves the attachment for reuse; the retry reuses it when the recorded
  name and byte size match.
- The `/tmp/opencode/evidence/<slug>/<sanitized-step>/` directory is removed after the step-7
  re-read.
- The no-Odoo path prints the evidence and where to paste it.
- No attachment is ever deleted.
