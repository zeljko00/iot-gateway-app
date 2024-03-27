import unittest

from src.data_service import parse_incoming_data

class TestDataService(unittest.TestCase):
    def test_parse_incoming_data_correct(self):
        val, typ = parse_incoming_data("nesto shemso=3 indeks_dva bla bla bla halid=invalid", "datatype")
        assert(val == 3.0)
        assert(typ == "invalid")

    # TODO: ne raditi ovako nego sa @pytest.mark.parametrize i/ili @fixture
    def test_parse_incoming_data_wrong(self):
        # TODO: ovaj zakomentarisani, ne javlja gresku, odnosno ako nesto nije broj dobijemo 0?!?!
        # TODO: poruke su iste u oba slucaja, treba ih razlikovati
        # with self.assertLogs('customErrorLogger', level='ERROR') as cm:
        #     _ = parse_incoming_data("nesto shemso=nije_broj indeks_dva bla bla bla halid=invalid", "datatype")
        #     self.assertEqual(cm.output, ['ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso indeks_dva bla bla bla halid=invalid'])
        with self.assertLogs('customErrorLogger', level='ERROR') as cm:
            _ = parse_incoming_data("nesto shemso=3 indeks_dva bla bla bla halit-ddd", "datatype")
            self.assertEqual(cm.output, ['ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso=3 indeks_dva bla bla bla halit-ddd'])
        with self.assertLogs('customErrorLogger', level='ERROR') as cm:
            _ = parse_incoming_data("nesto shemso=3", "datatype")
            self.assertEqual(cm.output, ['ERROR:customErrorLogger:Invalid datatype data format! - nesto shemso=3'])