"""Causal coverage and correction custody, ordered by Lamport time. PROPOSED.

Engineering kernel. Seal status (slide 21): SAVER reference demonstrated on a
synthetic suite; live five-grain retention open, not validated; ablation owed.

PROPOSED computational construction. Design lineage: Lamport, "Time, Clocks,
and the Ordering of Events in a Distributed System" (CACM 1978) for logical
clocks and happened-before; vector clocks (Fidge 1988, Mattern 1989) for
concurrent workers. That lineage gives ORDER only. It gives no authority, no
consensus and no distributed-systems guarantee for this setting.

- A chunk hash proves intake, not reading. A chunk counts as read only with a
  content-bound receipt: a quoted span named by a verifier-issued challenge,
  checked against the verifier's own copy of the text.
- Every threshold is supplied by the caller. None has a default; a missing
  threshold yields NO_VERDICT, never a pass.
- The release gate blocks PROMOTION of claims to final, never all output. A
  held PARTIAL answer naming uncovered chunks still goes out (Act=0 != Stop).
- Coverage never grants authority. Only the authority table does.
- Corrections cascade only with valid authority, a valid HMAC tag and an
  unused nonce, and are replayable from an append-only log.
- Stated limit: receipts and tags made in-process can be forged by in-process
  code holding the keys. This is a check on honest workflows, not a security
  boundary.
- Scope: "workflows we tested" only. No measurements; cost saving OPEN.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Set, Tuple

STATUS = ("PROPOSED construction; Lamport order is order, not authority; "
          "no measurements; cost saving OPEN; thresholds set by the caller")


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---- intake ----------------------------------------------------------------

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    source_version: str
    start: int          # inclusive char offset in the source
    end: int            # exclusive
    sha256: str
    kind: str = "content"        # "content" or "instruction"
    issuer: Optional[str] = None  # who wrote an instruction chunk


def intake(source_id: str, source_version: str, text: str,
           spans: Iterable[Tuple[int, int]], *, kinds: Optional[Mapping[int, str]] = None,
           issuers: Optional[Mapping[int, str]] = None) -> List[Chunk]:
    """Hash each span of text. Spans must be in range and non-overlapping."""
    out: List[Chunk] = []
    last = 0
    for i, (s, e) in enumerate(sorted(spans)):
        if not (0 <= s < e <= len(text)) or s < last:
            raise ValueError("span %r out of range or overlapping" % ((s, e),))
        last = e
        out.append(Chunk("%s@%s#%d" % (source_id, source_version, i), source_id,
                         source_version, s, e, sha256_text(text[s:e]),
                         (kinds or {}).get(i, "content"), (issuers or {}).get(i)))
    return out


# ---- content-bound receipts ------------------------------------------------

@dataclass(frozen=True)
class Challenge:
    chunk_id: str
    offset: int   # relative to chunk start
    length: int


@dataclass(frozen=True)
class Receipt:
    chunk_id: str
    reader: str
    sha256: str
    quoted: Optional[str]   # None means a hash-only receipt
    challenge: Optional[Challenge]


def issue_challenge(chunk: Chunk, nonce: int, length: int) -> Challenge:
    """Verifier side: pick a window derived from a verifier nonce."""
    size = chunk.end - chunk.start
    length = max(1, min(length, size))
    return Challenge(chunk.chunk_id, nonce % (size - length + 1), length)


def answer_challenge(chunk: Chunk, text: str, ch: Challenge, reader: str) -> Receipt:
    body = text[chunk.start:chunk.end]
    return Receipt(chunk.chunk_id, reader, chunk.sha256,
                   body[ch.offset:ch.offset + ch.length], ch)


def verify_receipt(chunk: Chunk, text: str, receipt: Optional[Receipt]) -> bool:
    """True only for a content-bound receipt. A hash alone is not 'read'."""
    if receipt is None or receipt.chunk_id != chunk.chunk_id:
        return False
    if receipt.quoted is None or receipt.challenge is None:
        return False
    body = text[chunk.start:chunk.end]
    if sha256_text(body) != chunk.sha256 or receipt.sha256 != chunk.sha256:
        return False
    ch = receipt.challenge
    return body[ch.offset:ch.offset + ch.length] == receipt.quoted


def coverage(chunks: List[Chunk], text: str,
             receipts: Mapping[str, Receipt]) -> Tuple[float, List[str]]:
    """Fraction of chunks with a verified receipt, and the uncovered ids."""
    if not chunks:
        return 0.0, []
    uncovered = [c.chunk_id for c in chunks
                 if not verify_receipt(c, text, receipts.get(c.chunk_id))]
    return 1.0 - len(uncovered) / len(chunks), uncovered


def coverage_certified(chunks: List[Chunk], text: str,
                       receipts: Mapping[str, Receipt],
                       min_coverage: Optional[float]) -> Optional[bool]:
    """None when the caller gave no threshold (no verdict)."""
    if min_coverage is None:
        return None
    frac, _ = coverage(chunks, text, receipts)
    return bool(chunks) and frac >= min_coverage


def two_ends_flag(support: Iterable[Chunk], source_len: int,
                  window_fraction: Optional[float]) -> Optional[bool]:
    """Flag (True) support that sits inside one short window of the source."""
    if window_fraction is None:
        return None
    sup = list(support)
    if not sup or source_len <= 0:
        return True
    span = max(c.end for c in sup) - min(c.start for c in sup)
    return span < window_fraction * source_len


# ---- Lamport and vector clocks ---------------------------------------------

class LamportClock:
    def __init__(self) -> None:
        self.time = 0

    def tick(self) -> int:
        self.time += 1
        return self.time

    def receive(self, other: int) -> int:
        self.time = max(self.time, other) + 1
        return self.time


VClock = Dict[str, int]


def vc_tick(vc: Mapping[str, int], worker: str) -> VClock:
    out = dict(vc)
    out[worker] = out.get(worker, 0) + 1
    return out


def vc_merge(a: Mapping[str, int], b: Mapping[str, int]) -> VClock:
    return {k: max(a.get(k, 0), b.get(k, 0)) for k in set(a) | set(b)}


def happened_before(a: Mapping[str, int], b: Mapping[str, int]) -> bool:
    keys = set(a) | set(b)
    return (all(a.get(k, 0) <= b.get(k, 0) for k in keys)
            and any(a.get(k, 0) < b.get(k, 0) for k in keys))


def concurrent(a: Mapping[str, int], b: Mapping[str, int]) -> bool:
    return not happened_before(a, b) and not happened_before(b, a) and dict(a) != dict(b)


@dataclass
class Event:
    event_id: str
    worker: str
    lamport: int
    vclock: VClock
    deps: FrozenSet[str]   # explicit happened-before dependencies only


class EventLog:
    """Workers record events; order comes from messages, not from ids."""

    def __init__(self) -> None:
        self.events: Dict[str, Event] = {}
        self._clocks: Dict[str, LamportClock] = {}
        self._vc: Dict[str, VClock] = {}

    def record(self, event_id: str, worker: str, deps: Iterable[str] = ()) -> Event:
        if event_id in self.events:
            raise ValueError("duplicate event id %s" % event_id)
        deps = frozenset(deps)
        clock = self._clocks.setdefault(worker, LamportClock())
        vc = self._vc.get(worker, {})
        for d in sorted(deps):
            dep = self.events[d]
            clock.receive(dep.lamport)
            vc = vc_merge(vc, dep.vclock)
        if not deps:
            clock.tick()
        vc = vc_tick(vc, worker)
        self._vc[worker] = vc
        ev = Event(event_id, worker, clock.time, vc, deps)
        self.events[event_id] = ev
        return ev

    def before(self, a: str, b: str) -> bool:
        return happened_before(self.events[a].vclock, self.events[b].vclock)


# ---- claims ----------------------------------------------------------------

class ClaimStatus(str, Enum):
    ANALOGY = "analogy"
    STRATEGY = "strategy"
    MEASURED = "measured"
    PROVED = "proved"


@dataclass
class Claim:
    claim_id: str
    text: str
    status: ClaimStatus
    support: Tuple[str, ...] = ()        # chunk ids
    depends_on: Tuple[str, ...] = ()     # claim ids
    scope: Optional[str] = None          # workflow the claim speaks for


class ClaimGraph:
    def __init__(self, claims: Iterable[Claim]) -> None:
        self.claims = {c.claim_id: c for c in claims}
        self.stale: Set[str] = set()

    def dependents_of(self, roots: Iterable[str]) -> Set[str]:
        return dependents_of(self, roots)


def dependents_of(graph: ClaimGraph, roots: Iterable[str]) -> Set[str]:
    """Reachability: every claim that depends, directly or not, on a root."""
    rev: Dict[str, Set[str]] = {}
    for c in graph.claims.values():
        for d in c.depends_on:
            rev.setdefault(d, set()).add(c.claim_id)
    seen: Set[str] = set()
    stack = list(roots)
    while stack:
        cur = stack.pop()
        for nxt in rev.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def status_violations(graph: ClaimGraph,
                      source_status: Mapping[str, ClaimStatus]) -> List[str]:
    """SEM: a claim may not assert a stronger status than its sources carry."""
    rank = {ClaimStatus.ANALOGY: 0, ClaimStatus.STRATEGY: 1,
            ClaimStatus.MEASURED: 2, ClaimStatus.PROVED: 2}
    bad = []
    for c in graph.claims.values():
        for cid in c.support:
            s = source_status.get(cid)
            if s is None or (s is not c.status and rank[s] <= rank[c.status]):
                bad.append(c.claim_id)
                break
    return sorted(bad)


def fidelity_failures(graph: ClaimGraph, covered: Set[str]) -> List[str]:
    """Claims resting, directly or not, on a claim with no read support."""
    unsupported = {c.claim_id for c in graph.claims.values()
                   if not c.support or not set(c.support) <= covered}
    return sorted(unsupported | dependents_of(graph, unsupported))


def scope_violations(graph: ClaimGraph, tested: Set[str]) -> List[str]:
    return sorted(c.claim_id for c in graph.claims.values()
                  if c.status is ClaimStatus.MEASURED and c.scope not in tested)


# ---- correction registry ---------------------------------------------------

@dataclass(frozen=True)
class Correction:
    correction_id: str
    target: str        # chunk id or claim id it releases or corrects
    issuer: str
    nonce: str
    tag: str           # HMAC over (correction_id, target, issuer, nonce)


def _payload(correction_id: str, target: str, issuer: str, nonce: str) -> bytes:
    return "\x1f".join((correction_id, target, issuer, nonce)).encode("utf-8")


def sign_correction(key: bytes, correction_id: str, target: str, issuer: str,
                    nonce: str) -> Correction:
    tag = hmac.new(key, _payload(correction_id, target, issuer, nonce),
                   hashlib.sha256).hexdigest()
    return Correction(correction_id, target, issuer, nonce, tag)


@dataclass(frozen=True)
class Authority:
    """Who may write which targets, and their keys. Coverage is not in here."""
    writers: Mapping[str, FrozenSet[str]]   # issuer -> targets they may correct
    keys: Mapping[str, bytes]
    actors: FrozenSet[str] = frozenset()    # issuers whose instructions may act


@dataclass
class Registry:
    authority: Authority
    log: List[Tuple[str, Correction]] = field(default_factory=list)
    accepted: Dict[str, Correction] = field(default_factory=dict)
    used_nonces: Set[str] = field(default_factory=set)

    def check(self, c: Correction) -> str:
        if c.target not in self.authority.writers.get(c.issuer, frozenset()):
            return "unauthorized"
        key = self.authority.keys.get(c.issuer)
        good = key is not None and hmac.compare_digest(
            c.tag, hmac.new(key, _payload(c.correction_id, c.target, c.issuer,
                                          c.nonce), hashlib.sha256).hexdigest())
        if not good:
            return "bad_tag"
        if c.nonce in self.used_nonces or c.correction_id in self.accepted:
            return "replayed"
        return "accepted"

    def submit(self, c: Correction) -> str:
        verdict = self.check(c)
        self.log.append((verdict, c))   # append-only, rejections kept too
        if verdict == "accepted":
            self.accepted[c.correction_id] = c
            self.used_nonces.add(c.nonce)
        return verdict

    def union(self, other: "Registry") -> List[str]:
        """Import another registry's log, re-checked under THIS authority."""
        return [self.submit(c) for _, c in other.log]


