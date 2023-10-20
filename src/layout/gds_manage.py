import gdspy
from src.layout.layout_cell import LayoutCell
from src.layout.layout_utils import Polygon, Label


class GDSManage(object):
    def __init__(self):
        self.gds_lib = gdspy.GdsLibrary
        self.top_cell_name = ''
        self.scale = 0
        self.gds_path = ''
        self.open_gds_flag = False
        self.polygon_data = {}
        self.label_data = {}

    def open_gds(self, gds_path):
        if self.open_gds_flag:
            self.reset()
        self.gds_path = gds_path
        self.gds_lib = gdspy.GdsLibrary(infile=r"{}".format(gds_path))
        self.top_cell_name = self.gds_lib.top_level()[0].name
        self.scale = round(self.gds_lib.unit / self.gds_lib.precision)
        top_layout_cell = LayoutCell(
            self.top_cell_name, self.scale)
        self._set_layout_data(top_layout_cell)
        self.open_gds_flag = True
        return top_layout_cell

    def reset(self):
        self.gds_lib = gdspy.GdsLibrary
        self.top_cell_name = ''
        self.scale = 0
        self.gds_path = ''
        self.open_gds_flag = False

    def write_gds(self, gds_path, top_layout_cell: LayoutCell):
        gdspy.current_library = gdspy.GdsLibrary(unit=self.gds_lib.unit, precision=self.gds_lib.precision)
        top_cell = top_layout_cell.get_gds_cell()
        for ref_cell in top_layout_cell.references:
            child_cell = ref_cell.get_gds_cell()
            top_cell.add(gdspy.CellReference(child_cell))
        gdspy.write_gds(gds_path)
        return

    def update_gds_data(self, polygon_data_list):
        res, title, err_msg = True, '', ''
        if not self.open_gds_flag:
            err_msg = 'save fail ,no gds content to save!'
            res = False
            title = "empty content"
            return res, title, err_msg
        try:
            cell = self.gds_lib.cells[self.top_cell_name]
            for pg in polygon_data_list:

                layer_dt_dict = {'layer': int(pg.layer_num), 'datatype': pg.data_type}

                gds_pg = gdspy.Rectangle((pg.bb[0] / self.scale, pg.bb[1] / self.scale),
                                         (pg.bb[2] / self.scale, pg.bb[3] / self.scale), **layer_dt_dict)
                cell.add(gds_pg)
        except Exception as e:
            err_msg = str(e)
            res = False
            title = 'system err'
        return res, title, err_msg

    def save_gds_bak(self, gds_path):
        res, title, err_msg = True, '', ''
        if not self.open_gds_flag:
            res = False
            err_msg = 'save fail ,no gds content to save!'
            title = "empty content"
            return res, title, err_msg
        try:
            self.gds_lib.write_gds(gds_path)
        except Exception as e:
            res = True
            err_msg = str(e)
            title = 'system err'
        return res, title, err_msg

    @staticmethod
    def float_to_int_floor(float_num, scale):
        return int(round(float_num * scale))

    def get_top_cell_data(self):
        cell = self.gds_lib.cells[self.top_cell_name]
        references = cell.references
        cell.references = []
        top_cell_polygons = cell.get_polygons(by_spec=True)
        top_cell_labels = cell.get_labels()
        cell.references = references
        return top_cell_polygons, top_cell_labels

    def get_polygon_data_by_gds_polygons(self, gds_polygons):
        polygon_data = {}
        for [layer_num, data_type], polygon_list in gds_polygons.items():
            polygon_data["{}-{}".format(layer_num, data_type)] = []
            for polygon_array in polygon_list:
                point_list = [(self.float_to_int_floor(point[0], self.scale),
                               self.float_to_int_floor(point[1], self.scale)) for point in polygon_array]
                pg = Polygon(layer_num, data_type, point_list)
                polygon_data[pg.layer_id].append(pg)

        return polygon_data

    def get_label_data_by_gds_labels(self, gds_labels):
        label_data = {}
        for label in gds_labels:
            layer_num = int(label.layer)
            data_type = int(label.texttype)
            text = label.text
            x = self.float_to_int_floor(label.position[0], self.scale)
            y = self.float_to_int_floor(label.position[1], self.scale)
            label = Label(layer_num, data_type, text, x, y)
            if label.layer_id not in label_data:
                label_data[label.layer_id] = []
            label_data[label.layer_id].append(label)
        return label_data

    @staticmethod
    def get_reference_cell_data(reference_cell):

        ref_cell_polygons = reference_cell.get_polygons(by_spec=True)
        ref_cell_labels = reference_cell.get_labels()
        return ref_cell_polygons, ref_cell_labels

    def add_polygons(self, data):
        for layer_id, data_list in data.items():
            if layer_id not in self.polygon_data:
                self.polygon_data[layer_id] = []
            self.polygon_data[layer_id].extend(data_list)

    def add_labels(self, data):
        for layer_id, data_list in data.items():
            if layer_id not in self.label_data:
                self.label_data[layer_id] = []
            self.label_data[layer_id].extend(data_list)

    def _set_layout_data(self, top_layout_cell):

        top_cell_polygons, top_cell_labels = self.get_top_cell_data()
        top_layout_cell.polygon_data = self.get_polygon_data_by_gds_polygons(top_cell_polygons)
        self.add_polygons(top_layout_cell.polygon_data)
        top_layout_cell.label_data = self.get_label_data_by_gds_labels(top_cell_labels)
        self.add_labels(top_layout_cell.label_data)
        for reference_cell in self.gds_lib.cells[self.top_cell_name].references:
            ref_cell_polygons, ref_cell_labels = self.get_reference_cell_data(reference_cell)
            ref_layout_cell = LayoutCell(reference_cell.ref_cell.name, self.scale)
            top_layout_cell.add_reference_cell(ref_layout_cell)
            ref_layout_cell.polygon_data = self.get_polygon_data_by_gds_polygons(ref_cell_polygons)
            ref_layout_cell.set_bb()
            ref_layout_cell.label_data = self.get_label_data_by_gds_labels(ref_cell_labels)
            self.add_polygons(ref_layout_cell.polygon_data)
            self.add_labels(ref_layout_cell.label_data)



