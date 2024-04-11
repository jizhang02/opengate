from scipy.spatial.transform import Rotation
from box import Box
from opengate.utility import g4_units
import numpy as np


def create_material(simulation, name):
    gcm3 = g4_units.g_cm3
    simulation.volume_manager.material_database.add_material_nb_atoms(
        f"{name}_target_tungsten", ["W", "Re"], [9, 1], 19.4 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_target_copper", ["Cu"], [1], 8.93 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_colli", ["W", "Ni", "Fe"], [0.95, 0.0375, 0.0125], 18 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_flat_filter", ["Cr", "Fe", "Ni"], [0.17, 0.75, 0.08], 7.9 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_mylar", ["H", "C", "O"], [0.04196, 0.625016, 0.333024], 1.38 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_carbon", ["C"], [1], 2.27 * gcm3
    )
    simulation.volume_manager.material_database.add_material_weights(
        f"{name}_aluminium", ["Al"], [1], 2.7 * gcm3
    )


def add_linac(sim, name="linac"):
    # unit
    m = g4_units.m
    mm = g4_units.mm
    deg = g4_units.deg
    create_material(sim, name)

    # for debug : should be the same as create_material
    # sim.volume_manager.add_material_database('../contrib/elekta_synergy_materials.db')

    # colors
    red = [1, 0.7, 0.7, 0.8]
    blue = [0.5, 0.5, 1, 0.8]
    white = [1, 1, 1, 0.8]

    # check overlap
    sim.g4_check_overlap_flag = True

    # global box
    linac = sim.add_volume("Box", name)
    linac.material = "G4_AIR"
    linac.size = [0.25 * m, 0.25 * m, 0.6 * m]
    linac.color = white

    # target
    target = add_target(sim, linac.name)

    # primary collimator
    primary_collimator = sim.add_volume("Cons", f"{name}_primary_collimator")
    primary_collimator.mother = linac.name
    primary_collimator.material = f"{name}_colli"
    primary_collimator.rmin1 = 31.45 * mm
    primary_collimator.rmax1 = 82 * mm
    primary_collimator.rmin2 = 6.45 * mm
    primary_collimator.rmax2 = 82 * mm
    primary_collimator.dz = 101 * mm / 2.0
    primary_collimator.sphi = 0
    primary_collimator.dphi = 360 * deg
    primary_collimator.translation = [0, 0, -65.5 * mm]
    primary_collimator.color = blue

    # flattening_filter
    add_flattening_filter(sim, linac.name)

    # ionizing_chamber
    add_ionizing_chamber(sim, linac.name)

    # back_scatter_plate
    bsp = sim.add_volume("Box", f"{name}_back_scatter_plate")
    bsp.mother = linac.name
    bsp.material = f"{name}_aluminium"
    bsp.size = [116 * mm, 84 * mm, 3 * mm]
    bsp.translation = [0, 0, -183 * mm]
    bsp.color = red

    # mirror
    add_mirror(sim, linac.name)

    # kill actor above the target
    kill_around_target(sim, target)

    return linac


def add_target(sim, linac_name):
    # unit
    mm = g4_units.mm

    # colors
    red = [1, 0.2, 0.2, 0.8]
    green = [0, 1, 0, 0.2]

    # material
    target_material = f"{linac_name}_target_tungsten"
    copper = f"{linac_name}_target_copper"

    # target
    target_support = sim.add_volume("Tubs", f"{linac_name}_target_support")
    target_support.mother = linac_name
    target_support.material = "G4_AIR"
    target_support.rmin = 0
    target_support.rmax = 15 * mm
    target_support.dz = 11 * mm / 2.0
    target_support.translation = [0, 0, -5 * mm]
    target_support.color = [0, 1, 0, 1]

    target = sim.add_volume("Tubs", f"{linac_name}_target")
    target.mother = target_support.name
    target.material = target_material
    target.rmin = 0
    target.rmax = 2.7 * mm
    target.dz = 1 * mm / 2.0
    target.translation = [0, 0, 5 * mm]
    target.color = red

    target_support_top = sim.add_volume("Tubs", f"{linac_name}_target_support_top")
    target_support_top.mother = target_support.name
    target_support_top.material = copper
    target_support_top.rmin = 2.7 * mm
    target_support_top.rmax = 15 * mm
    target_support_top.dz = 1 * mm / 2.0
    target_support_top.translation = [0, 0, 5 * mm]
    target_support_top.color = green

    target_support_bottom = sim.add_volume(
        "Tubs", f"{linac_name}_target_support_bottom"
    )
    target_support_bottom.mother = target_support.name
    target_support_bottom.material = copper
    target_support_bottom.rmin = 0
    target_support_bottom.rmax = 15 * mm
    target_support_bottom.dz = 10 * mm / 2.0
    target_support_bottom.translation = [0, 0, -0.5 * mm]
    target_support_bottom.color = green

    return target_support