def replay(log: Iterable[Tuple[str, Correction]], authority: Authority) -> Registry:
    reg = Registry(authority)
    for _, c in log:
        reg.submit(c)
    return reg


def apply_corrections(graph: ClaimGraph, registry: Registry) -> Set[str]:
    """Mark stale every claim supported by, or depending on, a corrected target."""
    targets = {c.target for c in registry.accepted.values()}
    direct = {cl.claim_id for cl in graph.claims.values()
              if cl.claim_id in targets or targets & set(cl.support)}
    newly = direct | graph.dependents_of(direct)
    graph.stale |= newly
    return newly


# ---- snapshots and emitted copies ------------------------------------------

class StaleSnapshot(LookupError):
    pass


class SnapshotStore:
    def __init__(self) -> None:
        self._head: Optional[str] = None
        self._data: Dict[str, object] = {}

    def commit(self, state: object, version: int) -> str:
        sid = "snap-%d-%s" % (version, sha256_text(repr(state))[7:19])
        self._data = {sid: state}   # older snapshots stop being addressable
        self._head = sid
        return sid

    def read(self, sid: str) -> object:
        if sid != self._head:
            raise StaleSnapshot("snapshot %s superseded by %s" % (sid, self._head))
        return self._data[sid]


@dataclass
class EmittedCopy:
    claim_id: str
    lamport: int
    retracted: bool = False
    flagged_unretractable: bool = False


