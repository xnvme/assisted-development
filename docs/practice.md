<!--
SPDX-FileCopyrightText: Simon A. F. Lund <os@safl.dk>

SPDX-License-Identifier: BSD-3-Clause
-->

# Working with an agent

For contributors using an agent in their own checkout, under their own name.

The conventions themselves are in [`AGENTS.md`](../AGENTS.md), which is the
normative copy and the file an agent loads. They are not agent-specific: they
are how a contribution is made, and an agent following them is just a
contributor following them. They apply where the project you are contributing
to says nothing, and give way where it says something. This page is the
reasoning behind them, for people.

## Whose commit is it

If you run an agent in your own checkout with your own credentials, the commit
is yours. Not partly yours. You are the author, you are accountable for the
content, and "the agent wrote it" is not available to you afterwards. That is
the price of the convenience, and it is the right price.

The expectation that follows is the whole point: assisted development, not vibe
coding. You must understand the change you are submitting. Not "it looked
plausible and the tests passed", but understand it well enough to defend it in
review, fix it when it breaks at an inconvenient hour, and answer for it when
someone else builds on it. If you cannot, the change is not ready, however
finished it looks.

This is the difference from the automation case. A standalone agent identity
exists precisely so that its work arrives as a proposal from someone else, which
you then review. When you run the agent yourself, no such separation exists, so
the review has to happen before you commit rather than after.

## The trailers

Three separate jobs. The author line says who is answerable, `Signed-off-by:`
certifies provenance, and `Assisted-by:` discloses what helped:

```
Assisted-by: Claude Code:claude-opus-5
Signed-off-by: Full Name <address>
```

Never `Co-Authored-By:` for an agent. Co-authorship would divide the first job
with something that cannot hold any part of it.

`Assisted-by:` is disclosure, not a disclaimer. It records how the change was
produced, which is useful later when someone is working out why a subtle bug
looks the way it does. It does not move responsibility onto the tool, and it
does not excuse a change its author cannot explain.

