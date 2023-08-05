import numpy as np
import re
from importlib.resources import open_binary

with open_binary("crisprbact", "reg_coef.pkl") as handle:
    coef = np.load(handle, allow_pickle=True)

bases = ["A", "T", "G", "C"]


def encode(seq):
    """One-hot encoding of a sequence (only non-ambiguous bases (ATGC) accepted)"""

    return np.array([[int(b == p) for b in seq] for p in bases])


# Quartiles: q1 > 0.4 > q2 > -0.08 > q3 > -0.59 > q4
def predict(X):
    return [np.sum(x * coef) for x in X]


def rev_comp(seq):
    comp = str.maketrans("ATGC", "TACG")
    return seq.translate(comp)[::-1]


def find_targets(seq):
    repam = "[ATGC]GG"
    L = len(seq)
    seq_revcomp = rev_comp(seq)
    return (
        dict(
            [
                ("target", m.group(1)),
                ("guide", m.group(1)[:20]),
                ("start", L - m.start() - 20),
                ("stop", L - m.start()),
                ("pam", L - m.start() - 22),
                ("ori", "-"),
            ]
        )
        for m in re.finditer("(?=([ATGC]{6}" + repam + "[ATGC]{16}))", seq_revcomp)
    )


def on_target_predict(seq):

    seq = seq.upper()  # make uppercase
    seq = re.sub(r"\s", "", seq)  # removes white space
    alltargets = list(find_targets(seq))
    if alltargets:
        X = np.array(
            [
                encode(tar["target"][:7] + tar["target"][9:]) for tar in alltargets
            ]  # encode and remove GG of PAM
        )
        X = X.reshape(X.shape[0], -1)
        preds = predict(X)
        for i, target in enumerate(alltargets):
            target.update({"pred": preds[i]})
        return alltargets
    else:
        return []
