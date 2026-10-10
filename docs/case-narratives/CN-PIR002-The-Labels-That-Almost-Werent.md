# CN-PIR002 — The Labels That Almost Weren't

*Companion case narrative to PIR-002. Written 2026-07-14, the night a routine
command quietly deleted the only thing in the project a machine could not make.*

---

## The twelve

There are twelve labels in `calibration/labeling.csv`. Each one is a single word —
`grounded` or `violation` — sitting at the end of a row that also holds a claim and
the source text it was checked against. Twelve words. Perhaps four hundred bytes.

Every threshold in Agent-Assure rests on them. `lex_tau = 0.71` is not a number
someone chose; it is what falls out of a leave-one-out sweep when those twelve words
are the ground truth. The held-out error rates — false alarm 0.20, false negative
0.143, the numbers that appear in the demo, in the README, in the pitch — are
statements *about those twelve words*. Remove them and CR-001 is not weakened; it
ceases to exist. There is nothing left to calibrate against.

The whole edifice of the project's honesty rests on them, and they are the one
artifact in the repository that no amount of compute can reconstruct. Everything
else — the feature rows, the verdicts, the scores, the reports — is derived. Run the
code again and it comes back, byte for byte. The labels are not derived. They came
out of a human head, one at a time, and the only way to get them back is to put a
human in front of the claims again.

Fifty-two more of them are waiting for Sai right now, in `labeling-v2.csv`. He has
not filled them in yet. When he does, it will cost him forty-five minutes of the
kind of attention nobody can delegate — reading a claim, reading the evidence,
deciding whether one supports the other. That is the α1 gate. That is the thing the
entire Phase 2 roadmap is queued behind.

## The command

I had changed the tier logic. The standing discipline in this repo — the one that
has now twice caught my own fixes leaking — says: after any change to
classify/tiers/score, regenerate the calibration corpus and diff it, because the
corpus is the fix's own adversary.

So I typed the command that regenerates the corpus.

```
uv run python -m calibration.build_corpus
```

It ran. It printed `12 claims written`. It exited zero.

And it wrote an empty string into the `human_label` column of all twelve rows.

Not because anything went wrong. Because that is what the builder does, and has
always done, and was written to do. It is a *template generator*: it emits the file
a human is supposed to fill in, and a file a human is supposed to fill in has an
empty label column. Line 460 of `build_corpus.py` writes `""`. It has been sitting
there since Phase 2a, correct and patient, waiting for someone to run it on a day
when the file was no longer empty.

Nobody ever had. Why would you? You build the corpus once, you label it, you
calibrate. The builder's job is done before the labels exist. The only reason I ran
it afterwards is that a *later* discipline — drift-checking after a tier change —
told me to, and that discipline was invented weeks after the builder, by someone
(me) who never thought about what the builder would do to a file that had since
acquired a human's judgment in it.

Two good practices, each correct alone. Their intersection was a delete.

## Ninety seconds

The next thing I typed was the calibration run, because that was the actual point of
the exercise — I wanted to see whether CR-001's numbers still held after my tier
changes.

```
ValueError: load_labels: 'calibration/labeling.csv' line 2 (claim_id='q01#0')
has human_label '', which is not one of ['grounded', 'violation']. Every row
must be labeled by hand before calibration — an unlabeled or mislabeled row is
never silently defaulted.
```

The loader refused. Fail loud, never fallback — the rule this codebase repeats like
a catechism, applied here to a case its author was thinking about (*a human forgot
to label a row*) and catching a case its author was not (*a machine unlabeled every
row*). `git checkout --` and the twelve came back.

Ninety seconds, no loss. On paper this is a non-incident. It is the most instructive
thing that happened all night.

## Count the things that had to go right

Three defenses stood between that command and permanent loss, and I want to be
precise about what each one actually is:

The labels were committed to git. That is not a defense, it is a *recovery* — and it
works only if someone notices in time to use it.

The loader failed loud. That is not prevention either. It is detection, and it is
detection *downstream of the destruction* — the bytes were already gone from the
working tree when it fired. It caught the damage, not the damaging.

