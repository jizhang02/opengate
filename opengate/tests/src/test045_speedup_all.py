#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from opengate.helpers import *

paths = gate.get_default_test_paths(__file__, "")

p = Box()
p.phantom_type = "analytic"
p.source_type = "analytic"
p.use_pet = True
p.use_gaga = False
p.a = 1e2

# debug
skip = False
# the seed is only for the G4 part, the GAN use his own seed
# so the results are not reproducible (yet)
seed = 812365478


def run(param):
    print("run ", param)
    cmd_line = (
        f"{paths.current}/test045_speedup.py -o AUTO --seed {seed} -p {param.phantom_type} "
        f"-s {param.source_type} -r Ga68 -a {param.a}"
    )
    if param.use_pet:
        cmd_line += " --pet "
    if param.use_gaga:
        cmd_line += " --gaga "
    out = f"test045_speedup_p_{param.phantom_type}_s_{param.source_type}_pet_{param.use_pet}_gaga_{param.use_gaga}.txt"
    if not skip:
        print("cmd line", cmd_line)
        r = os.system(f"python {cmd_line}")

    print("Output ", out)
    return out


# output
output = []

# Test 1
p.phantom_type = "analytic"
p.source_type = "analytic"
p.use_gaga = False
p.a = 1e3
out = run(p)
output.append(out)

# Test 2
p.phantom_type = "analytic"
p.source_type = "vox"
p.use_gaga = False
p.a = 1e3
out = run(p)
output.append(out)

# Test 3
p.phantom_type = "vox"
p.source_type = "vox"
p.use_gaga = False
p.a = 1e3
out = run(p)
output.append(out)

# Test 4
p.phantom_type = "analytic"
p.source_type = "analytic"
p.use_gaga = True
p.a = 1e3
out = run(p)
output.append(out)

# Test 5
p.phantom_type = "analytic"
p.source_type = "vox"
p.use_gaga = True
p.a = 1e3
out = run(p)
output.append(out)

# Test 6
p.phantom_type = "vox"
p.source_type = "vox"
p.use_gaga = True
p.a = 1e3
out = run(p)
output.append(out)

print(output)

# tests stats file
is_ok = True
for o in output:
    stats = gate.read_stat_file(paths.output / o)
    stats_ref = gate.read_stat_file(paths.output_ref / o)
    ok = gate.assert_stats(stats, stats_ref, 0.045)
    gate.print_test(ok, f"Check {o}")
    is_ok = is_ok and ok
    print()

# tests pet files
keys = [
    "GlobalTime",
    "PostPosition_X",
    "PostPosition_Y",
    "PostPosition_Z",
    "TotalEnergyDeposit",
    "TrackVolumeCopyNo",
]
tols = [10.0] * len(keys)
tols[keys.index("GlobalTime")] = 0.04
tols[keys.index("PostPosition_X")] = 7
tols[keys.index("PostPosition_Y")] = 10
tols[keys.index("PostPosition_Z")] = 1.3
tols[keys.index("TotalEnergyDeposit")] = 0.03
tols[keys.index("TrackVolumeCopyNo")] = 4.1
scalings = [1.0] * len(keys)
scalings[keys.index("GlobalTime")] = 1e-9  # time in ns
for o in output:
    o = o.replace(".txt", ".root")
    o1 = paths.output / o
    o2 = paths.output_ref / o
    img = paths.output / o.replace(".root", ".png")
    ok = gate.compare_root3(
        o1,
        o2,
        "Singles",
        "Singles",
        keys,
        keys,
        tols,
        scalings,
        scalings,
        img,
        hits_tol=5,
    )
    gate.print_test(ok, f"Check {o}")
    is_ok = is_ok and ok
    print()

gate.test_ok(is_ok)
