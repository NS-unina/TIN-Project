package org.tin.app;

import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;

import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;

import org.onosproject.net.packet.PacketService;
import org.onosproject.net.packet.PacketProcessor;
import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.InboundPacket;
import org.onosproject.net.HostId;
import org.onosproject.net.ConnectPoint;
import org.onosproject.net.DeviceId;

import org.onlab.packet.Ethernet;
import org.onlab.packet.IPv4;
import org.onlab.packet.TCP;
import org.onlab.packet.UDP;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

import java.net.InetAddress;
import java.net.UnknownHostException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component(immediate = true)// Ensure this component is activated immediately
public class AppComponent {

    private final Logger log= LoggerFactory.getLogger(getClass());
    private ApplicationId appId;
    private TinProcessor tinProcessor = new TinProcessor();


    @Reference (cardinality = ReferenceCardinality.MANDATORY)
    protected CoreService coreService;

    @Reference (cardinality = ReferenceCardinality.MANDATORY)  
    protected PacketService packetService;


    @Activate
    protected void activate() {        
        log.info("TinApp has been activated!");
        appId = coreService.registerApplication("org.tin.app");
        log.info("App id: "+ appId.id());

        packetService.addProcessor(tinProcessor, PacketProcessor.director(2));


    }

    @Deactivate
    protected void deactivate() {
        packetService.removeProcessor(tinProcessor);
        log.info("TinApp has been deactivated.");
    }


    private class TinProcessor implements PacketProcessor{
        
        @Override
        public void process(PacketContext context) {
            if (context.isHandled()) {
                return;
            }

        Check check = new Check();
        InboundPacket inboundPacket = context.inPacket();
        ConnectPoint connectPoint = inboundPacket.receivedFrom();
        DeviceId deviceId = connectPoint.deviceId();
        Ethernet ethPacket = inboundPacket.parsed();

        if (ethPacket == null){
            return;
        }

        HostId srcId = HostId.hostId(ethPacket.getSourceMAC());
        HostId dstId = HostId.hostId(ethPacket.getDestinationMAC());
        log.info("New connection detected: {} -> {}", srcId, dstId);
        log.info("cringe"+ethPacket.getEtherType());

        if (ethPacket.getEtherType() == Ethernet.TYPE_IPV4){
            IPv4 ipv4Packet = (IPv4) ethPacket.getPayload();

            String srcIp = IPv4.fromIPv4Address(ipv4Packet.getSourceAddress());
            String dstIp = IPv4.fromIPv4Address(ipv4Packet.getDestinationAddress());

            log.info ("New ipv4 connection: {} -> {}", srcIp, dstIp);
              
            try {
                if (check.ipCheck("10.1.3.1", "10.1.3.3", dstIp)){
                    
                    if (ipv4Packet.getPayload() instanceof TCP) {
                        TCP tcpPacket = (TCP) ipv4Packet.getPayload();
                        int srcPort = tcpPacket.getSourcePort();
                        int dstPort = tcpPacket.getDestinationPort();

                        log.info("Port: " + dstPort);
                        if(check.portCheck(dstPort)){
                            log.info("(TCP) Forbidden port");
                            //Request
                            HttpClient client = HttpClient.newHttpClient();
                            String payload = "{"
                                + "\"src_ip\": \"" + srcIp + "\","
                                + "\"dst_ip\": \"" + dstIp + "\","
                                + "\"src_port\": \"" + srcPort + "\","
                                + "\"dst_port\": \"" + dstPort + "\","
                                + "\"ovs_id\": \"" + deviceId + "\""
                                + "}";
                            log.info("payload" + payload);
                            HttpRequest request = HttpRequest.newBuilder()
                                .uri(URI.create("http://127.0.0.1:5001/network/create_int"))
                                .header("Content-Type", "application/json")
                                .POST(HttpRequest.BodyPublishers.ofString(payload))
                                .build();
                            CompletableFuture<HttpResponse<String>> futureResponse = client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
                            futureResponse.thenAccept(response -> {log.info("Response Code: " + response.statusCode());  log.info("Response Body: " + response.body());});
                            }
                        }

                    if (ipv4Packet.getPayload() instanceof UDP) {
                        UDP udpPacket = (UDP) ipv4Packet.getPayload();
                        int srcPort = udpPacket.getSourcePort();
                        int dstPort = udpPacket.getDestinationPort();

                        log.info("Port: " + dstPort);
                        if(check.portCheck(dstPort)){
                            log.info("(UDP) Forbidden port");
                            //Request
                            HttpClient client = HttpClient.newHttpClient();
                            String payload = "{\"src_ip\":\"foo\", \"dst_ip\":\"bar\", \"port\":1}";
                            HttpRequest request = HttpRequest.newBuilder()
                                .uri(URI.create("http://127.0.0.1:5001/network/create_int"))
                                .header("Content-Type", "application/json")
                                .POST(HttpRequest.BodyPublishers.ofString(payload))
                                .build();
                            CompletableFuture<HttpResponse<String>> futureResponse = client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
                            futureResponse.thenAccept(response -> {log.info("Response Code: " + response.statusCode());  log.info("Response Body: " + response.body());});
                            }
                        }
                    
                    }
            }              
            catch (UnknownHostException e){
                log.info ("Error");
            }

            
        }
        }
    }

    private class Check {
        public long ipToLong(InetAddress ip) {
            byte[] octets = ip.getAddress();
            long result = 0;
            for (byte octet : octets) {
                result <<= 8;
                result |= octet & 0xff;
            }
            return result;
        }

        public boolean ipCheck(String firstIp, String lastIp, String testIp) throws UnknownHostException {
            long ipLo = ipToLong(InetAddress.getByName(firstIp));
            long ipHi = ipToLong(InetAddress.getByName(lastIp));
            long ipToTest = ipToLong(InetAddress.getByName(testIp));

        return (ipToTest >= ipLo && ipToTest <= ipHi);
        }

        public boolean portCheck (int dstPort){
            int[] allowed_ports = {5001};

            for (int i=0; i<allowed_ports.length; i++){
                if (allowed_ports[i] == dstPort){
                    return false;
                }
            }
            return true;
        }
    }
}