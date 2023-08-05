'''sample ODS methods and utilities

-------
'''

from __future__ import print_function, division, unicode_literals

from .omas_utils import *
from .omas_core import ODS
from .omas_physics import constants
from .omas_plot import geo_type_lookup

__all__ = []
__ods__ = []


def add_to_ODS(f):
    '''
    anything wrapped here will be available as a ODS method with name 'sample_'+f.__name__
    '''
    __ods__.append(f.__name__)
    __all__.append(f.__name__)
    return f


def ods_sample():
    '''
    returns an ODS populated with all of the samples

    :return: sample ods
    '''
    ods = ODS()
    for ds in __all__:
        printd('Adding %s sample data to ods' % ds, topic='sample')
        ods = eval(ds)(ods)
    return ods


@add_to_ODS
def dataset_description(ods):
    ods['dataset_description.data_entry.machine'] = 'test'
    ods['dataset_description.data_entry.pulse'] = 100
    return ods


@add_to_ODS
def equilibrium(
        ods, time_index=0, include_profiles=True, include_phi=True, include_psi=True, include_wall=True, include_q=True
):
    """
    Add sample equilibrium data

    :param ods: ODS instance

    :param time_index: int
        Under which time index should fake equilibrium data be loaded?

    :param include_profiles: bool
        Include 1D profiles of pressure, q, p', FF'

    :param include_phi: bool
        Include 1D and 2D profiles of phi (toroidal flux, for calculating rho)

    :param include_psi: bool
        Include 1D and 2D profiles of psi (poloidal flux)

    :param include_wall: bool
        Include the first wall

    :param include_q: bool
        Include safety factor

    :return: ODS instance with equilibrium data added
        Since the original is modified, it is not necessary to catch the return, but it may be convenient to do so in
        some contexts. If you do not want the original to be modified, deepcopy it first.
    """
    from omas import load_omas_json
    eq = load_omas_json(imas_json_dir + '/../samples/sample_equilibrium_ods.json', consistency_check=False)

    phi = eq['equilibrium.time_slice.0.profiles_1d.phi']
    psi = eq['equilibrium.time_slice.0.profiles_1d.psi']
    q = eq['equilibrium.time_slice.0.profiles_1d.q']

    if not include_profiles:
        del eq['equilibrium.time_slice.0.profiles_1d']

    if not include_phi:
        if 'profiles_1d' in eq['equilibrium.time_slice.0']:
            del eq['equilibrium.time_slice.0.profiles_1d.phi']
        del eq['equilibrium.time_slice.0.profiles_2d.0.phi']
    else:
        eq['equilibrium.time_slice.0.profiles_1d.phi'] = phi

    if not include_psi:
        if 'profiles_1d' in eq['equilibrium.time_slice.0'] and 'psi' in eq['equilibrium.time_slice.0.profiles_1d']:
            del eq['equilibrium.time_slice.0.profiles_1d.psi']
        del eq['equilibrium.time_slice.0.profiles_2d.0.psi']
    else:
        eq['equilibrium.time_slice.0.profiles_1d.psi'] = psi

    if not include_q:
        if 'profiles_1d' in eq['equilibrium.time_slice.0'] and 'q' in eq['equilibrium.time_slice.0.profiles_1d']:
            del eq['equilibrium.time_slice.0.profiles_1d.q']
    else:
        eq['equilibrium.time_slice.0.profiles_1d.q'] = q

    if not include_wall:
        del eq['wall']

    ods['equilibrium.time_slice'][time_index].update(eq['equilibrium.time_slice.0'])
    ods['equilibrium.time_slice'][time_index]['time'] = float(time_index)
    ods['equilibrium.vacuum_toroidal_field.r0'] = eq['equilibrium.vacuum_toroidal_field.r0']
    ods.set_time_array(
        'equilibrium.vacuum_toroidal_field.b0', time_index, eq['equilibrium.vacuum_toroidal_field.b0'][0]
    )
    ods['equilibrium.time'] = ods['equilibrium.time_slice[:].time']

    return ods


