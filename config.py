import yaml

verbose = 2
with open('/home/nadavsc/LIGHTBITS/code2mpi/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    exclude_headers = config['exclude_headers']