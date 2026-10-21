# Final publication order — October 20 readiness

All technical deliverables were prepared and checked on **19 October 2026**. Publish the complete browsable package on **20 October**, your early target. The official public Level 2 window ends **31 October** with no stated closing time/timezone. Do not deliberately leave working code or corrected results unpublished until October 30 to manufacture the appearance of continued development.

## Before copying anything

Use the **existing** private `A3-PS003-TC520` repository in your logged-in account. You report that collaborators and the ownership transfer are already done. Do not create another repository, rename it, transfer it again, delete history or force-push.

Extract the final ZIP outside your clone. Copy the **contents of `A3-PS003-TC520/`**, not another nested project folder, into the existing clone. Preserve `.git`, personal settings and any already acquired raw dataset; do not copy `.env`, virtual environments, cache folders or raw NPZs into a commit. The final folder already contains safe ignore rules.

On a laptop, GitHub Desktop is an uncomplicated route: open the existing repository, fetch/pull, copy the supplied files, review **Changes**, commit the intended group and **Push origin**. If using GitHub’s website, use **Add file → Upload files** from the correct repository; preserve the folder structure. A single ZIP alone is not a browsable source-code submission.

## October 20 — upload all five groups in one session

These are meaningful reviewable groups, **not** an instruction to spread already completed work across fabricated dates. Use `main` if you are the sole person publishing and have just pulled current changes; otherwise coordinate with teammates or use a reviewed branch. Do not overwrite someone else’s concurrent changes.

| Order | Files/folders | Suggested commit message |
|---|---|---|
| 1 | `src/`, `configs/`, `tests/`, `scripts/`, `requirements.txt`, `.gitignore`, data instructions (no NPZ) | `feat: add reproducible NumPy traffic forecasting and FedAvg simulator` |
| 2 | `results/`, `checkpoints/`, `reports/tables/`, integrity/validation artifacts | `results: publish verified three-seed matrix and extended-round diagnostic` |
| 3 | `reports/`, `figures/`, technical `docs/` including assumptions, corrections and AI assistance | `docs: add final evaluation, reproducibility and mentor pseudocode` |
| 4 | **Complete `prototype/` including `dist/public/`**, launcher, source, lockfile and tests | `feat: add portable saved-model forecasting and evidence lab` |
| 5 | `presentation/`, `README.md`, `SUBMISSION_INDEX.md`, final checksum manifest | `docs: publish corrected AIORI presentation and complete submission index` |

Because documentation cross-links the full packet, complete all groups in the same publication session. If a group commit would create a broken visible README, publish one coherent commit instead: **`feat: publish complete PS-003 scientific prototype and final evaluation`**. Commit grouping is convenience, not an AIORI requirement.

**Do not push only the PPTX.** The prescribed PDF, source, results, report and usable prototype files are all important. Retain the introduction link **https://www.youtube.com/watch?v=jJh9rvyaiUA**. The old Level 1 presentation can remain as clearly marked superseded history, but the new README must make the corrected final PDF the current version.

## Immediately after the push

Open the actual remote repository and check README links, PDF rendering, PPTX download, representative result JSONs and all prototype files. Confirm that the browser app is not merely a screenshot: clone/extract and run **`python prototype/launch.py`**. Obtain/select the exact dataset for the real held-out forecast; the manual example is explicitly not dataset evidence.

Confirm that authorised AIORI/mentor/evaluator accounts can access the **private** repository. An unauthenticated 404 does not prove the repository is broken; your own successful login does not prove their access. Check the accepted collaborator/ownership settings from your account.

For Step 10, retain the **published live working demo** in the supplied README: **https://chaurahalab-gzh27d5b.manus.space**. This is the confirmed Manus publication, not a temporary Preview address. The supplied compiled app and launcher remain the direct file-review backup. GitHub does not automatically host `index.html`. Selecting the exact local dataset enables held-out playback; manual inference works without it. The hosted page includes platform analytics, but the scientific app has no dataset-upload endpoint; use the local launcher for strictly local operation.

## October 21–30 — real work only

| Date | Genuine action | Publish only if there is an actual change |
|---|---|---|
| Oct 21 | Reproduce the clean setup on the team computer; save real test/smoke output | Environment notes or a confirmed portability fix |
| Oct 22–24 | Peer review by both students and faculty guide; rehearse model/input/byte explanations | Actual documentation or accessibility fixes |
| Oct 23 · 7:30–8:30 PM IST; Oct 28 · 7:30–8:30 PM IST | Attend the confirmed Track 3 Smart Cities mentoring sessions; demonstrate prototype + pseudocode | Dated real attendance, feedback and any justified revision |
| Oct 29 | Check all links, current PDF, video playback and evaluator access again | Only real fixes |
| Oct 30 | Final publication/access buffer; preserve actual submission evidence | Final checklist status if verified |

The confirmed email details are: Session 1, Friday 23 October, https://meet.google.com/iye-duzu-gge; Session 2, Wednesday 28 October, https://meet.google.com/hmq-gcyu-xbf. Join the Track 3 mailing list at https://groups.google.com/a/iifon.net/g/smart-cities-aiori-3. No attendance, mentor acceptance or feedback should be ticked in advance. Record those only after the real sessions.

## Message to the organisers, if no invitation has arrived

> Hello, we are Chauraha Sync, A3-PS003-TC520, qualified for Level 2. We received the Track 3 Smart Cities mentoring schedule and will attend the sessions on 23 and 28 October. Please let us know if any additional private submission step or prototype/pseudocode demonstration instruction is required before the published October 31 window closes. Our repository is the existing A3-PS003-TC520 repository, configured according to the earlier instructions.

Use the existing official communication channel. The general public contact is **info@iifon.org**, but it is not specifically identified as a mentoring desk. This is a draft, not a message already sent.

No public final-submission form was verified in the current guideline. Follow any actual later organiser instruction; do not invent an extra form, meeting, upload receipt or date.