def flag_emitted(copies: Iterable[EmittedCopy], stale: Set[str],
                 retractable: bool) -> List[str]:
    """A copy already sent out cannot be pulled back: flag it instead."""
    out = []
    for e in copies:
        if e.claim_id in stale:
            if retractable:
                e.retracted = True
            else:
                e.flagged_unretractable = True
                out.append(e.claim_id)
    return out


# ---- action and release gate -----------------------------------------------

def act(chunk: Chunk, authority: Authority, *, covered: bool) -> int:
    """Act = 1 only for an instruction chunk from an authorized actor.

    `covered` is accepted and deliberately ignored: coverage is not authority.
    """
    del covered
    return int(chunk.kind == "instruction" and chunk.issuer in authority.actors)


class ReleaseState(str, Enum):
    FINAL = "FINAL"
    HELD_PARTIAL = "HELD_PARTIAL"
    AWAITING_HUMAN = "AWAITING_HUMAN"        # named terminal state
    CORRECTION_STORM = "CORRECTION_STORM"    # liveness terminal state
    NO_VERDICT = "NO_VERDICT"


@dataclass(frozen=True)
class Release:
    state: ReleaseState
    output: str                 # always emitted; Act=0 != Stop
    promoted: Tuple[str, ...]
    held: Tuple[str, ...]
    uncovered: Tuple[str, ...]
    reason: str
    label: str                  # "FULL" or "PARTIAL"


