import unittest
import libpysal
import geopandas as gpd
import numpy as np
from segregation.spatial import Spatial_Isolation


class Spatial_Isolation_Tester(unittest.TestCase):
    def test_Spatial_Isolation(self):
        s_map = gpd.read_file(libpysal.examples.get_path("sacramentot2.shp"))
        df = s_map[['geometry', 'HISP_', 'TOT_POP']]
        index = Spatial_Isolation(df, 'HISP_', 'TOT_POP')
        np.testing.assert_almost_equal(index.statistic, 0.1562162475606278)


if __name__ == '__main__':
    unittest.main()
