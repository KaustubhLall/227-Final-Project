### Constants file if needed
from _testcapi import INT_MAX

inf = INT_MAX
INCUBATION_PERIOD = 5  # time before symptoms show up, and you become infectious
ACTIVE_DISEASE_PERIOD = INCUBATION_PERIOD + 10  # average duration of incubation + time to recover
RECOVERY = 0.02  # chance to survive covid
CHANCE_INFECTION = 0.05