@add_to_ODS
def core_profiles(ods, time_index=0, nx=11, add_junk_ion=False, include_pressure=True):
    """
    Add sample core_profiles data

    :param ods: ODS instance

    :param time_index: int

    :param nx: int
        Number of points in test profiles

    :param add_junk_ion: bool
        Flag for adding a junk ion for testing how well functions tolerate problems. This will be missing labels, etc.

    :param include_pressure: bool
        Include pressure profiles when temperature and density are added

    :return: ODS instance with profiles added.
        Since the original is modified, it is not necessary to catch the return, but it may be convenient to do so in
        some contexts. If you do not want the original to be modified, deepcopy it first.
    """
    from omas import load_omas_json
    pr = load_omas_json(imas_json_dir + '/../samples/sample_core_profiles_ods.json', consistency_check=False)

    ods['core_profiles.profiles_1d'][time_index].update(pr['core_profiles.profiles_1d.0'])
    ods['core_profiles.vacuum_toroidal_field.r0'] = pr['core_profiles.vacuum_toroidal_field.r0']
    ods.set_time_array('core_profiles.vacuum_toroidal_field.b0', time_index, pr['core_profiles.vacuum_toroidal_field.b0'][0])

    if add_junk_ion:
        ions = ods['core_profiles.profiles_1d'][time_index]['ion']
        ions[len(ions)] = copy.deepcopy(ions[len(ions) - 1])
        for item in ions[len(ions) - 1].flat():
            ions[len(ions) - 1][item] *= 0

    if not include_pressure:
        for item in ods.physics_core_profiles_pressures(update=False).flat().keys():
            if 'pres' in item and item in ods:
                del ods[item]

    ods['core_profiles.profiles_1d'][time_index]['time'] = float(time_index)

    return ods


@add_to_ODS
def pf_active(ods, nc_weird=0, nc_undefined=0):
    """
    Adds some FAKE active PF coil locations so that the overlay plot will work in tests.
    It's fine to test with dummy data as long as you know it's not real.

    :param ods: ODS instance

    :param nc_weird: int
        Number of coils with badly defined geometry to include for testing plot overlay robustness

    :param nc_undefined: int
        Number of coils with undefined geometry_type (But valid r, z outlines) to include for testing plot overlay
        robustness.

    :return: ODS instance with FAKE PF ACTIVE HARDWARE INFORMATION added.
    """

    nc_reg = 4
    nc = nc_reg + nc_weird + nc_undefined
    fc_dat = [
        #  R        Z       dR      dZ    tilt1  tilt2
        [.8608, .16830, .0508, .32106, 0.0, 0.0],
        [1.0041, 1.5169, .13920, .11940, 45.0, 0.0],
        [2.6124, 0.4376, 0.17320, 0.1946, 0.0, 92.40],
        [2.3834, -1.1171, 0.1880, 0.16920, 0.0, -108.06],
    ]

    rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
    outline_code = geo_type_lookup('outline', 'pf_active', ods.imas_version, reverse=True)

    for i in range(nc_reg):
        if (fc_dat[i][4] == 0) and (fc_dat[i][5] == 0):
            rect = ods['pf_active.coil'][i]['element.0.geometry.rectangle']
            rect['r'] = fc_dat[i][0]
            rect['z'] = fc_dat[i][1]
            rect['width'] = fc_dat[i][2]  # Or width in R
            rect['height'] = fc_dat[i][3]  # Or height in Z
            ods['pf_active.coil'][i]['element.0.geometry.geometry_type'] = rect_code
        else:
            outline = ods['pf_active.coil'][i]['element.0.geometry.outline']
            fdat = fc_dat[i]
            fdat[4] = -fc_dat[i][4] * numpy.pi / 180.
            fdat[5] = -(fc_dat[i][5] * numpy.pi / 180. if fc_dat[i][5] != 0 else numpy.pi / 2.)
            outline['r'] = [
                fdat[0] - fdat[2] / 2. - fdat[3] / 2. * numpy.tan((numpy.pi / 2. + fdat[5])),
                fdat[0] - fdat[2] / 2. + fdat[3] / 2. * numpy.tan((numpy.pi / 2. + fdat[5])),
                fdat[0] + fdat[2] / 2. + fdat[3] / 2. * numpy.tan((numpy.pi / 2. + fdat[5])),
                fdat[0] + fdat[2] / 2. - fdat[3] / 2. * numpy.tan((numpy.pi / 2. + fdat[5])),
            ]
            outline['z'] = [
                fdat[1] - fdat[3] / 2. - fdat[2] / 2. * numpy.tan(-fdat[4]),
                fdat[1] + fdat[3] / 2. - fdat[2] / 2. * numpy.tan(-fdat[4]),
                fdat[1] + fdat[3] / 2. + fdat[2] / 2. * numpy.tan(-fdat[4]),
                fdat[1] - fdat[3] / 2. + fdat[2] / 2. * numpy.tan(-fdat[4]),
            ]
            ods['pf_active.coil'][i]['element.0.geometry.geometry_type'] = outline_code

    for i in range(nc_reg, nc_reg + nc_weird):
        # This isn't a real geometry_type, so it should trigger the contingency
        ods['pf_active.coil'][i]['element.0.geometry.geometry_type'] = 99
    for i in range(nc_reg + nc_weird, nc):
        # This one doesn't have geometry_type defined, so the plot overlay will have trouble looking up which type it is
        outline = ods['pf_active.coil'][i]['element.0.geometry.outline']
        outline['r'] = [1.5, 1.6, 1.7, 1.5]
        outline['z'] = [0.1, 0.3, -0.1, 0]

    # generate some data that is not time homogeneous
    for i in range(nc_reg):
        n = (1 + i) * 10
        outline = ods['pf_active.coil'][i]['current.data'] = numpy.linspace(0, 1, n)
        outline = ods['pf_active.coil'][i]['current.time'] = numpy.linspace(0, 1, n)

    return ods


