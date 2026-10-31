"""Open-addressing probe over an append-only receipt log. PROPOSED / ONGOING.

Engineering kernel (probe); not validated. Makes no slide-21 seal claim.

ANALOGY, NOT A RESULT ABOUT AI SYSTEMS. Source: Farach-Colton, Krapivin,
Kuszmaul, "Optimal Bounds for Open Addressing Without Reordering"
(arXiv:2501.02305v2). The paper proves bounds about hash tables with random
probe sequences. It proves nothing about agents, receipts, claims or L2_C.
This module borrows its *structure* only:

- "no reordering"  -> a receipt, once placed, is never moved (append-only).
                      Checked by `no_reorder_audit`, not assumed.
- "probe sequence" -> a bounded lookup path over placed receipts.
- "load 1 - delta" -> a coverage target. delta is caller-supplied, has no
                      default; missing delta -> NO_VERDICT.
- Lamport/vector order (kakeya_checks.causal) decides what a lookup may SEE:
  a receipt placed causally after the asking event is NOT_YET, never FOUND.

Fences (L2_C): found != authority (act_for ignores lookup results and needs
an HMAC under Authority.keys); Act = S*H*U with H and U undefined in this repo,
so act_for is only the S-side authority check; Act=0 != Stop (verdicts never
suppress output); nothing here certifies an agent or closes L2_C.
h<1 boundary: the influence of personal data on any verdict here stays below 1;
keys are opaque synthetic ids and no personal data is read or stored. Probe counts are synthetic simulation numbers, not measurements of any
agent workflow.

Schemes (paper sections):
- UniformProbing: greedy random probing (Sec. 1 baseline; iid probes as in Sec. 5).
- ElasticHashing: non-greedy, Sec. 2 / Theorem 1, using phi from Lemma 1.
- FunnelHashing: greedy, Sec. 3 / Theorem 2 (worst-case expected O(log^2 1/delta),
  whp worst case O(log^2 1/delta + log log n), amortized O(log 1/delta)), with
  stated small-n deviations.
"""

from __future__ import annotations

import hashlib
import hmac
import math
from typing import Dict, Iterator, List, Optional, Tuple

from . import causal

STATUS = "PROPOSED / ONGOING; analogy to arXiv:2501.02305 structure only; no measurements"


class TableFailure(RuntimeError):
    pass


def _h(seed: int, *parts) -> int:
    d = hashlib.blake2b(repr((seed,) + parts).encode(), digest_size=8).digest()
    return int.from_bytes(d, "big")


def phi(i: int, j: int) -> int:
    """Lemma 1 injection: bits of j each prefixed by 1, then 0, then bits of i."""
    s = "".join("1" + b for b in bin(j)[2:]) + "0" + bin(i)[2:]
    return int(s, 2)


def phi_inv(t: int) -> Optional[Tuple[int, int]]:
    s = bin(t)[2:]
    jb, k = "", 0
    while k + 1 < len(s) and s[k] == "1":
        jb += s[k + 1]
        k += 2
    if k >= len(s) or s[k] != "0" or not jb or jb[0] != "1":
        return None
    ib = s[k + 1:]
    if not ib or ib[0] != "1":
        return None
    return int(ib, 2), int(jb, 2)


class _Table:
    greedy = True

    def __init__(self, n: int, seed: int) -> None:
        if n < 8:
            raise ValueError("n too small")
        self.n, self.seed = n, seed
        self.slots: List[Optional[str]] = [None] * n
        self.pos: Dict[str, int] = {}
        self.search_pc: Dict[str, int] = {}     # probe complexity (paper's definition)
        self.insert_probes: Dict[str, int] = {}
        self.order: List[str] = []

    @property
    def load(self) -> float:
        return len(self.pos) / self.n

    def probe_seq(self, key: str) -> Iterator[Tuple[int, int]]:
        raise NotImplementedError

    def _put(self, key: str, slot: int, pc: int, ins: int) -> int:
        if key in self.pos:
            raise ValueError("duplicate key %s" % key)
        if self.slots[slot] is not None:
            raise TableFailure("slot occupied")
        self.slots[slot] = key
        self.pos[key], self.search_pc[key], self.insert_probes[key] = slot, pc, ins
        self.order.append(key)
        return slot

    def lookup(self, key: str, limit: Optional[int] = None) -> Tuple[bool, int]:
        """Walk the key's probe sequence. Returns (found, probes counted by index t)."""
        last = 0
        for t, slot in self.probe_seq(key):
            if limit is not None and t > limit:
                return False, last
            last = t
            occ = self.slots[slot]
            if occ == key:
                return True, t
            if occ is None and self.greedy:
                return False, t        # greedy: first free slot ends a negative query
        return False, last

    def first_free_index(self, key: str, upto: int) -> Optional[int]:
        """Smallest t < upto whose slot is free now (greedy audit helper)."""
        for t, slot in self.probe_seq(key):
            if t >= upto:
                return None
            if self.slots[slot] is None:
                return t
        return None


