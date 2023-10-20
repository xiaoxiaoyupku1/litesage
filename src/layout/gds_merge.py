import gdspy

def merge_gds_files(file1_path, file2_path, output_path):

    gds1 = gdspy.GdsLibrary()
    gds1.read_gds(file1_path)

    gds2 = gdspy.GdsLibrary()
    gds2.read_gds(file2_path)

    for cell_name in gds2.cells:
        if cell_name in gds1.cells:
            gds1.cells[cell_name].add(gds2.cells[cell_name])
        else:
            gds1.add(gds2.cells[cell_name])

    gds1.write_gds(output_path)

if __name__ == '__main__':

    import optparse
    mdopt = optparse.OptionParser()
    mdopt.add_option('-m', '--metal_gds_file', dest='metal_gds', type='string', default='', help='metal_gds_file.')
    mdopt.add_option('-d', '--device_gds_file', dest='device_gds', type='string', default='', help='device_gds_file.')
    mdopt.add_option('-o', '--output', dest='output', type='string', default='', help='output file.')
    options, args = mdopt.parse_args()
    metal_gds = options.metal_gds,
    metal_gds = metal_gds[0]
    device_gds = options.device_gds,
    device_gds = device_gds[0]
    output = options.output,
    output = output[0]
    if metal_gds == '' or device_gds == '':
        print('Please input gds file!')
    else:
        if output == '':
            output = './'
        if output[-1] != '/':
            output += '/'
        cellname = metal_gds.split('/')[-1]
        cellname = cellname.split('.')[0] + '.full.gds'
        outfile = output + cellname
        merge_gds_files(metal_gds, device_gds, outfile)