@add_to_ODS
def magnetics(ods):
    """
    Adds some FAKE magnetic probe locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real.

    :param ods: ODS instance

    :return: ODS instance with FAKE MAGNETICS HARDWARE INFORMATION added.
    """

    nbp = 12
    nfl = 7

    r0 = 1.5
    z0 = 0.0
    abp = 0.8
    afl = 1.0

    angle_bp = numpy.linspace(0, 2 * numpy.pi, nbp + 1)[:-1]
    rp = r0 + abp * numpy.cos(angle_bp)
    zp = z0 + abp * numpy.sin(angle_bp)

    angle_fl = numpy.linspace(0, 2 * numpy.pi, nfl + 1)[:-1]
    rf = r0 + afl * numpy.cos(angle_fl)
    zf = z0 + afl * numpy.sin(angle_fl)

    for i in range(nbp):
        ods['magnetics.b_field_pol_probe'][i]['identifier'] = 'FAKE bpol probe {}'.format(i)
        ods['magnetics.b_field_pol_probe'][i]['position.r'] = rp[i]
        ods['magnetics.b_field_pol_probe'][i]['position.z'] = zp[i]
        ods['magnetics.b_field_pol_probe'][i]['position.phi'] = 6.5

    for i in range(nfl):
        ods['magnetics.flux_loop'][i]['identifier'] = 'FAKE flux loop {}'.format(i)
        ods['magnetics.flux_loop'][i]['position.0.r'] = rf[i]
        ods['magnetics.flux_loop'][i]['position.0.z'] = zf[i]

    ods['magnetics.time'] = [0]

    return ods


@add_to_ODS
def thomson_scattering(ods, nc=10):
    """
    Adds some FAKE Thomson scattering channel locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real.

    :param ods: ODS instance

    :param nc: Number of channels to add.

    :return: ODS instance with FAKE THOMSON HARDWARE INFORMATION added.
    """

    r = numpy.linspace(1.935, 1.945, nc)
    z = numpy.linspace(-0.7, 0.2, nc)
    for i in range(nc):
        ch = ods['thomson_scattering.channel'][i]
        ch['identifier'] = 'F_TS_{:02d}'.format(i)  # F for fake
        ch['name'] = 'Fake Thomson channel for testing {}'.format(i)
        ch['position.phi'] = 6.5  # This angle in rad should look bad to someone who doesn't notice the Fake labels
        ch['position.r'] = r[i]
        ch['position.z'] = z[i]

    ods['thomson_scattering.time'] = [0]

    return ods


