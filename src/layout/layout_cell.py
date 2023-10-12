import gdspy
from src.layout.layout_utils import Status


class LayoutCell(object):

    def __init__(self, name, scale, magnification=None):
        self.name = name
        self.references = []
        self.polygon_data = {}
        self.label_data = {}
        self.all_layer_id_list = []
        self.scale = scale
        self.magnification = magnification
        self.bb = []

    def set_bb(self):
        x_list = []
        y_list = []
        for pg_list in self.polygon_data.values():
            for pg in pg_list:
                x_list.extend([pg.bb[0], pg.bb[2]])
                y_list.extend([pg.bb[1], pg.bb[3]])
        self.bb = [
            min(x_list),
            min(y_list),
            max(x_list),
            max(y_list)
        ]

    def add_polygons(self, polygon_list):
        for pg in polygon_list:
            if pg.layer_id not in self.polygon_data:
                self.polygon_data[pg.layer_id] = []
            self.polygon_data[pg.layer_id].append(pg)

    def add_cell_text(self, text_list):
        for label in text_list:
            if label.layer_id not in self.label_data:
                self.label_data[label.layer_id] = []
            self.label_data[label.layer_id].append(label)

    def add_labels(self, labels_list):
        for label in labels_list:
            if label.layer_id not in self.label_data:
                self.label_data[label.layer_id] = []
            self.label_data[label.layer_id].append(label)

    def add_reference_cell(self, ref_cell):
        self.references.append(ref_cell)

    def get_all_layer_id_list(self):
        if not self.all_layer_id_list:
            self.all_layer_id_list = list(set(
                [layer_id for layer_id in self.polygon_data.keys()] + [layer_id for layer_id in
                                                                       self.label_data.keys()]))
        return self.all_layer_id_list

    def add_polygon(self, cell):
        for layer_id, pg_list in self.polygon_data.items():
            layer_dt_dict = {'layer': int(pg_list[0].layer_num), 'datatype': pg_list[0].data_type}
            for pg in pg_list:
                if pg.status == Status.Normal:
                    if pg.is_polygon:
                        gds_pg = gdspy.Rectangle((pg.bb[0] / self.scale, pg.bb[1] / self.scale),
                                                 (pg.bb[2] / self.scale, pg.bb[3] / self.scale), **layer_dt_dict)
                        cell.add(gds_pg)
                    else:
                        e_polygon = [(coord[0] / self.scale, coord[1] / self.scale) for coord in pg.point_list]
                        gds_pg = gdspy.Polygon(e_polygon, **layer_dt_dict)
                        cell.add(gds_pg)

    def add_label(self, cell):
        for layer_id, label_list in self.label_data.items():
            layer_dt_dict = {'layer': int(label_list[0].layer_num), 'texttype': label_list[0].data_type}
            for label in label_list:
                if label.status == Status.Normal:
                    text = gdspy.Label(label.text, (label.x / self.scale, label.y / self.scale), **layer_dt_dict)
                    cell.add(text)

    def get_gds_cell(self):
        gds_cell = gdspy.Cell(self.name)
        self.add_polygon(gds_cell)
        self.add_label(gds_cell)
        return gds_cell
