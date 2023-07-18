import sys, os
testdir = os.path.dirname(__file__)
srcdir = '..\src'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import unittest
from pomodoro import App
import numpy as np
from datetime import datetime
from freezegun import freeze_time

class AppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_folder = os.path.join(os.getenv("APPDATA"), "Pomodoro")
        cls.date_format = '%Y.%m%d'
        cls.app = App()
        cls.test_files = []

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()
        for test_file in cls.test_files:
            if os.path.exists(test_file):
                os.remove(test_file)

    def _add_to_test_files(self, calendar_date):
        filename = str(calendar_date.year) + '_' + str(calendar_date.month) + '.csv'
        filepath = os.path.join(self.data_folder, filename)
        self.test_files.append(filepath)

    def test_load_data_no_data(self):
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('1999.1203', self.date_format))
        assert (self.app.monthly_start_times.size == 0)
        assert (self.app.monthly_end_times.size == 0)
        assert (self.app.weekly_start_times.size == 0)
        assert (self.app.weekly_end_times.size == 0)

    def test_load_data_2000_august(self):
        month = datetime.strptime('2000.0801', self.date_format)
        self.app.monthly_start_times = np.array([2000.0814, 1000, 1200, 2000.0815, 800, 900, 2000.0819, 300, 340, 2000.0822, 240, 980])
        self.app.monthly_end_times = np.array([2000.0814, 1100, 1240, 2000.0815, 880, 1000, 2000.0819, 330, 800, 2000.0822, 780, 1290])
        self.app._save_data(month)
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2000.0815', self.date_format))
        self._add_to_test_files(month)
        assert (self.app.monthly_start_times == np.array([2000.0814, 1000, 1200, 2000.0815, 800, 900, 2000.0819, 300, 340, 2000.0822, 240, 980])).all()
        assert (self.app.monthly_end_times == np.array([2000.0814, 1100, 1240, 2000.0815, 880, 1000, 2000.0819, 330, 800, 2000.0822, 780, 1290])).all()
        assert (self.app.weekly_start_times == np.array([2000.0814, 1000, 1200, 2000.0815, 800, 900, 2000.0819, 300, 340])).all()
        assert (self.app.weekly_end_times == np.array([2000.0814, 1100, 1240, 2000.0815, 880, 1000, 2000.0819, 330, 800])).all()

    def test_load_data_2010_jun_jul(self):
        month = datetime.strptime('2010.0601', self.date_format)
        self.app.monthly_start_times = np.array([2010.0628, 110, 240, 2010.0629, 450, 2010.0630, 780, 920])
        self.app.monthly_end_times = np.array([2010.0628, 200, 400, 2010.0629, 800, 2010.0630, 900, 1020])
        self.app._save_data(month)
        self._add_to_test_files(month)
        month = datetime.strptime('2010.0701', self.date_format)
        self.app.monthly_start_times = np.array([2010.0701, 450, 990, 2010.0703, 240, 880])
        self.app.monthly_end_times = np.array([2010.0701, 500, 1120, 2010.0703, 300, 980])
        self.app._save_data(month)
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2010.0702', self.date_format))
        self._add_to_test_files(month)
        assert (self.app.monthly_start_times == np.array([2010.0701, 450, 990, 2010.0703, 240, 880])).all()
        assert (self.app.monthly_end_times == np.array([2010.0701, 500, 1120, 2010.0703, 300, 980])).all()
        assert (self.app.weekly_start_times == np.array([2010.0628, 110, 240, 2010.0629, 450, 2010.0630, 780, 920, 2010.0701, 450, 990, 2010.0703, 240, 880])).all()
        assert (self.app.weekly_end_times == np.array([2010.0628, 200, 400, 2010.0629, 800, 2010.0630, 900, 1020, 2010.0701, 500, 1120, 2010.0703, 300, 980])).all()

    def test_load_data_2021_dec_2022_jan(self):
        month = datetime.strptime('2021.1201', self.date_format) 
        self.app.monthly_start_times = np.array([2021.1230, 450, 890, 930, 2021.1231, 1120]) 
        self.app.monthly_end_times = np.array([2021.1230, 770, 900, 1000, 2021.1231, 1330])
        self.app._save_data(month) 
        self._add_to_test_files(month)
        month = datetime.strptime('2022.0101', self.date_format)
        self.app.monthly_start_times = np.array([2022.0101, 240, 550, 2022.0103, 880, 990])
        self.app.monthly_end_times = np.array([2022.0101, 400, 800, 2022.0103, 920, 1234])
        self.app._save_data(month)
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2022.0102', self.date_format))
        self._add_to_test_files(month)
        assert (self.app.monthly_start_times == np.array([2022.0101, 240, 550, 2022.0103, 880, 990])).all()
        assert (self.app.monthly_end_times == np.array([2022.0101, 400, 800, 2022.0103, 920, 1234])).all()
        assert (self.app.weekly_start_times == np.array([2021.1230, 450, 890, 930, 2021.1231, 1120, 2022.0101, 240, 550])).all()
        assert (self.app.weekly_end_times == np.array([2021.1230, 770, 900, 1000, 2021.1231, 1330, 2022.0101, 400, 800])).all()

    def test_load_data_new_month_2021_feb(self):
        month = datetime.strptime('2022.0101', self.date_format)
        self.app.monthly_start_times = np.array([2022.0130, 450, 880, 2022.0131, 890, 1240])
        self.app.monthly_end_times = np.array([2022.0130, 770, 1200, 2022.0131, 1120, 1250])
        self.app._save_data(month)
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2022.0201', '%Y.%m%d'))
        self._add_to_test_files(month)
        assert (self.app.monthly_start_times.size == 0)
        assert (self.app.monthly_end_times.size == 0)
        assert (self.app.weekly_start_times == np.array([2022.0131, 890, 1240])).all()
        assert (self.app.weekly_end_times == np.array([2022.0131, 1120, 1250])).all()

    @freeze_time("2022-07-06")
    def test_register_time_less_than_1_min(self):
        self.app.monthly_start_times = np.array([2022.0704, 330, 450])
        self.app.monthly_end_times = np.array([2022.0704, 400, 500])
        self.app.last_start_time = datetime.strptime('2022.0706 07:00:29', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2022.0706 07:01:28', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2022.0701', self.date_format))
        assert (self.app.monthly_start_times == np.array([2022.0704, 330, 450])).all()
        assert (self.app.monthly_end_times == np.array([2022.0704, 400, 500])).all()

    @freeze_time("2022-07-06")
    def test_register_time_2022_jul_06_0700_to_1800(self):
        self.app.monthly_start_times = np.array([2022.0704, 330, 450])
        self.app.monthly_end_times = np.array([2022.0704, 400, 500])
        self.app.last_start_time = datetime.strptime('2022.0706 07:00:00', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2022.0706 08:00:00', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2022.0701', self.date_format))
        assert (self.app.monthly_start_times == np.array([2022.0704, 330, 450, 2022.0706, 420])).all()
        assert (self.app.monthly_end_times == np.array([2022.0704, 400, 500, 2022.0706, 480])).all()

    @freeze_time("2022-05-24")
    def test_register_time_2022_may_24_1100_to_1220(self):
        self.app.monthly_start_times = np.array([])
        self.app.monthly_end_times = np.array([])
        self.app.last_start_time = datetime.strptime('2022.0524 11:00:00', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2022.0524 12:20:00', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2022.0501', self.date_format))
        assert (self.app.monthly_start_times == np.array([2022.0524, 660])).all()
        assert (self.app.monthly_end_times == np.array([2022.0524, 740])).all()

    @freeze_time("2019-08-04")
    def test_register_time_2019_aug_3_2350_to_aug_4_0000(self):
        self.app.monthly_start_times = np.array([])
        self.app.monthly_end_times = np.array([])
        self.app.last_start_time = datetime.strptime('2019.0803 23:50:18', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2019.0804 00:00:26', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2019.0801', self.date_format))
        assert (self.app.monthly_start_times == np.array([2019.0803, 1430])).all()
        assert (self.app.monthly_end_times == np.array([2019.0803, 1440])).all()

    @freeze_time("2019-08-04")
    def test_register_time_2019_aug_3_2350_to_aug_4_0015(self):
        self.app.monthly_start_times = np.array([])
        self.app.monthly_end_times = np.array([])
        self.app.last_start_time = datetime.strptime('2019.0803 23:50:18', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2019.0804 00:14:38', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2019.0801', self.date_format))
        assert (self.app.monthly_start_times == np.array([2019.0803, 1430, 2019.0804, 0])).all()
        assert (self.app.monthly_end_times == np.array([2019.0803, 1440, 2019.0804, 15])).all()

    @freeze_time("2019-09-01")
    def test_register_time_2019_aug_31_2350_to_sep_1_0000(self):
        self.app.monthly_start_times = np.array([])
        self.app.monthly_end_times = np.array([])
        self.app.last_start_time = datetime.strptime('2019.0831 23:50:18', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2019.0901 00:00:14', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2019.0801', self.date_format))
        self._add_to_test_files(datetime.strptime('2019.0901', self.date_format))
        assert (self.app.monthly_start_times == np.array([])).all()
        assert (self.app.monthly_end_times == np.array([])).all()
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2019.0901', self.date_format))
        assert (self.app.weekly_start_times == np.array([2019.0831, 1430])).all()
        assert (self.app.weekly_end_times == np.array([2019.0831, 1440])).all()

    @freeze_time("2019-09-01")
    def test_register_time_2019_aug_31_2350_to_sep_1_0015(self):
        self.app.monthly_start_times = np.array([])
        self.app.monthly_end_times = np.array([])
        self.app.last_start_time = datetime.strptime('2019.0831 23:50:18', '%Y.%m%d %H:%M:%S')
        self.app.last_end_time = datetime.strptime('2019.0901 00:14:38', '%Y.%m%d %H:%M:%S')
        self.app._register_time()
        self._add_to_test_files(datetime.strptime('2019.0801', self.date_format))
        self._add_to_test_files(datetime.strptime('2019.0901', self.date_format))
        assert (self.app.monthly_start_times == np.array([2019.0901, 0])).all()
        assert (self.app.monthly_end_times == np.array([2019.0901, 15])).all()
        self.app.weekly_start_times, self.app.weekly_end_times, self.app.monthly_start_times, self.app.monthly_end_times = self.app._load_data(datetime.strptime('2019.0901', self.date_format))
        assert (self.app.weekly_start_times == np.array([2019.0831, 1430, 2019.0901, 0])).all()
        assert (self.app.weekly_end_times == np.array([2019.0831, 1440, 2019.0901, 15])).all()


if __name__ == '__main__':
    unittest.main()