@add_to_ODS
def charge_exchange(ods, nc=10):
    """
    Adds some FAKE CER channel locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real. This function can overwrite existing data if you're not careful.
    The original is modified, so deepcopy first if you want different ODSs.

    :param ods: ODS instance

    :param nc: Number of channels to add.

    :return: ODS instance with FAKE CER HARDWARE INFORMATION added.
    """

    r = numpy.linspace(1.4, 2.2, nc)
    z = numpy.linspace(0.05, -0.07, nc)
    for i in range(nc):
        ch = ods['charge_exchange.channel'][i]
        ch['identifier'] = 'FAKE_CER_{:02d}'.format(i)  # F for fake
        ch['name'] = 'Fake CER channel for testing {}'.format(i)
        for x in ['r', 'z', 'phi']:
            ch['position'][x]['time'] = numpy.array([0])
        ch['position.phi.data'] = numpy.array([6.5])
        ch['position.r.data'] = numpy.array([r[i]])
        ch['position.z.data'] = numpy.array([z[i]])

    return ods


@add_to_ODS
def interferometer(ods):
    """
    Adds some FAKE interferometer locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real.

    :param ods: ODS instance

    :return: ODS instance with FAKE INTERFEROMETER HARDWARE INFORMATION added.
    """
    ods['interferometer.channel.0.identifier'] = 'FAKE horz. interf.'
    r0 = ods['interferometer.channel.0.line_of_sight']
    r0['first_point.phi'] = r0['second_point.phi'] = 225 * (-numpy.pi / 180)
    r0['first_point.r'], r0['second_point.r'] = 3.0, 0.8
    r0['first_point.z'] = r0['second_point.z'] = 0.0

    i = 0
    ods['interferometer.channel'][i + 1]['identifier'] = 'FAKE vert. interf.'
    los = ods['interferometer.channel'][i + 1]['line_of_sight']
    los['first_point.phi'] = los['second_point.phi'] = 240 * (-numpy.pi / 180)
    los['first_point.r'] = los['second_point.r'] = 1.48
    los['first_point.z'], los['second_point.z'] = -1.8, 1.8

    for j in range(len(ods['interferometer.channel'])):
        ch = ods['interferometer.channel'][j]
        ch['line_of_sight.third_point'] = copy.deepcopy(ch['line_of_sight.first_point'])

    ods['interferometer.time'] = [0]

    return ods


@add_to_ODS
def bolometer(ods, nc=10):
    """
    Adds some FAKE bolometer chord locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real.

    :param ods: ODS instance

    :param nc: 10  # Number of fake channels to make up for testing

    :return: ODS instance with FAKE BOLOMETER HARDWARE INFORMATION added.
    """

    angles = numpy.pi + numpy.linspace(-numpy.pi / 4.0, numpy.pi / 4.0, nc)

    # FAKE origin for the FAKE bolometer fan
    r0 = 2.5
    z0 = 0.05

    for i in range(nc):
        ch = ods['bolometer.channel'][i]['line_of_sight']
        ch['first_point.r'] = r0
        ch['first_point.z'] = z0 + 0.001 * i
        ch['second_point.r'] = ch['first_point.r'] + numpy.cos(angles[i])
        ch['second_point.z'] = ch['first_point.z'] + numpy.sin(angles[i])
        ods['bolometer.channel'][i]['identifier'] = 'fake bolo {}'.format(i)

    ods['bolometer.channel'][nc - 1]['identifier'] = 'bolo fan 2 fake'  # This tests separate colors per fan in overlay

    ods['bolometer.time'] = [0]

    return ods


@add_to_ODS
def gas_injection(ods):
    """
    Adds some FAKE gas injection locations so that the overlay plot will work in tests. It's fine to test
    with dummy data as long as you know it's not real. This function can overwrite existing data if you're not careful.
    The original is modified, so deepcopy first if you want different ODSs.

    :param ods: ODS instance

    :return: ODS instance with FAKE GAS INJECTION HARDWARE INFORMATION added.
    """

    ods['gas_injection.time'] = [0]

    ods['gas_injection.pipe.0.name'] = 'FAKE_GAS_A'
    ods['gas_injection.pipe.0.exit_position.r'] = 2.25
    ods['gas_injection.pipe.0.exit_position.z'] = 0.0
    ods['gas_injection.pipe.0.exit_position.phi'] = 6.5
    ods['gas_injection.pipe.0.valve.0.identifier'] = 'FAKE_GAS_VALVE_A'

    ods['gas_injection.pipe.1.name'] = 'FAKE_GAS_B'
    ods['gas_injection.pipe.1.exit_position.r'] = 1.65
    ods['gas_injection.pipe.1.exit_position.z'] = 1.1
    ods['gas_injection.pipe.1.exit_position.phi'] = 6.5
    ods['gas_injection.pipe.1.valve.0.identifier'] = 'FAKE_GAS_VALVE_B'
    ods['gas_injection.pipe.1.second_point.r'] = 1.63
    ods['gas_injection.pipe.1.second_point.z'] = 1.08
    ods['gas_injection.pipe.1.second_point.phi'] = 6.5

    ods['gas_injection.pipe.2.name'] = 'FAKE_GAS_C'
    ods['gas_injection.pipe.2.exit_position.r'] = 2.1
    ods['gas_injection.pipe.2.exit_position.z'] = -0.6
    ods['gas_injection.pipe.2.valve.0.identifier'] = 'FAKE_GAS_VALVE_C'
    # This one deliberately doesn't have a phi angle defined, for testing purposes.

    return ods


