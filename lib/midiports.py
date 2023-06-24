import mido
from lib import connectall
import time
import threading
import queue

class MidiPorts:
    def __init__(self, usersettings):
        self.usersettings = usersettings
        self.pending_queue = []
        self.last_activity = 0
        self.inport = None
        self.playport = None

        # checking if the input port was previously set by the user
        port = self.usersettings.get_setting_value("input_port")
        if port != "default":
            try:
                self.inport = mido.open_input(port)
                print("Inport loaded and set to " + port)
            except:
                print("Can't load input port: " + port)
        else:
            # if not, try to find the new midi port
            try:
                for port in mido.get_input_names():
                    if "Through" not in port and "RPi" not in port and "RtMidOut" not in port and "USB-USB" not in port:
                        self.inport = mido.open_input(port)
                        self.usersettings.change_setting_value("input_port", port)
                        print("Inport set to " + port)
                        break
            except:
                print("no input port")
        # checking if the play port was previously set by the user
        port = self.usersettings.get_setting_value("play_port")
        if port != "default":
            try:
                self.playport = mido.open_output(port)
                print("Playport loaded and set to " + port)
            except:
                print("Can't load input port: " + port)
        else:
            # if not, try to find the new midi port
            try:
                for port in mido.get_output_names():
                    if "Through" not in port and "RPi" not in port and "RtMidOut" not in port and "USB-USB" not in port:
                        self.playport = mido.open_output(port)
                        self.usersettings.change_setting_value("play_port", port)
                        print("Playport set to " + port)
                        break
            except:
                print("no play port")
        
        self.output_port = None
        self.queue = None
        for outport in mido.get_output_names():
            print(outport)
        port = self.usersettings.get_setting_value("output_port")
        if port != "default":
            try:
                self.output_port = mido.open_output(port)
                self.queue = queue.Queue()
                print(f"Output port set to {port}")
            except:
                print(f"Can't open output port! {e}")
        else:
            #Add output port
            try:
                for port in mido.get_output_names():
                    if "raspberrypi:casio" in port.lower():
                        self.output_port = mido.open_output(port)
                        self.queue = queue.Queue()
                        break
                print(f"Output port set to {port}")
            except Exception as e:
                print(f"Can't open output port! {e}")
                self.output_port = None
                self.queue = None
        self.outputThread = threading.Thread(target=self.send_output, daemon=True)
        self.outputThread.start()
        self.portname = "inport"

    def connectall(self):
        # Reconnect the input and playports on a connectall
        self.reconnect_ports()
        # Now connect all the remaining ports
        connectall.connectall()

    def add_instance(self, menu):
        self.menu = menu

    def change_port(self, port, portname):
        try:
            destroy_old = None
            if port == "inport":
                destroy_old = self.inport
                self.inport = mido.open_input(portname)
                self.usersettings.change_setting_value("input_port", portname)
            elif port == "playport":
                destroy_old = self.playport
                self.playport = mido.open_output(portname)
                self.usersettings.change_setting_value("play_port", portname)
            elif port == "output_port":
                destroy_old = self.output_port
                self.output_port = mido.open_output(portname)
                self.usersettings.change_setting_value("output_port", portname)
            self.menu.render_message("Changing " + port + " to:", portname, 1500)
            if destroy_old != None:
                destroy_old.close()
            self.menu.show()
        except:
            self.menu.render_message("Can't change " + port + " to:", portname, 1500)
            self.menu.show()

    def reconnect_ports(self):
        try:
            destroy_old = self.inport
            port = self.usersettings.get_setting_value("input_port")
            self.inport = mido.open_input(port)
            if destroy_old != None:
                time.sleep(0.002)
                destroy_old.close()
        except:
            print("Can't reconnect input port: " + port)
        try:
            destroy_old = self.playport
            port = self.usersettings.get_setting_value("play_port")
            self.playport = mido.open_output(port)
            if destroy_old != None:
                time.sleep(0.002)
                destroy_old.close()
        except:
            print("Can't reconnect play port: " + port)
        try:
            destroy_old = self.output_port
            port = self.usersettings.get_setting_value("output_port")
            self.output_port = mido.open_output(port)
            if destroy_old != None:
                time.sleep(0.002)
                destroy_old.close()
        except:
            print("Can't reconnect output port: " + port)
    
    def send_output(self):
        while True:
            time.sleep(0.02)  # sleep for 20 milliseconds
            if self.queue is None: continue
            msg = self.queue.get()
            if self.output_port is not None and msg is not None: self.output_port.send(msg)
    
    def add_to_queue(self, msg):
        if self.queue is not None:
            self.queue.put(msg)
