#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from test043_garf_helpers import *
import itk
import numpy as np

# create the simulation
sim = gam.Simulation()

# main options
ui = sim.user_info
ui.g4_verbose = False
ui.g4_verbose_level = 1
ui.number_of_threads = 1
ui.visu = False
ui.random_seed = 'auto'

# activity
activity = 1e6 * Bq

# add a material database
sim.add_material_database(paths.gate_data / 'GateMaterials.db')

# init world
sim_set_world(sim)

# fake spect head
spect_length = 19 * cm
spect_translation = 15 * cm
SPECThead = sim.add_volume('Box', 'SPECThead')
SPECThead.size = [57.6 * cm, 44.6 * cm, spect_length]
SPECThead.translation = [0, 0, -spect_translation]
SPECThead.material = 'G4_AIR'
SPECThead.color = [1, 0, 1, 1]

# detector input plane
detPlane = sim_set_detector_plane(sim, SPECThead.name)

# physics
sim_phys(sim)

# sources
sim_source_test(sim, activity)

# arf actor
arf = sim.add_actor('ARFActor', 'arf')
arf.mother = detPlane.name
arf.output = paths.output / 'test043_projection_garf.mhd'
arf.batch_size = 2e5
arf.image_size = [128, 128]
arf.image_spacing = [4.41806 * mm, 4.41806 * mm]
arf.verbose_batch = True
arf.distance_to_crystal = 74.625 * mm
arf.pth_filename = paths.gate_data / 'pth' / 'arf_Tc99m.pth'
arf.pth_filename = 'bidon-v3.pth'
# arf.pth_filename = 'bidon-v4.pth'
arf.pth_filename = 'bidon-v5.pth'
arf.pth_filename = 'bidon-v6.pth'

# add stat actor
s = sim.add_actor('SimulationStatisticsActor', 'stats')
s.track_types_flag = True

# create G4 objects
sim.initialize()

# start simulation
sim.start()

# print results at the end
stat = sim.get_actor('stats')
print(stat)

# print info
print('')
arf = sim.get_actor('arf')
img = arf.output_image
# set the first channel to the same channel (spectrum) than the analog
img[0, :] = img[1, :] + img[2, :]
print(f'Number of batch: {arf.batch_nb}')
print(f'Number of detected particles: {arf.detected_particles}')
filename = str(arf.user_info.output).replace('.mhd', '_0.mhd')
itk.imwrite(img, str(filename))

# ----------------------------------------------------------------------------------------------------------------
# tests
print()
gam.warning('Tests stats file')
stats_ref = gam.read_stat_file(paths.gate_output / 'stats_analog.txt')
# dont compare steps of course
stats_ref.counts.step_count = stat.counts.step_count
is_ok = gam.assert_stats(stat, stats_ref, 0.01)

print()
gam.warning('Compare image to analog')
is_ok = gam.assert_images(filename,
                          paths.output_ref / 'test043_projection_analog.mhd',
                          stat, tolerance=65, ignore_value=0, axis='x') and is_ok

print()
gam.warning('profile compare : ')
print(f'garf_compare_image_profile {paths.gate_output / "projection_analog.mhd"} {filename} -w 3')
print(f'garf_compare_image_profile {paths.gate_output / "projection_analog.mhd"} {filename} -w 3 -s 75')

gam.delete_run_manager_if_needed(sim)
gam.test_ok(is_ok)