And the third: the very next command I happened to type was the one that reads the
labels. Had I typed `git add -A && git commit` — the most ordinary thing in the world
at the end of a work chunk, and something I had done four times already that night —
the blanked file would have gone into the commit, on top of the labels, and the loss
would have surfaced days later, in a session that had no idea what had happened,
with the truth buried in a diff nobody had reason to read.

That third defense has a name. It is luck.

**The system had detection. The system had recovery. The system had no prevention.**
And two of the three only worked because of a coincidence in my command ordering.

## The blind spot has a shape

This project thinks about asymmetry constantly. It is the central idea. Error-B — a
fabrication certified as PASS — is *unrecoverable*; Error-A — a false alarm on a real
claim — is *recoverable*; therefore no change may ever trade the second for the
first. That invariant is pinned in CLAUDE.md, enforced in the operating-point
selector, and defended by a red-team suite. I have spent two sessions doing almost
nothing else.

All of that asymmetric reasoning was applied to **verdicts**. None of it had ever
been applied to **artifacts**.

Because artifacts have exactly the same asymmetry, and it is exactly as consequential:

*Derived* artifacts — feature rows, reports, scores, the CR itself — are cheap and
reproducible. Delete them and the machine makes them again, identical. *Authored*
artifacts — the human labels — are scarce and irreproducible. Delete them and the
only regeneration path runs through a person's evening.

The builder treated both classes as "outputs to regenerate", because nothing in the
design had ever forced anyone to notice they were different classes. And so the
project whose founding claim is *"the store is audit evidence; silent repair destroys
defensibility"* shipped a tool that silently destroyed the **other** audit evidence —
the one that certifies the gate that certifies everything else.

The irony is not that the discipline failed. The discipline was airtight, in the
place it was pointed. It was pointed at the store, and the labels were standing
somewhere else.

## What we built, and what we did not

The guard is straightforward. `assert_labels_not_clobbered` reads the target before
any writer touches it, and if a single `human_label` cell is non-empty it raises,
naming the file, the count, and the first labeled row. Both builders call it first.
Three tests, proven red — before the guard, both writers cheerfully clobbered a
labeled file. Run the builder now and it says, in effect: *I will not do that; you
have 52 labels in there.*

There is one more piece, and it matters more than it looks. The guard makes the
labeled corpus un-regenerable — which collides head-on with the very discipline that
started this whole episode, the post-change drift check. Left that way, the honest
engineer doing the right thing would hit the guard every single time, and the guard
would become the obstacle between them and a check they *know* they should run.

That is how safety rails get ripped out. Not by malice — by a hundred small
frictions, until someone types `rm` to make the tool work again.

So the drift check got its own door: `--features-only` regenerates the gate's
predictions and does not go near the labels. The safe path is now also the easy
path. If your guard has no door, someone will eventually make one, and they will not
put it back.

And what we did **not** build, stated plainly because a PIR that hides its
unfinished business is a lie of omission: the root cause is still there. The labeling
CSV still holds machine-generated scaffolding and human judgment **in the same file,
owned by a generator**. The guard makes that file immutable once labeled, which means
the corpus cannot be extended after ratification without a manual merge — a real
limitation we accepted knowingly, trading it against silent destruction. The true fix
is separation: let the generator own the scaffold, let the labels live in their own
append-only file joined by `claim_id`, so that *regenerating the corpus* and
*preserving the judgment* stop being the same act. That is OI-CAL-03, and it should
land before anyone touches the corpus after Sai ratifies.

## The rule, for whoever reads this next

Sort every artifact your tools write into two piles. **Derived**: the machine can
make it again, so let the machine make it again. **Authored**: a person made it, and
only a person can make it again.

Then look at every generator you own and ask the question nobody asked here: *what
does this do if the file it is about to write already has a human's work in it?*

If the answer is "overwrite it", you do not have a bug yet. You have an appointment.

---

*Twelve labels survived by ninety seconds and a coincidence. Fifty-two more are
waiting to be written, and now there is something standing in front of them.*
