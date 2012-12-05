#!/usr/bin/python
import pstats
stats = pstats.Stats('profile.txt')
stats.sort_stats('time').reverse_order().print_stats()
