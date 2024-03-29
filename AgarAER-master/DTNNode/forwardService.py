from collections import deque
import queue
import threading
from struct import pack
import logging
import time
from forwarderPredictor import ForwarderPredictor
from dtnpacket import DTNPacket
from forwardMessage import Forward_Message


class ForwardService:
    """Class que trata de dar forward dos pacotes da cache """

    def __init__(self, peer, storeService):
        self.peer = peer
        self.predictor = ForwarderPredictor(self.peer)
        self.nextHopNeighbor = None
        self.storeService = storeService
        self.controlMessages = []
        self.forwardQueue = deque()
        self.forwardingToPeer = threading.Thread(target=self.forwardLoop)
        self.forwardingToPeer.daemon = True
        self.forwardingToPeer.start()
        self.neighHasSeen = {}

    def forwardLoop(self):
        while True:
            if len(self.forwardQueue) == 0: continue
            packet_report, addr = self.forwardQueue.popleft()
            self.peer.sendMessageToNeighbour(packet_report,addr)

    def forwardPacket(self, packet_report, addr):
        packet_digest = packet_report.get_digest()
        packet = self.storeService.requestPacket(packet_digest)
        #logging.debug(f'predicted forward {self.nextHopNeighbor}')

        if packet is None:
            return False
        dtnpacket = DTNPacket(packet_report.packet_src, packet_report.packet_dst,
                              packet_report.port, packet, packet_digest, packet_report.timestamp, packet_report.fromOverlay)
        self.forwardQueue.append((dtnpacket,addr))
        return True

    def call_predictor(self):
        self.nextHopNeighbor = self.predictor.predict()

    def neigh_seen_packet(self, packet_digest, addr):
        tmpset = self.neighHasSeen.get(addr,None)
        if tmpset is None:
            tmpset = set()
            self.neighHasSeen[addr] = tmpset
        tmpset.update(packet_digest)

    def has_neigh_seen_packet(self, packet_digest, addr):
        tmpset = self.neighHasSeen.get(addr,None)
        if tmpset is not None:
            return packet_digest in tmpset
        return False

    def forward(self):  ## CHAMAR O PREDICTOR ANTES DE DAR FORWARD GARANTE QUE SO PREVEMOS O NEXT HOP QUANDO TAMOS COM ALGUM VIZINHO
        #logging.debug('forward')
        self.call_predictor()
        #logging.debug(f'predicted hop: {self.nextHopNeighbor.isOverlay()}')
        tmp_report_list = []
        if self.nextHopNeighbor is None:
            return

        if self.nextHopNeighbor.isAlive():

            if not self.nextHopNeighbor.isOverlay():
                lstToSniff = list(self.peer.get_neighborsaddr_to_sniff())
                self.send_ForwardMessage(lstToSniff, True)

            shelves = self.storeService.getShelves()

            for shelve in shelves:

                tmpl = shelve.listPortQueueSortedByTimestamp()
                #logging.debug(f'forward {tmpl}')

                for p, queuelist in tmpl:
                    tmp_nopacket_list = []
                    for packet_report in queuelist:

                        if packet_report.timestamp > self.nextHopNeighbor.stats.get_passedByTime() and not self.nextHopNeighbor.isOverlay():
                            continue
                        if packet_report.packet_src == self.nextHopNeighbor.ip:
                            continue
                        if self.has_neigh_seen_packet(packet_report.get_digest(), self.nextHopNeighbor.ip):
                            continue

                        status = self.forwardPacket(packet_report, self.nextHopNeighbor.ip)
                        if not status:
                            tmp_nopacket_list.append(packet_report)
                        else:
                            tmp_report_list.append(packet_report.get_digest())
                    if len(tmp_nopacket_list) > 0:
                        tmpl.removePacketReports(p, tmp_nopacket_list)

                self.neigh_seen_packet(tmp_report_list, self.nextHopNeighbor.ip)

                # Obter os pacotes todos em cache
                # Enviar para o no predicted
                # So obter os que ainda não foram capturados

    def send_ForwardMessage(self, addr, sniff):
        forwardMessage = Forward_Message(addr, sniff)
        self.peer.sendMessageToNeighbour(forwardMessage, self.nextHopNeighbor.ip)

    def get_nextHopNeighbor(self):
        return self.nextHopNeighbor

    def clear(self):
        pass
