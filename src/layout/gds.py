import gdspy


class Polygon(object):

    def __init__(self, layer_num, data_type, bb):
        self.bb = data_type
        self.layer_num = layer_num
        self.data_type = data_type
        self.layer_id = "{}-{}".format(layer_num, data_type)
        self.bb = bb
        self.width = self.bb[2] - self.bb[0]
        self.height = self.bb[3] - self.bb[1]
        self.is_polygon = False


class Label(object):

    def __init__(self, layer_num, data_type, text, x, y):
        self.layer_num = layer_num
        self.data_type = data_type
        self.layer_id = "{}-{}".format(layer_num, data_type)
        self.x = x
        self.y = y
        self.text = text


class GDSManage(object):
    def __init__(self):
        self.gds_lib = gdspy.GdsLibrary
        self.polygon_data = {}
        self.label_data = {}
        self.top_cell_name = ''
        self.scale = 0

    def load_gds(self, gds_file):
        self.gds_lib = gdspy.GdsLibrary(infile=r"{}".format(gds_file))
        self.top_cell_name = self.gds_lib.top_level()[0].name
        self.scale = round(self.gds_lib.unit / self.gds_lib.precision)
        self._set_data()

    @staticmethod
    def float_to_int_floor(float_num, scale):
        return int(round(float_num * scale))

    def _set_polygon_data(self):
        cell = self.gds_lib.cells[self.top_cell_name]
        polygons = cell.get_polygons(by_spec=True)
        for [layer_num, data_type], polygon_list in polygons.items():
            self.polygon_data["{}-{}".format(layer_num, data_type)] = []
            for polygon_array in polygon_list:
                if polygon_array.__len__() == 4:
                    bb = [(self.float_to_int_floor(point[0], self.scale),
                           self.float_to_int_floor(point[1], self.scale)) for point in polygon_array]
                    pg = Polygon(layer_num, data_type, [bb[0][0], bb[0][1], bb[2][0], bb[2][1]])
                    self.polygon_data[pg.layer_id].append(pg)

    def _set_get_label_data(self):
        cell = self.gds_lib.cells[self.top_cell_name]
        labels_list = cell.get_labels()
        for label in labels_list:
            layer_num = int(label.layer)
            data_type = int(label.texttype)
            text = label.text
            x = self.float_to_int_floor(label.position[0], self.scale)
            y = self.float_to_int_floor(label.position[1], self.scale)
            label = Label(layer_num, data_type, text, x, y)
            if label.layer_id not in self.label_data:
                self.label_data[label.layer_id] = []
            self.label_data[label.layer_id].append(label)

    def _set_data(self):
        self._set_polygon_data()
        self._set_get_label_data()

