import argparse
import collections
import garnett
import pyriodic

parser = argparse.ArgumentParser(
    description='Generate code to import an external unit cell')
parser.add_argument('input_file',
    help='Input unit cell file to read')
parser.add_argument('-o', '--output',
    help='Output target to append to')

template = """Structure.from_fractional_coordinates(
    {positions},
    {types},
    {box})
"""

def main(input_file, output):
    with garnett.read(input_file) as traj:
        frame = traj[0]

        type_map = collections.defaultdict(lambda: len(type_map))
        types = [type_map[t] for t in frame.types]

        structure = pyriodic.Structure(
            frame.positions, types, frame.box.get_box_array())

        formatted = template.format(
            positions=structure.fractional_coordinates,
            types=types,
            box=structure.box)

        if output:
            with open(output, 'a') as f:
                f.write(formatted)
        else:
            print(formatted)

if __name__ == '__main__': main(**vars(parser.parse_args()))
