from tvrecord.tvrecorder.dvbstreamer import DvbStreamer


def test_dvbstreamer():
    dvb = DvbStreamer()
    assert dvb.adaptor == 0