def kill_around_target(sim, target):
    mm = g4_units.mm

    # above the target
    target_above = sim.add_volume("Tubs", f"{target.name}_kill_volume1")
    target_above.mother = target.mother
    target_above.material = "G4_AIR"
    target_above.rmin = 0
    target_above.rmax = 15 * mm
    target_above.dz = 0.001 * mm
    # source is 0.6 mm
    target_above.translation = [0, 0, 0.7 * mm]
    target_above.color = [1, 0, 0, 1]

    # around the target
    target_around = sim.add_volume("Tubs", f"{target.name}_kill_volume2")
    target_around.mother = target.mother
    target_around.material = "G4_AIR"
    target_around.rmin = 18 * mm
    target_around.rmax = 25 * mm
    target_around.dz = 10 * mm
    target_around.color = [1, 0, 0, 1]

    # psycho killer
    killer = sim.add_actor("KillActor", f"{target.name}_kill")
    killer.mother = [target_above.name, target_around.name]


def add_flattening_filter(sim, linac_name):
    # unit
    mm = g4_units.mm
    deg = g4_units.deg

    # colors
    yellow = [0, 0.7, 0.7, 0.8]

    # bounding cylinder
    flattening_filter = sim.add_volume("Tubs", f"{linac_name}_flattening_filter")
    flattening_filter.mother = linac_name
    flattening_filter.material = "G4_AIR"
    flattening_filter.rmin = 0
    flattening_filter.rmax = 40 * mm
    flattening_filter.dz = 24.1 * mm / 2
    flattening_filter.translation = [0, 0, -146.05 * mm]
    flattening_filter.color = [0, 0, 0, 0]  # invisible

    # create all cones
    def add_cone(sim, p):
        c = sim.add_volume("Cons", f"{linac_name}_flattening_filter_cone_{p.name}")
        c.mother = f"{linac_name}_flattening_filter"
        c.material = f"{linac_name}_flat_filter"
        c.rmin1 = 0
        c.rmax1 = p.rmax1
        c.rmin2 = 0
        c.rmax2 = p.rmax2
        c.dz = p.dz
        c.sphi = 0
        c.dphi = 360 * deg
        c.translation = [0, 0, p.tr]
        c.color = yellow

    cones = [
        [0.001, 5.45, 3.40, 10.35],
        [5.45, 9, 2.7, 7.3],
        [9, 14.5, 4.9, 3.5],
        [14.5, 22.5, 5.5, -1.7],
        [22.5, 32.5, 5.6, -7.25],
        [38.5, 38.5, 2, -11.05],
    ]  ## FIXME check 32.5 ?
    i = 0
    for c in cones:
        cone = Box()
        cone.name = i
        cone.rmax2 = c[0] * mm
        cone.rmax1 = c[1] * mm
        cone.dz = c[2] * mm / 2  # /2 to keep same values than Gate (where dz was /2)
        cone.tr = c[3] * mm
        add_cone(sim, cone)
        i = i + 1


