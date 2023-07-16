import socket

class lightController(object):


    def FindLights():
        discoveryPort = 56700
        UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDPServerSocket.settimeout(20)
        getServicePacket = lightController.encodePacket(1024,1,1,0,123,"0000000",1,0,100,2,"")
        print("sending packet")
        print(getServicePacket.encode())
        UDPServerSocket.sendto(getServicePacket.encode(),('<broadcast>',discoveryPort)) 
        reply,addr = UDPServerSocket.recvfrom(40)
        print(reply)
        print(addr)
        return

    def encodePacket(protocol,addressable,tagged,origin,source,target,res_required,ack_required,sequence,pkt_type,payload):
        sizelessFrameHeadder = lightController.getSizelessFrameHeadder(protocol,addressable,tagged,origin,source)
        frameAddress = lightController.getFrameAddress(target,res_required,ack_required,sequence)
        protocolHeadder = lightController.getProtocolHeadder(pkt_type)
        sizelessPacket = sizelessFrameHeadder + frameAddress + protocolHeadder + payload
        packetSizeBits = (len(sizelessPacket) // 8) + 2
        packet = format(packetSizeBits,"08b") + format(0,"08b") + sizelessPacket
        hexPacket = hex(int(packet, 2))
        return packet

    def getSizelessFrameHeadder(protocol,addressable,tagged,origin,source):
        protocol16Bits = format(protocol,"016b")
        addressableBits = format(addressable,"01b")
        taggedBits = format(tagged,"01b")
        originBits = format(origin,"02b")
        sourceBits = format(source,"08b") + format(0,"024b")
        return "00000000" + originBits + taggedBits + addressableBits +  protocol16Bits[4:8] + sourceBits 

    def getFrameAddress(target,res_required,ack_required,sequence):
        newTarget = target + "0000" # todo why do we need this?
        targetBits = lightController.MacAddressToBits(newTarget)
        reserved6Bytes = format(0,"048b") # 6 Bytes = 48 bits 
        res_requiredBits = format(res_required,"01b")
        ack_requiredBits = format(ack_required,"01b")
        reserved6Bits = format(0,"06b")
        sequenceBits = format(sequence,"08b")
        return targetBits + reserved6Bytes  + reserved6Bits + ack_requiredBits + res_requiredBits + sequenceBits

    def getProtocolHeadder(pkt_type):
        reserved8Bytes = format(0,"064b")
        pkt_typeBits = format(pkt_type,"08b") + format(0,"08b")
        reserved2Bytes = format(0,"016b")
        return reserved8Bytes + pkt_typeBits + reserved2Bytes

    def MacAddressToBits(address):
        address = [address[i:i+2] for i in range(0, len(address), 2)] #taken from https://stackoverflow.com/questions/9475241/split-string-every-nth-character 
        bits = ""
        for h in address:
            i = int(h,16)
            bits += format(i, "08b")
        
        return bits

payload = "00000000010101010101010111111111111111111111111111111111101011000000110100000000000000000000000000000000"
test = lightController.encodePacket(1024,1,0,0,2,"d073d5001337",0,1,1,102,payload)







