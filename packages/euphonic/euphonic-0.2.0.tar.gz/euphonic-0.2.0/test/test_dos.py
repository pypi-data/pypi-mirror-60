import unittest
import numpy as np
import numpy.testing as npt
# Before Python 3.3 mock is an external module
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from euphonic import ureg
from euphonic.data.bands import BandsData


class TestCalculateDos(unittest.TestCase):

    def setUp(self):
        # Create trivial function object so attributes can be assigned to it
        iron = type('', (), {})()
        mock_data = Mock(
            spec=BandsData,
            _e_units = 'E_h',
            _freqs=np.array(
                [[0.61994279, 0.71965754, 3.36969496,
                  4.19005014, 4.6599548, 11.76947015],
                 [0.75129323, 0.71971687, 3.38582288,
                  3.97216995, 4.55217895, 9.65011675],
                 [0.6597925, 0.57831182, 3.93864281,
                  3.93873641, 4.29865403, 9.30585629],
                 [1.91623131, 0.68094255, 2.32844159,
                  4.60528713, 3.54545356, 6.92907803],
                 [1.31309482, 0.83883714, 3.63675863,
                  4.72910328, 2.62995079, 9.91107037],
                 [0.94849194, 0.70136796, 3.60521438,
                  4.76928334, 3.30697109, 9.84672389],
                 [4.09669468, 9.87219429, 2.03982814,
                  4.2007423, 1.66974108, 1.08526588],
                 [4.21879869, 10.03489224, 1.14830785,
                  3.98517346, 1.64518417, 1.969158],
                 [4.44163652, 9.09726117, 1.03032365,
                  3.73380313, 2.10271909, 1.6011567],
                 [4.38372743, 7.62127765, 0.80563191,
                  3.47965126, 3.32296295, 1.06940083]]),
            _freq_down=np.array(
                [[2.2075221, 2.27080053, 5.22052453,
                  6.19431463, 6.77898358, 12.6564407],
                 [2.38881141, 2.18598238, 5.24878655,
                  5.93691943, 6.66050576, 10.67070688],
                 [2.31515727, 2.03424572, 5.88946115,
                  5.88693158, 6.39890777, 10.28803347],
                 [3.44111831, 8.40982789, 4.00526716,
                  6.7185675, 5.55451977, 1.92028853],
                 [2.82460361, 2.36408714, 5.5877661,
                  6.85656976, 4.39400517, 10.95945204],
                 [2.4933306, 2.2438063, 5.50581874,
                  6.91045619, 5.17588562, 10.86601713],
                 [11.13142744, 6.42438252, 3.42254246,
                  6.29084184, 3.13545502, 2.57103189],
                 [11.23283365, 6.10962655, 2.61564386,
                  6.36839401, 3.21634358, 3.39038677],
                 [10.33929618, 5.76769511, 2.47484074,
                  6.5454329, 3.77890382, 3.08910234],
                 [8.88541321, 5.37048973, 2.08710084,
                  6.46498163, 5.18913947, 2.76060135]]),
            weights=np.array(
                [0.01388889, 0.01388889, 0.00347222, 0.02777778,
                 0.01388889, 0.01388889, 0.01388889, 0.01388889,
                 0.02777778, 0.01388889]),
            n_branches=6)
        iron.mock_data = mock_data
        iron.gwidth = 0.1
        iron.dos_bins = np.array(
            [0.57831182, 0.62831182, 0.67831182, 0.72831182,
             0.77831182, 0.82831182, 0.87831182, 0.92831182,
             0.97831182, 1.02831182, 1.07831182, 1.12831182,
             1.17831182, 1.22831182, 1.27831182, 1.32831182,
             1.37831182, 1.42831182, 1.47831182, 1.52831182,
             1.57831182, 1.62831182, 1.67831182, 1.72831182,
             1.77831182, 1.82831182, 1.87831182, 1.92831182,
             1.97831182, 2.02831182, 2.07831182, 2.12831182,
             2.17831182, 2.22831182, 2.27831182, 2.32831182,
             2.37831182, 2.42831182, 2.47831182, 2.52831182,
             2.57831182, 2.62831182, 2.67831182, 2.72831182,
             2.77831182, 2.82831182, 2.87831182, 2.92831182,
             2.97831182, 3.02831182, 3.07831182, 3.12831182,
             3.17831182, 3.22831182, 3.27831182, 3.32831182,
             3.37831182, 3.42831182, 3.47831182, 3.52831182,
             3.57831182, 3.62831182, 3.67831182, 3.72831182,
             3.77831182, 3.82831182, 3.87831182, 3.92831182,
             3.97831182, 4.02831182, 4.07831182, 4.12831182,
             4.17831182, 4.22831182, 4.27831182, 4.32831182,
             4.37831182, 4.42831182, 4.47831182, 4.52831182,
             4.57831182, 4.62831182, 4.67831182, 4.72831182,
             4.77831182, 4.82831182, 4.87831182, 4.92831182,
             4.97831182, 5.02831182, 5.07831182, 5.12831182,
             5.17831182, 5.22831182, 5.27831182, 5.32831182,
             5.37831182, 5.42831182, 5.47831182, 5.52831182,
             5.57831182, 5.62831182, 5.67831182, 5.72831182,
             5.77831182, 5.82831182, 5.87831182, 5.92831182,
             5.97831182, 6.02831182, 6.07831182, 6.12831182,
             6.17831182, 6.22831182, 6.27831182, 6.32831182,
             6.37831182, 6.42831182, 6.47831182, 6.52831182,
             6.57831182, 6.62831182, 6.67831182, 6.72831182,
             6.77831182, 6.82831182, 6.87831182, 6.92831182,
             6.97831182, 7.02831182, 7.07831182, 7.12831182,
             7.17831182, 7.22831182, 7.27831182, 7.32831182,
             7.37831182, 7.42831182, 7.47831182, 7.52831182,
             7.57831182, 7.62831182, 7.67831182, 7.72831182,
             7.77831182, 7.82831182, 7.87831182, 7.92831182,
             7.97831182, 8.02831182, 8.07831182, 8.12831182,
             8.17831182, 8.22831182, 8.27831182, 8.32831182,
             8.37831182, 8.42831182, 8.47831182, 8.52831182,
             8.57831182, 8.62831182, 8.67831182, 8.72831182,
             8.77831182, 8.82831182, 8.87831182, 8.92831182,
             8.97831182, 9.02831182, 9.07831182, 9.12831182,
             9.17831182, 9.22831182, 9.27831182, 9.32831182,
             9.37831182, 9.42831182, 9.47831182, 9.52831182,
             9.57831182, 9.62831182, 9.67831182, 9.72831182,
             9.77831182, 9.82831182, 9.87831182, 9.92831182,
             9.97831182, 10.02831182, 10.07831182, 10.12831182,
             10.17831182, 10.22831182, 10.27831182, 10.32831182,
             10.37831182, 10.42831182, 10.47831182, 10.52831182,
             10.57831182, 10.62831182, 10.67831182, 10.72831182,
             10.77831182, 10.82831182, 10.87831182, 10.92831182,
             10.97831182, 11.02831182, 11.07831182, 11.12831182,
             11.17831182, 11.22831182, 11.27831182, 11.32831182,
             11.37831182, 11.42831182, 11.47831182, 11.52831182,
             11.57831182, 11.62831182, 11.67831182, 11.72831182,
             11.77831182, 11.82831182, 11.87831182, 11.92831182,
             11.97831182, 12.02831182, 12.07831182, 12.12831182,
             12.17831182, 12.22831182, 12.27831182, 12.32831182,
             12.37831182, 12.42831182, 12.47831182, 12.52831182,
             12.57831182, 12.62831182, 12.67831182])
        iron.expected_dos_gauss = np.array(
            [2.20437428e-01, 4.48772892e-01, 7.52538648e-01, 5.32423726e-01,
             3.02050060e-01, 2.13306464e-01, 1.39663554e-01, 1.63610442e-01,
             2.69621331e-01, 4.72982611e-01, 3.91689064e-01, 2.20437459e-01,
             8.23129014e-02, 7.36543547e-02, 1.30734252e-01, 6.52407077e-02,
             8.15883166e-03, 7.68497930e-04, 1.68213446e-02, 1.46787090e-01,
             3.91432231e-01, 3.91432239e-01, 1.46791072e-01, 1.73310220e-02,
             1.70781781e-02, 1.38638237e-01, 3.26452354e-01, 2.69619336e-01,
             1.63096763e-01, 2.69619336e-01, 3.26452354e-01, 1.38638229e-01,
             1.70741962e-02, 1.68213446e-02, 1.30481396e-01, 2.60954828e-01,
             1.30477414e-01, 1.63116672e-02, 7.64516076e-04, 8.15882000e-03,
             6.52387129e-02, 1.30477410e-01, 6.52387051e-02, 8.15483814e-03,
             2.54838692e-04, 1.99092728e-06, 3.88852984e-09, 0.00000000e+00,
             3.79739243e-12, 7.77895839e-09, 3.98574499e-06, 5.11672200e-04,
             1.65665059e-02, 1.38887091e-01, 3.34350362e-01, 3.26452350e-01,
             2.20692302e-01, 1.55708432e-01, 2.77778164e-01, 3.99847888e-01,
             3.34860036e-01, 2.28590311e-01, 2.04382628e-01, 2.69371473e-01,
             1.31118497e-01, 2.87987680e-02, 1.06524545e-01, 2.61213606e-01,
             2.36496263e-01, 1.43474182e-01, 1.63479519e-01, 2.61276359e-01,
             4.01629772e-01, 2.12539443e-01, 6.57503538e-02, 9.86245646e-02,
             2.63258326e-01, 3.34923753e-01, 2.20435974e-01, 2.85678156e-01,
             3.92453576e-01, 2.85423321e-01, 2.12280638e-01, 2.69621327e-01,
             1.30736235e-01, 1.63116750e-02, 5.09681272e-04, 3.98185456e-06,
             7.77705969e-09, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 3.79739243e-12, 7.77705969e-09, 3.98185456e-06,
             5.09677384e-04, 1.63096763e-02, 1.30477410e-01, 2.60954821e-01,
             1.30477410e-01, 1.63096763e-02, 5.09677384e-04, 3.98185456e-06,
             7.77705969e-09, 0.00000000e+00, 1.89869621e-12, 3.88852984e-09,
             1.99092728e-06, 2.54838692e-04, 8.15483814e-03, 6.52387051e-02,
             1.30477410e-01, 6.52387051e-02, 8.15483814e-03, 2.54838692e-04,
             1.99092728e-06, 3.88852984e-09, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             3.79739243e-12, 7.77705969e-09, 3.98185456e-06, 5.09677384e-04,
             1.63096763e-02, 1.30477411e-01, 2.60955318e-01, 1.30541120e-01,
             1.83483843e-02, 1.68193419e-02, 3.26233109e-02, 1.63096723e-02,
             2.03871196e-03, 6.57005544e-05, 2.55336423e-04, 8.15483912e-03,
             6.52387129e-02, 1.30481396e-01, 6.57503734e-02, 2.47193531e-02,
             1.38887091e-01, 3.26197507e-01, 2.61209663e-01, 8.97032196e-02,
             7.39032207e-02, 1.30736231e-01, 6.52407038e-02, 8.15484203e-03,
             2.54838692e-04, 1.99092728e-06, 3.88852984e-09, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 1.89869621e-12, 3.88852984e-09, 1.99092728e-06,
             2.54838692e-04, 8.15483814e-03, 6.52387051e-02, 1.30477410e-01,
             6.52387051e-02, 8.15483814e-03, 2.54838692e-04, 1.99092728e-06,
             3.88852984e-09, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00])
        iron.expected_dos_down_gauss = np.array(
            [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             3.79739243e-12, 7.77705969e-09, 3.98185456e-06, 5.09677384e-04,
             1.63096773e-02, 1.30477912e-01, 2.61020521e-01, 1.32770965e-01,
             4.07781686e-02, 9.88813718e-02, 1.63610912e-01, 2.14130212e-01,
             4.01946324e-01, 4.16410894e-01, 2.53313623e-01, 2.45411647e-01,
             3.37157561e-01, 4.08064445e-01, 3.42758550e-01, 2.77523322e-01,
             2.04639455e-01, 8.20620445e-02, 8.18052188e-02, 1.95972949e-01,
             1.95718110e-01, 7.33935549e-02, 8.41366258e-03, 7.68501819e-04,
             1.65685007e-02, 1.38887091e-01, 3.34348364e-01, 3.26193533e-01,
             2.12029781e-01, 7.44168799e-02, 2.52330124e-02, 1.47043924e-01,
             3.91434226e-01, 3.91432235e-01, 1.46787087e-01, 1.68193614e-02,
             5.17641093e-04, 5.13667015e-04, 1.63096841e-02, 1.30477418e-01,
             2.60958802e-01, 1.30987088e-01, 3.26193526e-02, 1.30987088e-01,
             2.60958802e-01, 1.30477418e-01, 1.63096763e-02, 5.09681272e-04,
             5.97278184e-06, 2.54846469e-04, 8.15483814e-03, 6.52387051e-02,
             1.30477410e-01, 6.52387051e-02, 8.15483814e-03, 2.54838692e-04,
             1.99092728e-06, 3.88852984e-09, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 1.89869621e-12, 3.89232724e-09, 1.99870624e-06,
             2.58824435e-04, 8.66650645e-03, 8.18032240e-02, 2.69111650e-01,
             3.91687069e-01, 2.77264501e-01, 1.47043924e-01, 1.39402741e-01,
             7.41640360e-02, 8.99600570e-02, 2.69364509e-01, 3.91438204e-01,
             2.69619340e-01, 9.81128983e-02, 1.39144916e-01, 2.61343055e-01,
             1.34811664e-01, 5.70838513e-02, 1.30989032e-01, 1.63355564e-01,
             7.74729581e-02, 7.37758051e-02, 1.38890077e-01, 1.30736238e-01,
             1.47044422e-01, 1.39207626e-01, 2.14321337e-01, 2.85678148e-01,
             3.02240660e-01, 2.36747136e-01, 2.06425312e-01, 2.78094721e-01,
             2.12285118e-01, 2.77523326e-01, 3.35114875e-01, 2.12284612e-01,
             2.20435476e-01, 2.61466489e-01, 2.03874939e-01, 7.36483897e-02,
             8.41166776e-03, 2.56833508e-04, 1.99481581e-06, 3.88852984e-09,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 3.79739243e-12, 7.77705969e-09,
             3.98185456e-06, 5.09677384e-04, 1.63096763e-02, 1.30477410e-01,
             2.60954821e-01, 1.30477410e-01, 1.63096763e-02, 5.09677384e-04,
             3.98185646e-06, 1.16655895e-08, 1.99092728e-06, 2.54838692e-04,
             8.15483814e-03, 6.52387051e-02, 1.30477410e-01, 6.52387051e-02,
             8.15483814e-03, 2.54838692e-04, 1.99092728e-06, 3.88852984e-09,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             4.74673712e-13, 9.75929154e-10, 5.05508521e-07, 6.76914817e-05,
             2.54838545e-03, 3.26193408e-02, 1.63096739e-01, 2.77264485e-01,
             1.32516122e-01, 1.63753768e-02, 7.65013807e-04, 8.15882097e-03,
             6.52387168e-02, 1.30479401e-01, 6.54935477e-02, 1.63116672e-02,
             6.57483825e-02, 1.38634239e-01, 1.30477418e-01, 1.38634239e-01,
             6.57483864e-02, 1.63136581e-02, 6.57483864e-02, 1.38634239e-01,
             1.30477414e-01, 1.38632248e-01, 6.54935438e-02, 8.15682907e-03,
             2.54842580e-04, 1.99092728e-06, 3.88852984e-09, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
             0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.89869621e-12,
             3.88852984e-09, 1.99092728e-06, 2.54838692e-04, 8.15483814e-03,
             6.52387051e-02, 1.30477410e-01])
        iron.expected_dos_lorentz = np.array(
            [2.36213697e-01, 3.40960260e-01, 5.59791268e-01, 4.05306050e-01,
             3.00598745e-01, 2.43092104e-01, 1.84501806e-01, 2.12440899e-01,
             2.41422709e-01, 3.74553522e-01, 3.00602608e-01, 2.18331410e-01,
             1.26875982e-01, 1.06125833e-01, 1.33009500e-01, 8.27211557e-02,
             5.67620854e-02, 5.60551098e-02, 7.60557996e-02, 1.44770764e-01,
             2.86200343e-01, 2.88029390e-01, 1.51215080e-01, 9.03030819e-02,
             8.84900554e-02, 1.43118025e-01, 2.59738838e-01, 2.28740492e-01,
             1.74253600e-01, 2.27089806e-01, 2.56264802e-01, 1.37057751e-01,
             7.82387532e-02, 7.22717763e-02, 1.14916280e-01, 1.98181334e-01,
             1.07339937e-01, 5.39137068e-02, 3.84507277e-02, 3.90891380e-02,
             6.14510617e-02, 1.03358784e-01, 5.78728658e-02, 3.07348683e-02,
             2.17869020e-02, 1.84978042e-02, 1.75391620e-02, 1.79809140e-02,
             1.96814765e-02, 2.29887110e-02, 2.89082558e-02, 4.02850972e-02,
             6.52972607e-02, 1.34070480e-01, 2.63217893e-01, 2.55190061e-01,
             2.22274470e-01, 1.85256660e-01, 2.55123153e-01, 3.23141606e-01,
             2.80154419e-01, 2.33922425e-01, 1.95579381e-01, 2.43000590e-01,
             1.45495058e-01, 1.03245617e-01, 1.33509038e-01, 2.23492540e-01,
             2.11145578e-01, 1.62820603e-01, 1.93941715e-01, 2.17413233e-01,
             3.23354158e-01, 1.93497505e-01, 1.37824072e-01, 1.45823628e-01,
             2.32192550e-01, 2.86377875e-01, 2.16187833e-01, 2.60758613e-01,
             3.15208920e-01, 2.51521079e-01, 1.92696540e-01, 2.29726552e-01,
             1.21024085e-01, 5.79789945e-02, 3.46176173e-02, 2.37294585e-02,
             1.76658441e-02, 1.38712402e-02, 1.13365964e-02, 9.46142550e-03,
             8.08900071e-03, 7.03126965e-03, 6.19545426e-03, 5.52169446e-03,
             4.96976375e-03, 4.51171417e-03, 4.12758862e-03, 3.80281147e-03,
             3.52654240e-03, 3.29060629e-03, 3.08878053e-03, 2.91631187e-03,
             2.69887842e-03, 2.54258423e-03, 2.40860930e-03, 2.33097726e-03,
             2.23691766e-03, 2.12783765e-03, 2.07647651e-03, 2.04752802e-03,
             2.07890953e-03, 2.06717075e-03, 2.16253029e-03, 2.30037279e-03,
             2.49420576e-03, 2.71171131e-03, 3.05843646e-03, 3.60532593e-03,
             4.44493556e-03, 5.68551364e-03, 7.60565706e-03, 1.12217284e-02,
             1.85265449e-02, 3.62439128e-02, 8.93055286e-02, 1.77715984e-01,
             8.93806665e-02, 3.64040780e-02, 1.87980192e-02, 1.17207806e-02,
             8.40712866e-03, 6.72839778e-03, 6.11665105e-03, 6.39258212e-03,
             7.67847107e-03, 1.09303720e-02, 1.94891231e-02, 4.58401335e-02,
             8.98934531e-02, 4.55661961e-02, 1.89525340e-02, 1.00461964e-02,
             6.36008876e-03, 4.53045250e-03, 3.50418856e-03, 2.88031312e-03,
             2.48161009e-03, 2.22067560e-03, 2.05082161e-03, 1.94572894e-03,
             1.89018541e-03, 1.87557669e-03, 1.89761743e-03, 1.95525225e-03,
             2.05026174e-03, 2.18740247e-03, 2.37509553e-03, 2.62686080e-03,
             2.96397172e-03, 3.42034456e-03, 4.05186639e-03, 4.95524738e-03,
             6.30914282e-03, 8.47301283e-03, 1.22562202e-02, 1.97770682e-02,
             3.77849753e-02, 9.12980790e-02, 1.80428367e-01, 9.32495061e-02,
             4.28345215e-02, 3.23803443e-02, 3.69192859e-02, 2.33552857e-02,
             1.63350706e-02, 1.54633814e-02, 1.85894814e-02, 2.82176395e-02,
             5.69305330e-02, 1.05577010e-01, 7.05254413e-02, 6.56961296e-02,
             1.19566254e-01, 2.32519327e-01, 1.90028371e-01, 1.00499075e-01,
             8.21126732e-02, 1.09723491e-01, 5.78987561e-02, 2.73020731e-02,
             1.60177253e-02, 1.07927734e-02, 7.90434641e-03, 6.11284612e-03,
             4.91247225e-03, 4.06322774e-03, 3.43802517e-03, 2.96384639e-03,
             2.59605395e-03, 2.30602449e-03, 2.07472037e-03, 1.88913924e-03,
             1.74025907e-03, 1.62180973e-03, 1.52952958e-03, 1.46072816e-03,
             1.41406280e-03, 1.38949045e-03, 1.38839771e-03, 1.41395751e-03,
             1.47182970e-03, 1.57144956e-03, 1.72841012e-03, 1.96903223e-03,
             2.33964680e-03, 2.92692643e-03, 3.90692971e-03, 5.67896039e-03,
             9.22305166e-03, 1.80438414e-02, 4.45502384e-02, 8.87420594e-02,
             4.45070028e-02, 1.79662533e-02, 9.11048774e-03, 5.45685864e-03,
             3.64453449e-03, 2.62239101e-03, 1.99069950e-03, 1.53756987e-03,
             1.24786384e-03, 1.03781587e-03, 8.80373037e-04, 6.88366229e-04,
             5.60123022e-04, 4.87189378e-04, 4.28047121e-04, 3.44044435e-04,
             3.04894551e-04, 2.72059754e-04])
        iron.expected_dos_down_lorentz = np.array(
            [0.0013475, 0.00146787, 0.00159829, 0.00170474, 0.00182271,
             0.00195399, 0.00217147, 0.00241002, 0.00260242, 0.00282077,
             0.00307032, 0.0033578, 0.00369198, 0.00408453, 0.00462199,
             0.00518793, 0.00588205, 0.00675157, 0.00794075, 0.00943199,
             0.01150628, 0.01457372, 0.0195215, 0.02859401, 0.04875881,
             0.105446, 0.19968201, 0.12170387, 0.09154094, 0.12484921,
             0.17948006, 0.20193574, 0.3240029, 0.33821893, 0.24954929,
             0.26075907, 0.29592108, 0.33989225, 0.29051919, 0.25064571,
             0.20443418, 0.12634374, 0.11741981, 0.17151742, 0.16472999,
             0.09227176, 0.05935657, 0.0554398, 0.07256366, 0.13562152,
             0.25907784, 0.24308362, 0.19462211, 0.11651152, 0.09850056,
             0.15311752, 0.28742319, 0.28408118, 0.14141214, 0.07127905,
             0.04923873, 0.04553691, 0.05820503, 0.10952556, 0.19917575,
             0.11646775, 0.08006111, 0.11475898, 0.19549973, 0.10344664,
             0.04861393, 0.03045644, 0.02403997, 0.02340451, 0.02981211,
             0.05485597, 0.0980809, 0.05330216, 0.02648495, 0.01757166,
             0.01404505, 0.01261522, 0.0121577, 0.01241502, 0.01339631,
             0.01514719, 0.01807406, 0.02300105, 0.03208878, 0.05128866,
             0.10110371, 0.21041985, 0.2868535, 0.22804927, 0.1535098,
             0.15898331, 0.11597735, 0.13079622, 0.22629805, 0.29521889,
             0.22940054, 0.14053834, 0.14700392, 0.22122407, 0.13342144,
             0.09972378, 0.13109371, 0.14992302, 0.10012457, 0.09932044,
             0.14448793, 0.12925554, 0.16084467, 0.14957955, 0.20665545,
             0.24246127, 0.25827098, 0.23121046, 0.20098413, 0.26324916,
             0.20533169, 0.24776663, 0.28393675, 0.19780771, 0.20992422,
             0.21170163, 0.17377596, 0.08797637, 0.04513846, 0.0283027,
             0.02004941, 0.01529163, 0.01224536, 0.01015221, 0.00864108,
             0.00751084, 0.00664392, 0.0059676, 0.00543508, 0.00501547,
             0.00468831, 0.00440512, 0.0041598, 0.00402182, 0.004001,
             0.00408715, 0.0042393, 0.00451851, 0.00494137, 0.00560175,
             0.00674536, 0.00875912, 0.01233736, 0.01954766, 0.03725946,
             0.09040613, 0.17891059, 0.09065215, 0.03784843, 0.0205432,
             0.01382251, 0.01124858, 0.01097745, 0.01340217, 0.02138911,
             0.04731746, 0.09108457, 0.04655124, 0.01981425, 0.01074552,
             0.00699312, 0.0050785, 0.00394609, 0.00329972, 0.00285159,
             0.00255002, 0.00234778, 0.00225378, 0.00221641, 0.0022279,
             0.00228543, 0.00239015, 0.00254718, 0.00276628, 0.00306359,
             0.00346482, 0.00401131, 0.00477179, 0.00586637, 0.00752012,
             0.01019561, 0.01500473, 0.02484254, 0.04962022, 0.11436168,
             0.19264527, 0.09899253, 0.0460507, 0.03181838, 0.03397179,
             0.05824292, 0.10293166, 0.06234208, 0.04600056, 0.06731815,
             0.11718641, 0.0987186, 0.11756247, 0.06834638, 0.04825988,
             0.06737867, 0.11547569, 0.09513789, 0.11122093, 0.05712155,
             0.02622802, 0.01502387, 0.00997969, 0.00725769, 0.00560479,
             0.00451746, 0.0037611, 0.00321387, 0.00280723, 0.00250029,
             0.00226771, 0.00209352, 0.00196792, 0.00188558, 0.00184495,
             0.00184827, 0.00190246, 0.00202124, 0.00222951, 0.00257251,
             0.00313605, 0.00409552, 0.0058497, 0.00944888, 0.0182532,
             0.0447449, 0.08892355])

        self.iron = iron

    def test_dos_up_iron_gauss(self):
        iron = self.iron
        BandsData.calculate_dos(
            iron.mock_data, iron.dos_bins, iron.gwidth, lorentz=False)
        npt.assert_allclose(iron.mock_data.dos, iron.expected_dos_gauss)

    def test_dos_down_iron_gauss(self):
        iron = self.iron
        BandsData.calculate_dos(
            iron.mock_data, iron.dos_bins, iron.gwidth, lorentz=False)
        npt.assert_allclose(
            iron.mock_data.dos_down, iron.expected_dos_down_gauss)

    def test_dos_up_iron_gauss_weights(self):
        iron = self.iron
        factor = 2.0
        weights = np.repeat(factor*iron.mock_data.weights[:, np.newaxis],
                            iron.mock_data.n_branches, axis=1)
        BandsData.calculate_dos(iron.mock_data, iron.dos_bins, iron.gwidth,
                                lorentz=False, weights=weights)
        npt.assert_allclose(iron.mock_data.dos/factor, iron.expected_dos_gauss)

    def test_dos_down_iron_gauss_ir(self):
        iron = self.iron
        factor = 2.0
        weights = np.repeat(factor*iron.mock_data.weights[:, np.newaxis],
                            iron.mock_data.n_branches, axis=1)
        BandsData.calculate_dos(iron.mock_data, iron.dos_bins, iron.gwidth,
                                lorentz=False, weights=weights)
        npt.assert_allclose(iron.mock_data.dos_down/factor,
                            iron.expected_dos_down_gauss)

    def test_dos_iron_lorentz(self):
        iron = self.iron
        BandsData.calculate_dos(
            iron.mock_data, iron.dos_bins, iron.gwidth, lorentz=True)
        npt.assert_allclose(iron.mock_data.dos, iron.expected_dos_lorentz)

    def test_dos_down_iron_lorentz(self):
        iron = self.iron
        BandsData.calculate_dos(
            iron.mock_data, iron.dos_bins, iron.gwidth, lorentz=True)
        npt.assert_allclose(iron.mock_data.dos_down,
                            iron.expected_dos_down_lorentz, atol=1e-08)

    def test_dos_iron_lorentz_ir(self):
        iron = self.iron
        factor = 2.0
        weights = np.repeat(factor*iron.mock_data.weights[:, np.newaxis],
                            iron.mock_data.n_branches, axis=1)
        BandsData.calculate_dos(iron.mock_data, iron.dos_bins, iron.gwidth,
                                lorentz=True, weights=weights)
        npt.assert_allclose(
            iron.mock_data.dos/factor, iron.expected_dos_lorentz)

    def test_dos_down_iron_lorentz_ir(self):
        iron = self.iron
        factor = 2.0
        weights = np.repeat(factor*iron.mock_data.weights[:, np.newaxis],
                            iron.mock_data.n_branches, axis=1)
        BandsData.calculate_dos(iron.mock_data, iron.dos_bins, iron.gwidth,
                                lorentz=True, weights=weights)
        npt.assert_allclose(iron.mock_data.dos_down/factor,
                            iron.expected_dos_down_lorentz, atol=1e-08)
