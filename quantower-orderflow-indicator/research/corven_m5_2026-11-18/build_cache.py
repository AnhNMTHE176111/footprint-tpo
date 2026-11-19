"""Builds F_m5.pkl (per-level features) and E_m5.pkl (exhaustion table) used by all fit/eval scripts. Run first."""
import sys; sys.path.insert(0,'.')
from feats import build; from common import *; from exh_feats import exh_table
D,B=load(); build(D,B).to_pickle('F_m5.pkl'); exh_table(D,B).to_pickle('E_m5.pkl')
