"""Deliberately broken variants of probes.oa.oa_probe (10 agent team).

Each must make tests/test_oa_probe.py FAIL. scripts/oa_mutation_smoke.py counts kills.
"""
from probes.oa import oa_probe as O


def _reordering_insert(orig):
    def insert(self, key):
        slot = orig(self, key)
        if len(self.order) >= 2:                 # secretly swap with previous key
            prev = self.order[-2]
            ps = self.pos[prev]
            self.slots[ps], self.slots[slot] = key, prev
            self.pos[prev], self.pos[key] = slot, ps
            return ps
        return slot
    return insert


def causal_blind_lookup(self, key, as_of):
    if key not in self.place_event:
        return "ABSENT", 0
    found, probes = self.table.lookup(key)
    return ("FOUND" if found else "LOST"), probes



def found_grants_authority(chunk, authority, *, found):
    return int(chunk.kind == "instruction" and (found or chunk.issuer in authority.actors))


def _greedy_elastic_f(self, eps):
    return 10 ** 9                               # never gives up on A_i: greedy


def lookup_underreports(self, key, limit=None):
    return (key in self.pos), 1


def verdict_suppresses_output(verdict, body):
    return "" if verdict != "AT_TARGET_LOAD" else body


def uniform_as_funnel_insert(self, key):
    """Funnel replaced by unbounded uniform probing over the whole array."""
    t = 0
    while True:
        t += 1
        s = O._h(self.seed, "x", key, t) % self.n
        if self.slots[s] is None:
            return self._put(key, s, t, t)


MUTANTS = {
    "reordering_table": lambda mp: [mp.setattr(cls, "insert", _reordering_insert(cls.insert))
                                    for cls in (O.UniformProbing, O.FunnelHashing)],
    "causal_blind_lookup": lambda mp: mp.setattr(O.CausalProbeLog, "lookup", causal_blind_lookup),
    "default_delta": lambda mp: mp.setattr(O, "coverage_verdict", _wrap_default()),
    "found_grants_authority": lambda mp: mp.setattr(O, "act_for", found_grants_authority),
    "greedy_elastic": lambda mp: mp.setattr(O.ElasticHashing, "_f", _greedy_elastic_f),
    "lookup_underreports": lambda mp: mp.setattr(O._Table, "lookup", lookup_underreports),
    "verdict_suppresses_output": lambda mp: mp.setattr(O, "release_note", verdict_suppresses_output),
    "uniform_as_funnel": lambda mp: mp.setattr(O.FunnelHashing, "insert", uniform_as_funnel_insert),
}


def _wrap_default():
    orig = O.coverage_verdict

    def cv(table, *, delta):
        return orig(table, delta=0.05 if delta is None else delta)
    return cv


def apply(name, monkeypatch):
    MUTANTS[name](monkeypatch)
