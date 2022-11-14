import matplotlib.pyplot as plt
import os
import json

from repos_parser import Database

database = Database()
# funcs_counter = database.total_mpi_functions()
# keys, values = zip(*dict(sorted(funcs_counter.items(), key=lambda item: item[1], reverse=True)).items())
#
# fig, ax = plt.subplots(1, 1)
# ax.set_title('Functions Distribution')
# ax.bar(keys[:30], values[:30], color='g')
# plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
# plt.show()
