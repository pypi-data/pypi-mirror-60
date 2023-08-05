# import sys
# import struct
# from functools import reduce
# from operator import add

# VREF = 4.5
# GAIN = 24
# FACTOR_SCALE = VREF / (24 * ((2 ** 23) - 1))

# input_ = sys.argv[1]

# input_file = open(input_, 'r')
# output_file = open(input_.replace('raw', 'bin'), 'wb')

# line = input_file.readline()
# sample = 0

# while line:
    # data_eeg = reduce(add, [list(struct.pack("I", int(float(n) // FACTOR_SCALE))[:3]) for n in line.split(',')[0:9]])

    # pre = ['A0', hex(sample % 255)]
    # end = ['00', '00', '00', '00', '00', '00', 'C0']
    # data = [int(v, 16) for v in pre] + data_eeg + [int(v, 16) for v in end]

    # output_file.write(bytearray(data))
    # line = input_file.readline()
    # sample += 1


# output_file.close()
# input_file.close()
