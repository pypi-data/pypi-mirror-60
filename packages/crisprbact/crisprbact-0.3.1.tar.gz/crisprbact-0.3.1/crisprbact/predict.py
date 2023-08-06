import numpy as np
import re
from importlib.resources import open_binary
from crisprbact.utils import rev_comp
from crisprbact.off_target import (
    compute_off_target_df,
    extract_records,
    extract_features,
)

with open_binary("crisprbact", "reg_coef.pkl") as handle:
    coef = np.load(handle, allow_pickle=True)

bases = ["A", "T", "G", "C"]


def encode(seq):
    """One-hot encoding of a sequence (only non-ambiguous bases (ATGC) accepted)"""

    return np.array([[int(b == p) for b in seq] for p in bases])


# Quartiles: q1 > 0.4 > q2 > -0.08 > q3 > -0.59 > q4
def predict(X):
    return [np.sum(x * coef) for x in X]


def find_targets(seq):
    repam = "[ATGC]GG"
    L = len(seq)
    seq_revcomp = rev_comp(seq)
    matching_target = re.finditer("(?=([ATGC]{6}" + repam + "[ATGC]{16}))", seq_revcomp)
    for target in matching_target:
        yield dict(
            [
                ("target", target.group(1)),
                ("guide", target.group(1)[:20]),
                ("start", L - target.start() - 20),
                ("stop", L - target.start()),
                ("pam", L - target.start() - 22),
                ("ori", "-"),
            ]
        )


def on_target_predict(seq, genome=None, seed_size=7):

    seq = seq.upper()  # make uppercase
    seq = re.sub(r"\s", "", seq)  # removes white space
    records = None
    genome_features = None
    if genome:
        records = extract_records(genome)
        genome_features = extract_features(records)

    alltargets = list(find_targets(seq))
    if alltargets:
        X = np.array(
            [
                encode(target["target"][:7] + target["target"][9:])
                for target in alltargets
            ]  # encode and remove GG of PAM
        )
        X = X.reshape(X.shape[0], -1)
        preds = predict(X)

        for i, target in enumerate(alltargets):
            target.update({"pred": preds[i]})
            target.update({"seed_size": seed_size})
            if genome:
                off_target_df = compute_off_target_df(
                    target["guide"], seed_size, records, genome_features
                )
                off_targets_list = []
                off_targets = off_target_df.loc[
                    0:, ["start", "end", "pampos", "strand", "features"]
                ]
                for index, off_t in enumerate(off_targets.values.tolist()):
                    off_target_dict = {
                        "off_target_start": off_t[0],
                        "off_target_end": off_t[1],
                        "pampos": off_t[2],
                        "strand": off_t[3],
                    }
                    if len(off_t[4]) > 0:
                        for feat in off_t[4]:
                            feature_dict = {
                                "feat_strand": feat.location.strand,
                                "feat_start": feat.location.start,
                                "feat_end": feat.location.end,
                                "feat_type": feat.type,
                            }
                            for k, feat in feat.qualifiers.items():
                                if k != "translation":
                                    feature_dict[k] = " :: ".join(feat)
                            off_targets_list.append(off_target_dict)
                    else:
                        off_targets_list.append({**feature_dict, **off_target_dict})
                target.update({"off_targets": off_targets_list})
            else:
                target.update({"off_targets": []})
        return alltargets
    else:
        return []
