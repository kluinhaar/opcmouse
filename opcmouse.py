import sys
import struct
#sys.path.insert(0, "..")
from opcua import ua, Server

if __name__ == "__main__":
    # redirect stdout to logfile
    sys.stdout = open('/var/log/opcmouse.log', 'a')

    print "Change OS processname."
    if sys.platform == 'linux2':
        import ctypes
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
        libc.prctl(15, 'opcmouse', 0, 0, 0)

    print "Setup OPC UA Server"
    server = Server(shelffile="cache")

    print "Set OPC UA Server endpoint"
    server.set_endpoint("opc.tcp://0.0.0.0:4841/MouseOPCServer/")

    uri = "http://cherrypi"
    print "setup OPC UA server namespace."
    idx = server.register_namespace(uri)

    print "Get OPC UA Objects node."
    objects = server.get_objects_node()

    print "Populating address space."
    myobj = objects.add_object(idx, "MyObject")

    print "Create OPC UA vars."
    opcmouseloopcounter = myobj.add_variable(idx, "opcmouseloopcounter", 0)
    opcmouseloopcounter.set_writable()
    mousex = myobj.add_variable(idx, "mousex", 0)
    mousey = myobj.add_variable(idx, "mousey", 0)
    mousebLeft = myobj.add_variable(idx, "mousebLeft", False)
    mousebMiddle = myobj.add_variable(idx, "mousebMiddle", False)
    mousebRight = myobj.add_variable(idx, "mousebRight", False)

    # mouse event handler...
    file = open( "/dev/input/mice", "rb" )
    def getMouseEvent():
        buf = file.read(3)
        button = ord( buf[0] )
        bLeft = ( button & 0x1 ) > 0
        bMiddle = ( button & 0x4 ) > 0
        bRight = ( button & 0x2 ) > 0
        x, y = struct.unpack( "bb", buf[1:] )

        # Set OPC variabelen
        mousex.set_value(x)
        mousey.set_value(y)
        mousebLeft.set_value(bLeft)
        mousebMiddle.set_value(bMiddle)
        mousebRight.set_value(bRight)

    print "starting OPC server"
    server.start()

    print "Start main loop"
    try:
        while True:
            getMouseEvent()
            opcmouseloopcounter.set_value(opcmouseloopcounter.get_value() + 1)
    finally:
        file.close()
        server.stop()