def add_ionizing_chamber(sim, linac_name):
    # unit
    mm = g4_units.mm

    # main cylinder
    ionizing_chamber = sim.add_volume("Tubs", f"{linac_name}_ionizing_chamber")
    ionizing_chamber.mother = linac_name
    ionizing_chamber.material = "G4_AIR"
    ionizing_chamber.rmin = 0
    ionizing_chamber.rmax = 45 * mm
    ionizing_chamber.dz = 9.28 * mm / 2
    ionizing_chamber.translation = [0, 0, -169 * mm]
    ionizing_chamber.color = [0, 0, 0, 0]

    # layers
    def add_layer(sim, p):
        l = sim.add_volume("Tubs", f"{linac_name}_ionizing_chamber_mylar_layer_{p.i}")
        l.mother = f"{linac_name}_ionizing_chamber"
        l.material = f"{linac_name}_mylar"
        l.rmin = 0
        l.rmax = 45 * mm
        l.dz = 0.012 * mm / 2
        l.translation = [0, 0, p.tr1]

        l = sim.add_volume("Tubs", f"{linac_name}_ionizing_chamber_carbon_layer_{p.i}")
        l.mother = f"{linac_name}_ionizing_chamber"
        l.material = f"{linac_name}_carbon"
        l.rmin = 0
        l.rmax = 45 * mm
        l.dz = 0.000150 * mm / 2
        l.translation = [0, 0, p.tr2]

    layers = [
        [-2.634, -2.627925],
        [-0.434, -0.427925],
        [0.566, 0.572075],
        [1.566, 1.572075],
        [2.566, 2.572075],
        [3.566, 3.572075],
    ]
    i = 1
    for l in layers:
        ll = Box()
        ll.i = i
        ll.tr1 = l[0] * mm
        ll.tr2 = l[1] * mm
        add_layer(sim, ll)
        i = i + 1


def add_mirror(sim, linac_name):
    # unit
    mm = g4_units.mm
    blue = [0, 0, 1, 0.8]

    # main box
    m = sim.add_volume("Box", f"{linac_name}_mirror")
    m.mother = linac_name
    m.material = "G4_AIR"
    m.size = [137 * mm, 137 * mm, 1.5 * mm]
    m.translation = [0, 0, -225 * mm]
    rot = Rotation.from_euler("x", 37.5, degrees=True)
    m.rotation = rot.as_matrix()

    # mylar
    l = sim.add_volume("Box", f"{linac_name}_mirror_mylar_layer")
    l.mother = m.name
    l.material = f"{linac_name}_mylar"
    l.size = [110 * mm, 110 * mm, 0.0012 * mm]
    l.translation = [0, 0, 0.15 * mm]
    l.color = blue

    # alu
    l = sim.add_volume("Box", f"{linac_name}_mirror_alu_layer")
    l.mother = m.name
    l.material = f"{linac_name}_aluminium"
    l.size = [110 * mm, 110 * mm, 0.0003 * mm]
    l.translation = [0, 0, -0.6 * mm]
    l.color = blue


def enable_brem_splitting(sim, linac_name, splitting_factor):
    # create a region
    linac = sim.volume_manager.get_volume(linac_name)
    region_linac = sim.physics_manager.add_region(name=f"{linac.name}_region")
    region_linac.associate_volume(linac)
    # set the brem splitting
    s = f"/process/em/setSecBiasing eBrem {region_linac.name} {splitting_factor} 50 MeV"
    sim.add_g4_command_after_init(s)


def add_electron_source(sim, linac_name, rotation_matrix):
    MeV = g4_units.MeV
    mm = g4_units.mm
    source = sim.add_source("GenericSource", f"{linac_name}_e-_source")
    source.particle = "e-"
    source.mother = f"{linac_name}_target"
    source.energy.type = "gauss"
    source.energy.mono = 6.7 * MeV
    source.energy.sigma_gauss = 0.077 * MeV
    source.position.type = "disc"
    source.position.radius = 2 * mm  # FIXME not really similar to GATE need sigma etc
    source.position.translation = [0, 0, 0.6 * mm]
    source.direction.type = "momentum"
    source.n = 10
    # consider linac rotation
    dir = np.dot(rotation_matrix, np.array([0, 0, -1]))
    source.direction.momentum = dir
    return source


def add_phase_space_plane(sim, linac_name):
    mm = g4_units.mm
    nm = g4_units.nm
    plane = sim.add_volume("Tubs", f"{linac_name}_phsp_plane")
    plane.mother = linac_name
    plane.material = "G4_AIR"
    plane.rmin = 0
    plane.rmax = 70 * mm
    plane.dz = 1 * nm  # half height
    plane.translation = [0, 0, -299.99 * mm]
    plane.color = [1, 0, 0, 1]  # red
    return plane


def add_phase_space(sim, plane_name):
    phsp = sim.add_actor("PhaseSpaceActor", f"{plane_name}_phsp")
    phsp.mother = plane_name
    phsp.attributes = [
        "KineticEnergy",
        "Weight",
        "PrePosition",
        "PrePositionLocal",
        "PreDirection",
        "PreDirectionLocal",
        "PDGCode",
    ]
    return phsp
