import unittest
from os.path import join

import viscojapan as vj

class Test_PredDispToDatabaseWriter(vj.test_utils.MyTestCase):
    def setUp(self):
        self.this_script = __file__
        super().setUp()

    def test1(self):
        pred = vj.inv.DispPred(
            file_G0 = join(self.share_dir, 'G0_He50km_VisM6.3E18_Rake83.h5'),
            result_file = join(self.share_dir, 'nrough_05_naslip_11.h5'),
            fault_file = join(self.share_dir, 'fault_bott80km.h5'),
            files_Gs = [join(self.share_dir, 'G1_He50km_VisM1.0E19_Rake83.h5'),
                        join(self.share_dir, 'G2_He60km_VisM6.3E18_Rake83.h5'),
                        join(self.share_dir, 'G3_He50km_VisM6.3E18_Rake90.h5')
                        ],
            nlin_par_names = ['log10(visM)','log10(He)','rake'],
            file_incr_slip0 = join(self.share_dir, 'slip0.h5')
        )

        writer = vj.inv.PredDispToDatabaseWriter(
            pred_disp = pred,
            db_file = join(self.outs_dir, '~pred.db')
            )
        writer.create_database()
        writer.insert_all()




if __name__ == '__main__':
    unittest.main()