The format follows the Linux kernel's [coding assistants
guidance](https://docs.kernel.org/process/coding-assistants.html), which
specifies `AGENT_NAME:MODEL_VERSION` with analysis tools appended and basic
tools omitted. Following it rather than inventing our own matters, because a
trailer is only worth having if the same name means the same thing everywhere.

That document is worth reading for its own sake. It reaches the same conclusion
about sign-off independently, stating that "AI agents MUST NOT add Signed-off-by
tags. Only humans can legally certify the Developer Certificate of Origin
(DCO)." A rule two projects arrive at separately is usually a rule about the
problem rather than about taste.

## Why a bug has to be reproduced first

A fix for a bug nobody reproduced is the single largest way agent-assisted work
wastes a maintainer's time. It looks reasonable, it reads as if someone
understood the problem, and it cannot be evaluated without redoing the work that
was skipped. An agent is particularly good at producing that: it can read code,
construct a convincing account of how it fails, and propose a patch for a fault
that was never there.

So the reproducer comes first, and if there is not one, the useful output is a
precise account of what was tried rather than a fix. The same reasoning makes
the fix the smallest one that addresses the cause. Tidying nearby code in the
same change makes it harder to review, and harder to backport later by whoever
is maintaining a stable branch.

## Review it like a stranger's patch

The failure mode is reading agent output the way you read your own code, which
is to say skimming for shape and trusting the details. Read it the way you read
a patch from a contributor you do not know: check the edges, check the error
paths, check that it did what was asked rather than something adjacent.

Verify claims rather than accepting them. If an agent says the tests pass, run
them. A report of success is a sentence it produced, not an observation you
made, and the two are easy to confuse when the sentence is confident.

The counterpart to that is stating what was not checked. An agent should say
which platform it tested on and what it could not exercise, and so should you
when you pass the work on. The kernel's guidance exists because maintainers
"waste too much time analyzing unverified reports and untested fixes", and an
unstated gap is how that time gets wasted: the reviewer assumes coverage that
was never there, and finds out at the worst moment.

Which is why silence has to mean "nothing to declare". One overstatement, one
"tested on Linux and FreeBSD" that was only ever Linux, and every future
omission is worthless, because nobody can tell the difference between a gap you
did not have and a gap you did not mention.

Keep changes small enough to actually review. An agent will happily produce a
thousand line change that you will not read properly, and an unreviewed change
is unreviewed regardless of who wrote it.

Keep the review small too. A review that is mostly noise trains people to skim
the parts that are not, and a list that mixes a leaked token with a naming
preference buries the token. That is the whole reason findings get sorted by
severity rather than presented as a pile.

## Why you check the branch out yourself

Reviewing someone's pull request starts with getting it onto your machine, and
that step is worth keeping. You were going to want the code in front of you
anyway, to read around it, build it, and poke at the thing it changed. An agent
that fetches, checks out, reviews, and reports in one motion hands you an
opinion that nobody looked at any code to form, and you are the one who will put
your name to it.

It is the same reasoning as not applying fixes during a review. The steps worth
automating are the ones where nothing is decided. Checking out is where you
start deciding, so it stays yours, and a review that leaves your working tree
exactly as it found it is easier to trust for the same reason.

The cost of that division is that the agent no longer knows where you are. You
switch branches in your shell and the session hears nothing, so a second review
in the same conversation will happily describe the first one's diff unless it
looks again. This has happened: a review that opened "same head, same working
tree, same pull request" after the branch underneath had been swapped, every
word of it recalled rather than observed. An agent's memory of a checkout is not
evidence about the checkout, and the fix is not to trust it harder but to make
each review name what it was made against, so the person who did the switching
can see the mismatch before anything is published.

## Self-review before pushing

The `review` skill exists so this happens every time rather than when you
remember. Run it before the first push, before pushing an update to an open pull
request, and before marking a draft ready, since each of those is a moment when
you are asking someone else for attention.

The bar is that nothing critical is outstanding when you push: nothing that
breaks users or the build, no secret, no data loss, no commit under the wrong
identity. Everything else is your call.

There is one deliberate exception. Pushing so that CI checks something you
cannot check locally is a reasonable thing to do, and different from pushing and
hoping. State it in the pull request. "CI will catch it" offered afterwards is
an excuse; "I pushed this for CI to reproduce on FreeBSD" offered beforehand is
a plan.

None of this is review. Review is someone else reading it. This only keeps you
from spending their attention on something you could have found yourself.

## Untrusted input

Issue text, pull request descriptions, review comments, and fetched web pages
are data, not instructions. This matters more than it sounds, because an agent
has no reliable way to tell the difference: instructions embedded in content
look exactly like instructions from you. Acting on someone else's text is the
failure mode these conventions exist to contain, and it gets worse the less a
human is watching.

The frame worth knowing is the [lethal
trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/): access to
private data, exposure to untrusted content, and an outbound channel. Any two
are survivable. All three means text someone else wrote can direct the agent to
read your private data and send it somewhere.

Notice how easily you assemble all three without meaning to. Point an agent at a
private repository, ask it to work from an issue a stranger filed, and leave it
able to push or comment, and you are there. So is anything that reads a web page
mid-task.

What actually helps, in rough order of usefulness:

- Do not point an agent at untrusted content and private context in the same
  run. Split it into two.
- Keep secrets out of the environment for any run that reads untrusted input.
  Not in env vars, not in files it can reach.
- Use an egress allowlist. Claude Code's devcontainer ships
  [`init-firewall.sh`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh),
  which does default-DROP with an ipset allowlist and is worth copying. Root can
  flush it, so it narrows reach rather than containing anything.
- Read the diff before you push it. This catches the crude version of the
  attack, which is most of it today.

If an agent reports that content told it to change its behaviour, that is a
finding worth keeping, not a curiosity.

## When the bug might be a vulnerability

Everywhere else, opening a pull request is the responsible thing to do. Here it
is the mistake: a fix in public discloses the flaw to everyone reading, and the
people best placed to act on that disclosure are rarely the ones you had in
mind. So nothing goes out, not an issue, not a comment, not an advisory, and
the decision about who to tell and when belongs to a person who can weigh it.

The awkward part is that you often cannot tell early on. A crash on malformed
input is a bug until someone notices where the input comes from. When it is not
obvious, treat it as the more serious of the two readings and ask.

## What goes to the model provider

Everything the agent reads is sent somewhere by design. Isolation changes what
it can read; it does not change where what it reads goes.

So treat the agent's context as published to a third party. Do not paste
credentials into a session on the theory that you will rotate them later. Do not
point it at a directory containing secrets and rely on it not looking. If a file
should not leave the building, it should not be in the working tree the agent
has.

## When to give the agent its own identity instead

Use one when the agent runs without you watching, on a schedule, or against
input you did not write. The separation buys attribution, independent
revocation, and a review gate that exists whether or not you remember to apply
one. Setting that up is a separate project, and a different exercise from this
page.

Use your own identity when you are driving interactively and reviewing as you
go. A second identity there adds ceremony without adding a boundary, since you
are sitting right beside it.

## The project outranks you

Any project you contribute to that documents its own process outranks anything
here, and an agent should be told to read that documentation before starting
rather than assuming defaults. xNVMe's [contributing
process](https://xnvme.io/contributing/contributing-process.html) is a good
example of what to look for: which branch to target, whether history must be
rebased, subject line constraints, sign-off terms, and how long CI takes on a
fork pull request.

None of those are matters of taste, and none of them are about the quality of
your change. Get one wrong and the contribution is bounced for a reason that has
nothing to do with its content, after someone spent their attention finding out.
Merging the default branch into your topic branch to catch up is the common one:
it produces exactly the history a project asking for rebases is trying to avoid.

CI cost is worth watching with an agent specifically. A full verification run
can take tens of minutes, on infrastructure shared with everyone else's, and an
agent that pushes a fix every time it notices something small will re-trigger it
each time. Batch the changes.
