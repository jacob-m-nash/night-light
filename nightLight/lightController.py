import socket

class lightController(object):


    def FindLights():
        discoveryPort = 56700
        UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        getServicePacket = b'' #todo https://lan.developer.lifx.com/docs/querying-the-device-for-data#discovery 
        UDPServerSocket.sendto(getServicePacket,('<broadcast>',discoveryPort)) 
        reply = UDPServerSocket.recvfrom(40)
        print(reply)

    def encodePacket(protocol,addressable,tagged,origin,source,target,res_required,ack_required,sequence,pkt_type,payload, payloadSize):
        protocolBits = format(protocol,"016b") #todo move entire  protocol header into new function 
        addressableBits = format(addressable,"01b")
        taggedBits = format(tagged,"01b")
        originBits = format(origin,"02b")
        sourceBits = format(source,"032b")
        targetBits = lightController.MacAddressToBits(target)
        reserved6Bytes = format(0,"048b") # 6 Bytes = 48 bits 
        res_requiredBits = format(res_required,"01b")
        ack_requiredBits = format(ack_required,"01b")
        reserved6Bits = format(0,"06b")
        sequenceBits = format(sequence,"08b")
        reserved8Bytes = format(0,"064b")
        pkt_typeBits = format(pkt_type,"016b")
        reserved2Bytes = format(0,"016b")
        payloadBits = format(payload,f"0{payloadSize}b")
        sizelessPacket = protocolBits + addressableBits + taggedBits + originBits + sourceBits + targetBits + reserved6Bytes + res_requiredBits + ack_requiredBits + reserved6Bits + sequenceBits + reserved8Bytes + pkt_typeBits + reserved2Bytes + payloadBits
        packetSize = len(sizelessPacket)
        packetSizeBits = (packetSize / 8) + 2
        packet = format(packetSizeBits,"016b") + sizelessPacket
        return packet

    def MacAddressToBits(address):
        address = [address[i:i+2] for i in range(0, len(address), 2)] #taken from https://stackoverflow.com/questions/9475241/split-string-every-nth-character 
        bits = ""
        for h in address:
            i = int(h,16)
            bits += format(i, "08b")
        
        return bits






