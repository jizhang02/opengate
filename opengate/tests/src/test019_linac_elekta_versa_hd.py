#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import opengate.contrib.linacs.elektaversa as versa
from opengate.tests import utility
from scipy.spatial.transform import Rotation

if __name__ == "__main__":
    # paths
    paths = utility.get_default_test_paths(__file__, output_folder="test019_linac")

    # create the simulation
    sim = gate.Simulation()

    # main options
    sim.g4_verbose = False
    # sim.visu = True
    sim.visu_type = "vrml"
    sim.check_volumes_overlap = False
    sim.number_of_threads = 1
    sim.output_dir = paths.output  # FIXME (not yet)
    # sim.random_seed = 123456789 # FIXME
    sim.check_volumes_overlap = True

    # units
    m = gate.g4_units.m
    mm = gate.g4_units.mm

    # world
    world = sim.world
    world.size = [1 * m, 1 * m, 1 * m]
    world.material = "G4_AIR"

    # add a linac
    linac = versa.add_linac(sim, "versa", None)
    linac.translation = [50 * mm, 19 * mm, 17 * mm]
    linac.rotation = Rotation.from_euler("ZY", [38, 29], degrees=True).as_matrix()

    # add linac e- source
    source = versa.add_electron_source(sim, linac.name, linac.rotation)
    source.n = 5e4 / sim.number_of_threads
    if sim.visu:
        source.n = 200

    # physics
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option3"
    sim.physics_manager.set_production_cut("world", "all", 1 * mm)
    versa.enable_brem_splitting(sim, linac.name, splitting_factor=10)

    # add stat actor
    s = sim.add_actor("SimulationStatisticsActor", "stats")
    s.track_types_flag = True

    # add phase space
    plane = versa.add_phase_space_plane(sim, linac.name)
    phsp = versa.add_phase_space(sim, plane.name)
    phsp.output = paths.output / "phsp_versa.root"

    # start simulation
    sim.run()

    # print results
    stats = sim.output.get_actor(s.name)
    print(stats)

    # compare root
    br = "versa_phsp_plane_phsp"
    print()
    root_ref = paths.output_ref / "phsp_versa_no_tr_no_rot.root"
    keys = ["KineticEnergy", "PrePositionLocal_X", "PrePositionLocal_Y"]
    tols = [0.03, 1.8, 1.8]
    is_ok = utility.compare_root3(
        root_ref,
        phsp.output,
        br,
        br,
        keys,
        keys,
        tols,
        None,
        None,
        paths.output / "phsp_versa1.png",
        hits_tol=7,
    )

    print()
    root_ref = paths.output_ref / "phsp_versa_tr_no_rot.root"
    keys = ["KineticEnergy", "PrePositionLocal_X", "PrePositionLocal_Y"]
    tols = [0.03, 1.8, 1.8]
    is_ok = (
        utility.compare_root3(
            root_ref,
            phsp.output,
            br,
            br,
            keys,
            keys,
            tols,
            None,
            None,
            paths.output / "phsp_versa2.png",
            hits_tol=7,
        )
        and is_ok
    )

    print()
    root_ref = paths.output_ref / "phsp_versa_tr_rot.root"
    keys = [
        "KineticEnergy",
        "PrePosition_X",
        "PrePosition_Y",
        "PrePositionLocal_X",
        "PrePositionLocal_Y",
    ]
    tols = [0.03, 1.8, 1.8, 1.8, 1.8]
    is_ok = (
        utility.compare_root3(
            root_ref,
            phsp.output,
            br,
            br,
            keys,
            keys,
            tols,
            None,
            None,
            paths.output / "phsp_versa3.png",
            hits_tol=7,
        )
        and is_ok
    )
    # end
    utility.test_ok(is_ok)
