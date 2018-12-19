from ... import lut
from ..skel import create_skel


def read_dalton(basis_lines, fname):
    '''Reads Dalton-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the nwchem format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '$'
    basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    bs_data = create_skel('component')

    i = 0

    while i < len(basis_lines):
        line = basis_lines[i]

        if line.lower().startswith('a '):
            element_Z = line.split()[1]
            i += 1

            # Shell am is strictly increasing (I hope)
            shell_am = 0

            while i < len(basis_lines) and not basis_lines[i].lower().startswith('a '):
                line = basis_lines[i]
                nprim, ngen = line.split()

                if not element_Z in bs_data['basis_set_elements']:
                    bs_data['basis_set_elements'][element_Z] = {}
                if not 'element_electron_shells' in bs_data['basis_set_elements'][element_Z]:
                    bs_data['basis_set_elements'][element_Z]['element_electron_shells'] = []

                element_data = bs_data['basis_set_elements'][element_Z]

                shell = {
                    'shell_function_type': 'gto',
                    'shell_harmonic_type': 'spherical',
                    'shell_region': '',
                    'shell_angular_momentum': [shell_am]
                }

                exponents = []
                coefficients = []

                i += 1
                for _ in range(int(nprim)):
                    line = basis_lines[i].replace('D', 'E')
                    line = line.replace('d', 'E')
                    lsplt = line.split()
                    exponents.append(lsplt[0])
                    coefficients.append(lsplt[1:])
                    i += 1

                shell['shell_exponents'] = exponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                shell['shell_coefficients'] = list(map(list, zip(*coefficients)))

                if len(shell['shell_coefficients']) != int(ngen):
                    print(ngen, len(shell['shell_coefficients']))
                    print(shell['shell_coefficients'])
                    raise RuntimeError("Number of general contractions does not equal what was given")

                element_data['element_electron_shells'].append(shell)
                shell_am += 1

    return bs_data
