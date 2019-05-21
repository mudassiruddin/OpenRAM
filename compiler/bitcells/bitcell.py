# See LICENSE for licensing information.
#
#Copyright (c) 2016-2019 Regents of the University of California and The Board
#of Regents for the Oklahoma Agricultural and Mechanical College
#(acting for and on behalf of Oklahoma State University)
#All rights reserved.
#
import design
import debug
import utils
from tech import GDS,layer,parameter,drc
import logical_effort

class bitcell(design.design):
    """
    A single bit cell (6T, 8T, etc.)  This module implements the
    single memory cell used in the design. It is a hand-made cell, so
    the layout and netlist should be available in the technology
    library.
    """

    pin_names = ["bl", "br", "wl", "vdd", "gnd"]
    internal_nets = ['Q', 'Qbar']
    type_list = ["OUTPUT", "OUTPUT", "INPUT", "POWER", "GROUND"] 
    (width,height) = utils.get_libcell_size("cell_6t", GDS["unit"], layer["boundary"])
    pin_map = utils.get_libcell_pins(pin_names, "cell_6t", GDS["unit"])

    def __init__(self, name=""):
        # Ignore the name argument
        design.design.__init__(self, "cell_6t")
        debug.info(2, "Create bitcell")

        self.width = bitcell.width
        self.height = bitcell.height
        self.pin_map = bitcell.pin_map
        self.add_pin_types(self.type_list)
        self.nets_match = self.check_internal_nets()
        
    def analytical_delay(self, corner, slew, load=0, swing = 0.5):
        parasitic_delay = 1
        size = 0.5 #This accounts for bitline being drained thought the access TX and internal node
        cin = 3 #Assumes always a minimum sizes inverter. Could be specified in the tech.py file.
        return logical_effort.logical_effort('bitline', size, cin, load, parasitic_delay, False)
 
    def list_bitcell_pins(self, col, row):
        """ Creates a list of connections in the bitcell, indexed by column and row, for instance use in bitcell_array """
        bitcell_pins = ["bl_{0}".format(col),
                        "br_{0}".format(col),
                        "wl_{0}".format(row),
                        "vdd",
                        "gnd"]
        return bitcell_pins
    
    def list_all_wl_names(self):
        """ Creates a list of all wordline pin names """
        row_pins = ["wl"]    
        return row_pins
    
    def list_all_bitline_names(self):
        """ Creates a list of all bitline pin names (both bl and br) """
        column_pins = ["bl", "br"]
        return column_pins
    
    def list_all_bl_names(self):
        """ Creates a list of all bl pins names """
        column_pins = ["bl"]
        return column_pins
        
    def list_all_br_names(self):
        """ Creates a list of all br pins names """
        column_pins = ["br"]
        return column_pins
        
    def analytical_power(self, corner, load):
        """Bitcell power in nW. Only characterizes leakage."""
        from tech import spice
        leakage = spice["bitcell_leakage"]
        dynamic = 0 #temporary
        total_power = self.return_power(dynamic, leakage)
        return total_power

    def check_internal_nets(self):
        """For handmade cell, checks sp file contains the storage nodes."""
        nets_match = True
        for net in self.internal_nets:
            nets_match = nets_match and self.check_net_in_spice(net)
        return nets_match
    
    def get_storage_net_names(self):
        """Returns names of storage nodes in bitcell in  [non-inverting, inverting] format."""
        #Checks that they do exist
        if self.nets_match:
            return self.internal_nets
        else:
            debug.info(1,"Storage nodes={} not found in spice file.".format(self.internal_nets))
            return None
    
    def get_wl_cin(self):
        """Return the relative capacitance of the access transistor gates"""
        #This is a handmade cell so the value must be entered in the tech.py file or estimated.
        #Calculated in the tech file by summing the widths of all the related gates and dividing by the minimum width.
        access_tx_cin = parameter["6T_access_size"]/drc["minwidth_tx"]
        return 2*access_tx_cin

    def build_graph(self, graph, inst_name, port_nets):        
        """Adds edges based on inputs/outputs. Overrides base class function."""
        self.add_graph_edges(graph, port_nets) 