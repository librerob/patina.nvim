"""Published CIEDE2000 test vectors and conversion/simulation sanity checks."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from color_math import delta_e, lab, linear_rgb, encode_rgb, simulate_linear, MATRICES

DATA = Path(__file__).resolve().parent/'fixtures/ciede2000.txt'

def check():
    rows = [list(map(float,line.split())) for line in DATA.read_text().splitlines() if line and not line.startswith('#')]
    assert len(rows) == 34
    for i,row in enumerate(rows,1):
        actual = delta_e(row[:3],row[3:6])
        assert abs(actual-row[6]) <= .000051, f'Sharma vector {i}: {actual} != {row[6]}'
        assert abs(actual-delta_e(row[3:6],row[:3])) < 1e-10, 'distance must be symmetric'
    assert max(abs(v) for v in lab('#000000')) < 1e-10
    assert abs(lab('#FFFFFF')[0]-100) < .00001
    for color in ('#000000','#FFFFFF','#101F20','#F6F4EB','#984733','#7BCBB3'):
        assert encode_rgb(linear_rgb(color)) == color
    # A linear red input must select the first column, not a gamma-encoded transform.
    assert simulate_linear((1.,0.,0.),'protan',100) == (.152286,.114503,0.)
    for kind in ('protan','deutan','tritan'):
        assert sorted(MATRICES[kind]) == list(range(0,101,10))
        for severity in range(0,101,10):
            white = simulate_linear((1.,1.,1.),kind,severity)
            assert all(abs(v-1) < .000002 for v in white)
    print('34 published CIEDE2000 vectors, symmetry, sRGB/D65 and simulation checks passed')

if __name__ == '__main__':
    check()