class UniformProbing(_Table):
    """Greedy random probing: h_t(x) iid uniform over [n]."""

    def probe_seq(self, key):
        t = 0
        while True:
            t += 1
            yield t, _h(self.seed, "u", key, t) % self.n

    def insert(self, key: str) -> int:  # pylint: disable=inconsistent-return-statements  # loop returns or raises TableFailure
        for t, slot in self.probe_seq(key):
            if self.slots[slot] is None:
                return self._put(key, slot, t, t)
            if t > 64 * self.n:
                raise TableFailure("no free slot found")


class ElasticHashing(_Table):
    """Sec. 2. Non-greedy: may probe deep in A_i, then place early in A_{i+1}."""
    greedy = False

    def __init__(self, n: int, seed: int, *, delta: float, c: float) -> None:
        super().__init__(n, seed)
        inv = 1 / delta
        if abs(inv - round(inv)) > 1e-9 or round(inv) & (round(inv) - 1):
            raise ValueError("Theorem 1 needs 1/delta a power of two")
        self.delta, self.c = delta, c
        sizes, rem = [], n
        while rem > 0:
            s = (rem + 1) // 2
            sizes.append(s)
            rem -= s
        self.sizes = sizes                      # A_1..A_k, halving
        self.base = [sum(sizes[:k]) for k in range(len(sizes))]
        self.count = [0] * len(sizes)
        self.batch = 0
        self.case3 = 0
        self.overflow = 0

    def slot(self, i: int, j: int, key: str) -> int:   # i is 1-based
        return self.base[i - 1] + _h(self.seed, "e", key, i, j) % self.sizes[i - 1]

    def probe_seq(self, key):
        t = 0
        while True:
            t += 1
            ij = phi_inv(t)
            if ij and ij[0] <= len(self.sizes):
                yield t, self.slot(ij[0], ij[1], key)

    def _f(self, eps: float) -> int:
        a = math.log2(1 / eps) ** 2
        b = math.log2(1 / self.delta)
        return max(1, math.ceil(self.c * min(a, b)))

    def _first_free(self, key, i, jmax=None) -> Tuple[Optional[int], int]:
        j = 0
        while jmax is None or j < jmax:
            j += 1
            if self.slots[self.slot(i, j, key)] is None:
                return j, j
            if jmax is None and j > 64 * self.sizes[i - 1]:
                raise TableFailure("A_%d full" % i)
        return None, j

    def _target_full(self, i):
        s = self.sizes[i - 1]
        return s - math.floor(self.delta * s / 2)

    def _target_75(self, i):
        return math.ceil(0.75 * self.sizes[i - 1])

    def _put_ij(self, key, i, j, ins):
        self.count[i - 1] += 1
        return self._put(key, self.slot(i, j, key), phi(i, j), ins)

    def insert(self, key: str) -> int:
        k = len(self.sizes)
        if self.batch == 0:
            if self.count[0] < self._target_75(1):
                j, ins = self._first_free(key, 1)
                return self._put_ij(key, 1, j, ins)
            self.batch = 1
        while True:
            i = self.batch
            if i >= k:     # no A_{i+1}: finish in the last arrays greedily
                for a in range(i, 0, -1):
                    if self.count[a - 1] < self.sizes[a - 1]:
                        self.overflow += 1
                        j, ins = self._first_free(key, a)
                        return self._put_ij(key, a, j, ins)
                raise TableFailure("table full")
            full1 = self.count[i - 1] >= self._target_full(i)
            full2 = self.count[i] >= self._target_75(i + 1)
            if full1 and full2:
                self.batch += 1
                continue
            if full1:                                   # case 2
                j, ins = self._first_free(key, i + 1)
                return self._put_ij(key, i + 1, j, ins)
            if full2:                                   # case 3 (expensive)
                self.case3 += 1
                j, ins = self._first_free(key, i)
                return self._put_ij(key, i, j, ins)
            eps1 = 1 - self.count[i - 1] / self.sizes[i - 1]   # case 1
            f = self._f(eps1)
            j, ins = self._first_free(key, i, f)
            if j is not None:
                return self._put_ij(key, i, j, ins)
            j2, ins2 = self._first_free(key, i + 1)
            return self._put_ij(key, i + 1, j2, ins + ins2)