def release(graph: ClaimGraph, chunks: List[Chunk], text: str,
            receipts: Mapping[str, Receipt], *, min_coverage: Optional[float],
            declared_partial: bool = False, awaiting_human: bool = False) -> Release:
    frac, uncovered = coverage(chunks, text, receipts)
    covered = {c.chunk_id for c in chunks} - set(uncovered)
    bad = set(fidelity_failures(graph, covered)) | graph.stale
    ok = tuple(sorted(set(graph.claims) - bad))
    held = tuple(sorted(bad))
    label = "PARTIAL" if (uncovered or declared_partial) else "FULL"
    lines = ["[%s] %s" % ("final" if cid in ok else "held", graph.claims[cid].text)
             for cid in sorted(graph.claims)]
    if uncovered:
        lines.append("PARTIAL: uncovered chunks: " + ", ".join(uncovered))
    output = "\n".join(lines)
    if awaiting_human:
        return Release(ReleaseState.AWAITING_HUMAN, output, (), tuple(sorted(graph.claims)),
                       tuple(uncovered), "waiting on a named human decision", label)
    cert = coverage_certified(chunks, text, receipts, min_coverage)
    if cert is None:
        return Release(ReleaseState.NO_VERDICT, output, (), tuple(sorted(graph.claims)),
                       tuple(uncovered), "no min_coverage supplied", label)
    if cert and not held and label == "FULL":
        return Release(ReleaseState.FINAL, output, ok, (), (), "all claims supported", label)
    return Release(ReleaseState.HELD_PARTIAL, output, ok if cert else (),
                   held if cert else tuple(sorted(graph.claims)), tuple(uncovered),
                   "coverage %.3f; %d claims held" % (frac, len(held)), label)


def settle(stream: Iterable[Correction], registry: Registry, graph: ClaimGraph,
           *, max_rounds: Optional[int]) -> Tuple[ReleaseState, str]:
    """Liveness: a correction stream ends in a named terminal state."""
    if max_rounds is None:
        return ReleaseState.NO_VERDICT, "no max_rounds supplied"
    for n, c in enumerate(stream, 1):
        if n > max_rounds:
            return (ReleaseState.CORRECTION_STORM,
                    "more than %d corrections; holding with reason" % max_rounds)
        registry.submit(c)
        apply_corrections(graph, registry)
    return ReleaseState.HELD_PARTIAL if graph.stale else ReleaseState.FINAL, "settled"


# ---- metrics ---------------------------------------------------------------

def gate_metrics(episodes: Iterable[Tuple[bool, bool]]) -> Dict[str, object]:
    """episodes: (gate_blocked, should_block). Rates read 'n/a' with no base."""
    eps = list(episodes)
    should = [b for b, s in eps if s]
    shouldnt = [b for b, s in eps if not s]
    return {
        "episodes": len(eps),
        "missed_coverage": (sum(1 for b in should if not b) / len(should)
                            if should else "n/a"),
        "false_block": (sum(1 for b in shouldnt if b) / len(shouldnt)
                        if shouldnt else "n/a"),
    }
