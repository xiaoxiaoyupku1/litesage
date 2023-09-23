from src.layout.gds import GDSManage


class LayoutApplication(object):

    def __init__(self):
        self.gds_manage = GDSManage()
        self.layer_list_view_data = []
        self.net_list_view_data = []

    def load_gds(self, gds_path):
        self.gds_manage.load_gds(gds_path)

    def get_layer_list_view_data(self):
        if not self.layer_list_view_data:
            layer_list = list(set(list(self.gds_manage.polygon_data.keys()) + list(self.gds_manage.label_data.keys())))
            layer_list.sort(key=lambda x: int(x.replace('-', '')))
            self.layer_list_view_data = layer_list

        return self.layer_list_view_data

    def get_net_list_view_data(self):
        if not self.net_list_view_data:
            layer_num_set = set([int(layer_id.split('-')[0]) for layer_id in self.gds_manage.polygon_data.keys()])
            net_list_view_data = []
            for layer_id, label_list in self.gds_manage.label_data.items():
                label_num = int(layer_id.split('-')[0])
                if label_num in layer_num_set:
                    net_list_view_data.extend(list(set([label.text for label in label_list])))
            net_list_view_data = list(set(net_list_view_data))
            net_list_view_data.sort(key=lambda x: x)
            self.net_list_view_data = net_list_view_data

        return self.net_list_view_data