class FunnelHashing(_Table):
    """Sec. 3. Greedy. Deviation D1: a_i clamped to >= 1 bucket at small n.
    Deviation D2: C overflow raises TableFailure (paper: whp it does not)."""

    def __init__(self, n: int, seed: int, *, delta: float) -> None:
        super().__init__(n, seed)
        d = min(delta, 1 / 8)
        L = math.log2(1 / d)
        self.alpha = math.ceil(4 * L + 10)
        self.beta = math.ceil(2 * L)
        special = max(math.ceil(delta * n / 2), 4)
        avail = (n - special) // self.beta          # buckets for A'
        ratios = [(3 / 4) ** k for k in range(self.alpha)]
        a1 = avail / sum(ratios)
        while True:
            a = [max(1, round(a1 * r)) for r in ratios]
            if sum(a) <= avail:
                break
            a1 *= 0.99
        a[0] += avail - sum(a)
        self.a = a
        self.lvl_base = []
        off = 0
        for ai in a:
            self.lvl_base.append(off)
            off += ai * self.beta
        sp = n - off
        self.B0, self.Bn = off, sp // 2
        self.C0, self.Cn = off + sp // 2, sp - sp // 2
        ll = max(1, math.ceil(math.log2(max(2.0, math.log2(n)))))
        self.b_cap = ll
        self.c_bucket = max(1, 2 * ll)
        self.c_buckets = max(1, self.Cn // self.c_bucket)

    @property
    def lookup_bound(self) -> int:
        return self.alpha * self.beta + self.b_cap + 2 * self.c_bucket

    def probe_seq(self, key):
        t = 0
        for lvl in range(self.alpha):
            j = _h(self.seed, "f", key, lvl) % self.a[lvl]
            start = self.lvl_base[lvl] + j * self.beta
            for s in range(self.beta):
                t += 1
                yield t, start + s
        for r in range(self.b_cap):
            t += 1
            yield t, self.B0 + _h(self.seed, "B", key, r) % self.Bn
        ba = _h(self.seed, "Ca", key) % self.c_buckets
        bb = _h(self.seed, "Cb", key) % self.c_buckets
        for s in range(self.c_bucket):
            for b in (ba, bb):
                t += 1
                yield t, self.C0 + b * self.c_bucket + s

    def insert(self, key: str) -> int:
        for t, slot in self.probe_seq(key):
            if self.slots[slot] is None:
                return self._put(key, slot, t, t)
        raise TableFailure("funnel: both C buckets full")


# ---- audits and causal layer ------------------------------------------------

def no_reorder_audit(table: _Table, placements: Dict[str, int]) -> List[str]:
    """Keys whose current slot differs from the slot logged at placement."""
    bad = [k for k, s in placements.items()
           if table.slots[s] != k or table.pos.get(k) != s]
    return sorted(bad)


def greedy_violations(table: _Table, key: str, pc: int) -> bool:
    """Called right before placing: True if an earlier probe index is free."""
    return table.first_free_index(key, pc) is not None


class CausalProbeLog:
    """Append-only placement log over a table, ordered by causal.EventLog."""

    def __init__(self, table: _Table) -> None:
        self.table = table
        self.events = causal.EventLog()
        self.placed_at: Dict[str, int] = {}     # written once, never edited
        self.place_event: Dict[str, str] = {}

    def place(self, key: str, worker: str, deps=()) -> causal.Event:
        ev = self.events.record("place:" + key, worker, deps)
        slot = self.table.insert(key)
        self.placed_at[key] = slot
        self.place_event[key] = ev.event_id
        return ev

    def note(self, event_id: str, worker: str, deps=()) -> causal.Event:
        return self.events.record(event_id, worker, deps)

    def lookup(self, key: str, as_of: str) -> Tuple[str, int]:
        """FOUND only if the placement happened-before (or is) the asking event."""
        pe = self.place_event.get(key)
        if pe is None:
            return "ABSENT", 0
        if pe != as_of and not self.events.before(pe, as_of):
            return "NOT_YET", 0
        found, probes = self.table.lookup(key)
        return ("FOUND" if found else "LOST"), probes


def coverage_verdict(table: _Table, *, delta: Optional[float]) -> str:
    if delta is None:
        return "NO_VERDICT"
    return "AT_TARGET_LOAD" if table.load >= 1 - delta - 1e-12 else "BELOW_TARGET_LOAD"


def sign_chunk(key: bytes, chunk: causal.Chunk) -> str:
    return hmac.new(key, ("%s\x1f%s" % (chunk.chunk_id, chunk.sha256)).encode(),
                    hashlib.sha256).hexdigest()


def act_for(chunk: causal.Chunk, authority: causal.Authority, *, found: bool,
            signature: Optional[str] = None) -> int:
    """Authority check (S side of Act = S*H*U; H, U undefined here).

    Lookup success is stickiness, not authority: `found` is passed as covered
    and ignored by causal.act. The issuer must hold a key in Authority.keys and
    the chunk must carry a valid HMAC under it; data chunks never authorize.
    """
    key = authority.keys.get(chunk.issuer or "")
    if key is None or signature is None or not hmac.compare_digest(
            signature, sign_chunk(key, chunk)):
        return 0
    return causal.act(chunk, authority, covered=found)


def release_note(verdict: str, body: str) -> str:
    """Every verdict still emits the body (Act=0 != Stop)."""
    return "[%s] %s" % (verdict, body)
