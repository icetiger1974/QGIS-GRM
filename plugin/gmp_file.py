import xml.etree.ElementTree as ET

from utils import *
from config import NAMESPACE

class GMPFILE(object):

    def __init__(self, path):
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()
        self.project_settings_node = self.tree.find("{0}ProjectSettings".format(NAMESPACE))
        self.subwatershed_settings_node = self.tree.find("{0}SubWatershedSettings".format(NAMESPACE))
        self.watch_points_node = self.tree.find("{0}WatchPoints".format(NAMESPACE))
        self.flow_control_grid_node = self.tree.find("{0}FlowControlGrid".format(NAMESPACE))
        self.green_ampt_parameter_node = self.tree.find("{0}GreenAmptParameter".format(NAMESPACE))
        self.land_cover_node = self.tree.find("{0}LandCover".format(NAMESPACE))
        self.subwatershed_list = self.root.findall('{0}SubWatershedSettings'.format(NAMESPACE))

    def get_project_settings_attributes(self, attribute_name):
        path = "{0}{1}".format(NAMESPACE, attribute_name)
        return self.project_settings_node.find(path).text

    def get_computation_time_step_sec(self):
        return ""

    def get_enable_analyzer(self):
        return False

    def set_select_watershed_index(self):
        for i in self.subwatershed_list:
            if c_bool(i.find(NAMESPACE+"UserSet").text):
                self.selected_watershed_index = self.subwatershed_list.index(i)

    def set_project_settings_attributes(self, attribute_name, value):
        node = self.project_settings_node.find("{0}{1}".format(NAMESPACE, attribute_name))
        node.text = str(value)

    def set_computation_time_step_sec(self, value):
        pass

    def set_enable_analyzer(self, value):
        pass

    def get_selected_watershed_info(self, tag_name):
        i = self.subwatershed_list[self.selected_watershed_index]
        return i.find(NAMESPACE+tag_name).text if i.find(NAMESPACE+tag_name) != None else ""

    def set_selected_watershed_info(self, tag_name=None, dlg_obj=None):
        if dlg_obj:
            self.updated_watershed = dlg_obj.select_watershed.currentText()

        if tag_name:
            for subwatershed in self.subwatershed_list:
                if subwatershed.find(NAMESPACE+"ID").text == self.updated_watershed:
                    return subwatershed.find(NAMESPACE+tag_name)

    def set_watershed(self, value):
        watershed = self.set_selected_watershed_info(tag_name="ID")
        watershed.text = str(value)

    def set_watershed_attributes(self, attribute_name, value):
        node = self.set_selected_watershed_info(tag_name=attribute_name)
        if node:
            ini_saturation.text = str(value)

    def set_apply_initial_stream_check(self, value):
        apply_initial_stream_check = self.set_selected_watershed_info(tag_name ="UserSet")
        apply_initial_stream_check.text = bool_c(value)

    def save(self, output_file):
        self.tree.write(open(output_file, 'wb'), encoding='utf-8', xml_declaration=True,
                        default_namespace="http://tempuri.org/GRMProject.xsd")