@add_to_ODS
def langmuir_probes(ods):
    """
    Adds some FAKE Langmuir probe locations so the overlay plot will work in tests.
    :param ods: ODS instance

    :return: ODS instance
        The data are also written to the original, so you don't have to catch the return
    """

    ods['langmuir_probes.time'] = numpy.array([0])

    ods['langmuir_probes.embedded.0.identifier'] = 0
    ods['langmuir_probes.embedded.0.name'] = 'p1'
    ods['langmuir_probes.embedded.0.position.r'] = 0.9
    ods['langmuir_probes.embedded.0.position.z'] = 0.1
    ods['langmuir_probes.embedded.0.position.phi'] = 0

    ods['langmuir_probes.embedded.1.identifier'] = -1
    ods['langmuir_probes.embedded.1.name'] = 'p23'
    ods['langmuir_probes.embedded.1.position.r'] = 0.9
    ods['langmuir_probes.embedded.1.position.z'] = -0.9
    ods['langmuir_probes.embedded.1.position.phi'] = numpy.NaN

    ods['langmuir_probes.embedded.2.identifier'] = -2
    ods['langmuir_probes.embedded.2.name'] = 'blah'
    ods['langmuir_probes.embedded.2.position.r'] = 1.5
    ods['langmuir_probes.embedded.2.position.z'] = -1.25
    ods['langmuir_probes.embedded.2.position.phi'] = numpy.NaN

    ods['langmuir_probes.embedded.3.identifier'] = -3
    ods['langmuir_probes.embedded.3.name'] = 'donkey!'
    ods['langmuir_probes.embedded.3.position.r'] = 1.525
    ods['langmuir_probes.embedded.3.position.z'] = -1.25
    ods['langmuir_probes.embedded.3.position.phi'] = numpy.NaN

    ods['langmuir_probes.embedded.4.identifier'] = -4
    ods['langmuir_probes.embedded.4.name'] = 'zzz'
    ods['langmuir_probes.embedded.4.position.r'] = 1.4
    ods['langmuir_probes.embedded.4.position.z'] = 1.4
    ods['langmuir_probes.embedded.4.position.phi'] = numpy.pi

    ods['langmuir_probes.embedded.5.identifier'] = -5
    ods['langmuir_probes.embedded.5.name'] = "it's just a test"
    ods['langmuir_probes.embedded.5.position.r'] = 2.45
    ods['langmuir_probes.embedded.5.position.z'] = 0.25
    ods['langmuir_probes.embedded.5.position.phi'] = numpy.NaN

    return ods


@add_to_ODS
def wall(ods):
    """
    Adds some FAKE wall data to support testing. The wall is approximately DIII-D shaped, but I didn't try very hard.

    :param ods: ODS instance

    :return: ODS instance
        Edits are done in-place, so you don't have to catch the return (but you can if you want to!)
    """
    ods['wall.description_2d[0].limiter.type.description'] = 'first wall'
    ods['wall.description_2d[0].limiter.type.index'] = 0
    ods['wall.description_2d[0].limiter.type.name'] = 'first_wall'
    ods['wall.description_2d[0].limiter.unit[0].outline.r'] = [
        1.0, 1.0, 1.3, 1.4, 1.6, 2.15, 2.35, 2.35, 2.15, 1.800, 1.350, 1.35, 1.10, 1.00, 1.0
    ]
    ods['wall.description_2d[0].limiter.unit[0].outline.z'] = [
        0.0, 1.4, 1.4, 1.3, 1.1, 1.00, 0.50, -0.5, -1.0, -1.25, -1.25, -1.4, -1.4, -1.3, 0.0
    ]

    return ods
