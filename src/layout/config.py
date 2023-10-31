import configparser
import os
from src.layout.layout_utils import OnGrid


class Config(configparser.ConfigParser):
    """
    set ConfigParser options for case sensitive.
    """

    def __init__(self, config_file_path, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
        self.config_file_path = config_file_path
        self.poly_layer_id = ''
        self.met1_layer_id = '7-0'
        self.met1_txt_layer_id = '121-0'
        self.met2_layer_id = '9-0'
        self.met2_txt_layer_id = '122-0'
        self.met3_layer_id = ''
        self.met4_layer_id = ''
        self.met5_layer_id = ''
        self.contact_layer_id = '6-0'
        self.via1_layer_id = '8-0'
        self.via2_layer_id = ''
        self.via3_layer_id = ''
        self.via4_layer_id = ''
        self.size_contact_equal = 500
        self.space_contact_min = 500
        self.overlap_contact_min = 200
        self.size_v1_equal = 260
        self.space_v1_min = 250
        self.overlap_v1_min = 200
        self.size_v2_equal = 550
        self.space_v2_min = 600
        self.overlap_v2_min = ''
        self.size_v3_equal = ''
        self.space_v3_min = ''
        self.overlap_v3_min = ''
        self.size_v4_equal = ''
        self.space_v4_min = ''
        self.overlap_v4_min = ''
        self.layer_id_order = []
        self.via_set = set()
        self.metal_set = {self.met1_layer_id, self.met2_layer_id}
        self.routing_set = set()
        self.metal_order = []
        self.contact_via_order = []
        self.on_grid = 10
        self.routing_width = 1200
        self.met1_routing_space = 600
        self.met2_routing_space = 1200
        self.met3_routing_space = 0
        self.met4_routing_space = 0
        self.met5_routing_space = 0
        self.metal_space_map = {}
        self.met_to_net_map = {
            self.met1_layer_id: self.met1_txt_layer_id,
            self.met2_layer_id: self.met2_txt_layer_id,
        }
        self.run()

    def on_grid_value_floor(self, value):
        return OnGrid.on_grid_floor(self.on_grid, value)

    def on_grid_value_ceil(self, value):
        return OnGrid.on_grid_ceil(self.on_grid, value)

    def optionxform(self, optionstr):
        return optionstr

    def parse_metal(self):
        metal_map = {}
        net_map = {}
        for item in list(self['metal_info'].items()):
            if 'txt' in item[0]:
                net_map[item[0]] = item[1]
            else:
                metal_map[item[0]] = item[1]
                if hasattr(self, item[0]):
                    setattr(self, item[0], item[1])
                    self.metal_set.add(getattr(self, item[0]))
        for metal_name, layer_id in metal_map.items():
            metal_txt_name = "{}_txt".format(metal_name)
            if metal_txt_name in net_map:
                self.met_to_net_map[layer_id] = net_map[metal_txt_name]

    def parse_contact_via(self):
        for item in list(self['contact_via_info'].items()):
            if hasattr(self, item[0]):
                setattr(self, item[0], item[1])
                self.via_set.add(getattr(self, item[0]))

    def update_layer_id_order(self):
        self.layer_id_order = [getattr(self, "met{}_layer_id".format(idx)) for idx in range(1, 6) if
                               getattr(self, "met{}_layer_id".format(idx))]

    def get_minimum_overlap_length(self, layer_id1, layer_id2):
        length = 0
        via_id = self.get_between_via_layer_id(layer_id1, layer_id2)
        if via_id == self.contact_layer_id:
            length = self.overlap_contact_min*2+self.size_contact_equal
        else:
            for idx in range(1, 10):
                if hasattr(self, 'via{}_layer_id'.format(idx)) and \
                        getattr(self, 'via{}_layer_id'.format(idx)) == via_id:
                    length = getattr(self, 'overlap_v{}_min'.format(idx))*2+getattr(self, 'size_v{}_equal'.format(idx))
                    break

        return length

    def get_upper_layer_id(self, current_layer_id):
        if current_layer_id in self.layer_id_order:
            idx = self.layer_id_order.index(current_layer_id)
            if len(self.layer_id_order) > idx + 1:
                return self.layer_id_order[idx + 1]

    def get_lower_layer_id(self, current_layer_id):
        if current_layer_id in self.layer_id_order:
            idx = self.layer_id_order.index(current_layer_id)
            if idx - 1 >= 0:
                return self.layer_id_order[idx - 1]

    def is_jump(self, layer_id1, layer_id2):
        if layer_id1 in self.metal_order and layer_id2 in self.metal_order:
            order1 = self.metal_order.index(layer_id1)
            order2 = self.metal_order.index(layer_id2)
            if abs(order1-order2) <= 1:
                return True
        return False

    def update_fab_dr(self):
        for item in list(self['fab_dr'].items()):
            if hasattr(self, item[0]):
                setattr(self, item[0], int(item[1]))

    def get_between_via_layer_id(self, layer_id1, layer_id2):
        if layer_id1 != layer_id2 and layer_id1 in self.metal_set and layer_id2 in self.metal_set:
            order1 = self.metal_order.index(layer_id1)
            order2 = self.metal_order.index(layer_id2)
            if abs(order1-order2) == 1:
                min_order = min(order1, order2)
                if min_order == 0:
                    return self.contact_layer_id
                else:
                    return getattr(self, 'via{}_layer_id'.format(min_order))

    def get_via_contact_dr(self, layer_id):

        order = self.contact_via_order.index(layer_id)
        if order == 0:
            x_space, y_space, size_width, size_length, overlap_via_contact_min =\
                self.space_contact_min, self.space_contact_min, self.size_contact_equal, \
                self.size_contact_equal, self.overlap_contact_min
        else:
            x_space, y_space, size_width, size_length, overlap_via_contact_min = getattr(
                self, 'space_v{}_min'.format(order)), getattr(self, 'space_v{}_min'.format(order)), getattr(
                self, 'size_v{}_equal'.format(order)),  getattr(self, 'size_v{}_equal'.format(order)), getattr(
                self, 'overlap_v{}_min'.format(order))
        return x_space, y_space, size_width, size_length, overlap_via_contact_min

    def shift_via_to_center(self, bb, via_list):
        new_via_list = []
        if via_list:
            x_list = []
            y_list = []
            for via_bb in via_list:
                x_list.extend([via_bb[0], via_bb[2]])
                y_list.extend([via_bb[1], via_bb[3]])
            all_via_bb = [min(x_list), min(y_list), max(x_list), max(y_list)]
            shift_x = self.on_grid_value_floor(((bb[2]-bb[0]) - (all_via_bb[2]-all_via_bb[0]))/2)+bb[0] - all_via_bb[0]
            shift_y = self.on_grid_value_floor(((bb[3]-bb[1]) - (all_via_bb[3]-all_via_bb[1]))/2)+bb[1] - all_via_bb[1]
            for via_bb in via_list:
                new_via_list.append([via_bb[0]+shift_x, via_bb[1]+shift_y, via_bb[2]+shift_x, via_bb[3]+shift_y])

        return new_via_list

    def fab_contact_via_space_array_processor(self, bb, layer_id):
        import math
        from src.layout.layout_utils import OnGrid
        x_space, y_space, size_width, size_length, overlap_via_contact_min = \
            [int(v) for v in self.get_via_contact_dr(layer_id)]
        bb = [bb[0]+overlap_via_contact_min, bb[1]+overlap_via_contact_min,
              bb[2]-overlap_via_contact_min, bb[3]-overlap_via_contact_min]
        bb_width = bb[3]-bb[1]
        bb_length = bb[2]-bb[0]
        first_box = [bb[0], bb[1], bb[0]+size_length, bb[1]+size_width]
        res = []
        if x_space and y_space:
            if (bb_length - size_length) % (size_length + x_space) == 0:
                col_nums = int((bb_length - size_length) / (size_length + x_space)) + 1
                first_row = [(first_box[0] + idx * (size_length + x_space), first_box[1], first_box[2] +
                              idx * (size_length + x_space), first_box[3]) for idx in range(col_nums)]
            else:
                left_width = (bb_length - size_length) % (size_length + x_space)
                col_nums = math.floor((bb_length - size_length) / (size_length + x_space))
                h_add_value = 0
                if col_nums and left_width / col_nums >= 5:
                    h_add_value = OnGrid.on_grid_floor(self.on_grid, left_width / col_nums)
                col_nums = col_nums + 1
                first_row = [(first_box[0] + (size_length + x_space+h_add_value) * idx, first_box[1], first_box[2] +
                              (size_length + x_space + h_add_value) * idx, first_box[3]) for idx in range(col_nums)]

            v_add_value = 0
            if (bb_width - size_width) % (size_width + y_space) == 0:
                col_nums = int((bb_width - size_width) / (size_width + y_space)) + 1
            else:
                left_width = (bb_width - size_width) % (size_width + y_space)
                col_nums = math.floor((bb_width - size_width) / (size_width + y_space))
                if col_nums and left_width / col_nums >= 5:
                    v_add_value = OnGrid.on_grid_floor(self.on_grid, left_width / col_nums)
                col_nums = col_nums + 1
            res = [(item[0], item[1] + idx * (size_width + y_space + v_add_value), item[2], item[3] + idx *
                    (size_width + y_space + v_add_value)) for idx in range(col_nums) for item in first_row]
        elif x_space:
            if (bb_length - size_length) % (size_length + x_space) == 0:
                nums = int((bb_length - size_length) / (size_length + x_space)) + 1
                res = [(first_box[0] + idx*(size_length + x_space), first_box[1], first_box[2] +
                        idx*(size_length + x_space), first_box[3]) for idx in range(nums)]
            else:
                left_width = (bb_length - size_length) % (size_length + x_space)
                nums = math.floor((bb_length - size_length) / (size_length + x_space))
                add_value = 0
                if nums and left_width / nums >= 5:
                    add_value = OnGrid.on_grid_floor(self.on_grid, left_width / nums)
                nums = nums + 1
                res = [(first_box[0] + (size_length + x_space + add_value)*idx, first_box[1], first_box[2] +
                        (size_length + x_space + add_value)*idx, first_box[3]) for idx in range(nums)]
        elif y_space:
            if (bb_width-size_width) % (size_width+y_space) == 0:
                nums = int((bb_width-size_width)/(size_width+y_space))+1
                res = [(first_box[0], first_box[1]+idx*(size_width+y_space), first_box[2],
                        first_box[3]+idx*(size_width+y_space)) for idx in range(nums)]
            else:
                left_width = (bb_width-size_width) % (size_width+y_space)
                nums = math.floor((bb_width-size_width) / (size_width+y_space))
                add_value = 0
                if nums and left_width/nums >= 5:
                    add_value = OnGrid.on_grid_floor(self.on_grid, left_width/nums)
                nums = nums+1
                res = [(first_box[0], first_box[1] + idx * (size_width + y_space + add_value), first_box[2],
                        first_box[3] + idx * (size_width + y_space + add_value)) for idx in range(nums)]
        return self.shift_via_to_center(bb, res)

    def is_metal(self, layer_id):
        if layer_id in self.metal_order:
            return True
        return False

    def is_adjacent_metal(self, layer_id1, layer_id2):
        if not self.is_metal(layer_id1) or not self.is_metal(layer_id2):
            return False
        order_1 = self.metal_order.index(layer_id1)
        order_2 = self.metal_order.index(layer_id2)
        if abs(order_1-order_2) == 1:
            return True
        return False

    def get_metal_space(self, layer_id):
        return self.metal_space_map.get(layer_id, 0)

    def update_metal_order(self):

        self.metal_order = [
            self.poly_layer_id,
            self.met1_layer_id,
            self.met2_layer_id,
            self.met3_layer_id,
            self.met4_layer_id,
            self.met5_layer_id
        ]

    def update_via_contact_order(self):
        self.contact_via_order = [
            self.contact_layer_id,
            self.via1_layer_id,
            self.via2_layer_id,
            self.via3_layer_id,
            self.via4_layer_id,
        ]

    def update_global_parameter(self):
        for item in list(self['global_parameter'].items()):
            if hasattr(self, item[0]):
                setattr(self, item[0], int(item[1]))

    def update_metal_space_map(self):
        for idx in range(1, 6):
            layer_id_name = 'met{}_layer_id'.format(idx)
            if hasattr(self, layer_id_name) and getattr(self, layer_id_name):
                self.metal_space_map[getattr(self, layer_id_name)] = getattr(self, 'met{}_routing_space'.format(idx))

    def run(self):
        file = self.config_file_path

        # if os.path.exists(file):
        # self.read(file)
        # self.sections()
        # self.parse_metal()
        # self.parse_contact_via()
        self.update_layer_id_order()
        # self.update_fab_dr()
        self.update_metal_order()
        self.update_via_contact_order()
        # self.update_global_parameter()
        self.update_metal_space_map()
