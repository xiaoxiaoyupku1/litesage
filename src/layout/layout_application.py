from src.layout.gds_manage import GDSManage
from src.layout.config import Config
from src.layout.layout_utils import Polygon


class LayoutApplication(object):

    def __init__(self, main_file_path):
        self.gds_manage = GDSManage()
        self.layer_list_view_data = []
        self.net_list_view_data = []
        self.config = Config(main_file_path)
        self.top_layout_cell = None

    def open_gds(self, gds_path):
        self.top_layout_cell = self.gds_manage.open_gds(gds_path)

    def save_data(self, polygon_list, text_list):
        self.top_layout_cell.add_polygons(polygon_list)
        self.top_layout_cell.add_cell_text(text_list)

    def is_via(self, layer_id):
        return layer_id in self.config.via_set

    def is_metal(self, layer_id):
        return layer_id in self.config.metal_set

    def is_routing_layer(self, layer_id):
        pass

    def is_poly(self, layer_id):
        pass

    def save_gds(self, gds_path):

        res, title, err_msg = True, '', ''

        if not self.top_layout_cell:
            res = False
            err_msg = 'Save fail ,no gds content to save!'
            title = "Empty Content"
            return res, title, err_msg
        try:
            self.gds_manage.write_gds(gds_path, self.top_layout_cell)
        except Exception as e:
            print(e)
            res = True
            err_msg = 'Save Fail!'
            title = 'System Err'
        return res, title, err_msg

    def get_via_bb_list(self, pg1: Polygon, pg2: Polygon):
        via_bb_list = []
        via_layer_id = self.config.get_between_via_layer_id(pg1.layer_id, pg2.layer_id)
        if via_layer_id:
            overlap_bb = Polygon.get_overlap_bb(pg1.bb, pg2.bb)
            if overlap_bb:
                via_bb_list = self.config.fab_contact_via_space_array_processor(overlap_bb, via_layer_id)
        return via_bb_list, via_layer_id

    def get_all_layer_id(self):

        all_layer_id_list = list(self.gds_manage.polygon_data.keys())
        all_layer_id_list.sort(key=lambda x: int(x.replace('-', '')))
        return all_layer_id_list

