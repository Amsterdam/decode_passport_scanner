from mrtd import MRTD
import config

passport = MRTD(config.MRZ_CONFIG['mrz2'])
print(passport.do_bac())
