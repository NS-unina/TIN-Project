package org.tin.app;

import org.osgi.service.component.annotations.*;
// import org.osgi.service.component.annotations.Activate;
// import org.osgi.service.component.annotations.Component;
// import org.osgi.service.component.annotations.Deactivate;
// import org.osgi.service.component.annotations.Reference;
// import org.osgi.service.component.annotations.ReferenceCardinality;

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


import java.io.*;
import java.util.Properties;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Base64;



@Component(immediate = true)// Ensure this component is activated immediately
public class AppComponent {
    
    private final Logger log = LoggerFactory.getLogger(getClass());
    private ApplicationId appId;
    private TinProcessor tinProcessor = new TinProcessor();

    //Config values
    private String tinIp;    //ip address for tin manager server
    private String tinPort;  //port for tin manager server
    private String firstIp;  
    private String lastIp;
    private int[] allowed_ports;

    @Reference (cardinality = ReferenceCardinality.MANDATORY)
    protected CoreService coreService;

    @Reference (cardinality = ReferenceCardinality.MANDATORY)  
    protected PacketService packetService;  


    @Activate
    protected void activate() {

        log.info("TinApp has been activated!");
        appId = coreService.registerApplication("org.tin.app");
        log.info("App id: " + appId.id());
        packetService.addProcessor(tinProcessor, PacketProcessor.director(2));

        //Read properties file
        Properties prop = new Properties();
        String fileName = "/opt/onos/apps/tin.config";
        
        try (FileInputStream fis = new FileInputStream(fileName)) {
            prop.load(fis);
        } catch (FileNotFoundException ex) {
            log.info("Error: "+ ex.getMessage());
        } catch (IOException ex) {
            log.info("Error: "+ ex.getMessage());
        }

        log.info(prop.getProperty("tin.ip"));
        
        tinIp=prop.getProperty("tin.ip");
        tinPort= prop.getProperty("tin.port");
        firstIp=prop.getProperty("check.firstIp");
        lastIp= prop.getProperty("check.lastIp");

        log.info(prop.getProperty("check.allowed_ports"));


        String allowed_ports_string=prop.getProperty("check.allowed_ports");
        if (allowed_ports_string != null) {
                // Convert the string back to an int array
                String[] parts = allowed_ports_string.split(",");
                int[] intArray = new int[parts.length];
                for (int i = 0; i < parts.length; i++) {
                    intArray[i] = Integer.parseInt(parts[i].trim());

                }
                for (int num : intArray) {
                    log.info(num + " ");
                }
                allowed_ports=intArray;
            }

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
        Ethernet ethPacket = inboundPacket.parsed();

        ConnectPoint connectPoint = inboundPacket.receivedFrom();
        DeviceId deviceId = connectPoint.deviceId();

        if (ethPacket == null){
            return;
        }
        
        HostId srcId = HostId.hostId(ethPacket.getSourceMAC());
        HostId dstId = HostId.hostId(ethPacket.getDestinationMAC());
        log.info("New connection detected: {} -> {}", srcId, dstId);
        log.info("cringe" + ethPacket.getEtherType());

        if (ethPacket.getEtherType() == Ethernet.TYPE_IPV4){
            IPv4 ipv4Packet = (IPv4) ethPacket.getPayload();

            String srcIp = IPv4.fromIPv4Address(ipv4Packet.getSourceAddress());
            String dstIp = IPv4.fromIPv4Address(ipv4Packet.getDestinationAddress());

            log.info ("New ipv4 connection: {} -> {}", srcIp, dstIp);
              
            try {
                log.info ("first ip, last, dst: " + firstIp + " " + lastIp + " " + dstIp);
                if (check.ipCheck(firstIp, lastIp, dstIp)){
                    log.info ("Check ");

                    if (ipv4Packet.getPayload() instanceof TCP) {
                        TCP tcpPacket = (TCP) ipv4Packet.getPayload();
                        int srcPort = tcpPacket.getSourcePort();
                        int dstPort = tcpPacket.getDestinationPort();

                        log.info("Port: " + dstPort);
                        if(check.portCheck(dstPort,allowed_ports)){
                            log.info("(TCP) Forbidden port");
                            
                            //Request creating flow for redirection
                            HttpClient client = HttpClient.newHttpClient();
                            String payload_redirection = "{"
                                + "\"src_ip\": \"" + srcIp + "\","
                                + "\"dst_ip\": \"" + dstIp + "\","
                                + "\"src_port\": \"" + srcPort + "\","
                                + "\"dst_port\": \"" + dstPort + "\","
                                + "\"ovs_id\": \"" + deviceId + "\""
                                + "}";
                            log.info("payload_redirection" + payload_redirection);
                            HttpRequest request_redirection = HttpRequest.newBuilder()
                                .uri(URI.create("http://"+tinIp+":"+tinPort+"/tinmanager/tcp/addflow"))
                                .header("Content-Type", "application/json")
                                .POST(HttpRequest.BodyPublishers.ofString(payload_redirection))
                                .build();
                            CompletableFuture<HttpResponse<String>> futureResponse_redirection = client.sendAsync(request_redirection, HttpResponse.BodyHandlers.ofString());
                            futureResponse_redirection.thenAccept(response -> {log.info("Response Code (redirection): " + response.statusCode());  log.info("Response Body (redirection): " + response.body());});
                            log.info ("Request_redirection send");
                            }
                        }

                    if (ipv4Packet.getPayload() instanceof UDP) {
                        UDP udpPacket = (UDP) ipv4Packet.getPayload();
                        int srcPort = udpPacket.getSourcePort();
                        int dstPort = udpPacket.getDestinationPort();

                        log.info("Port: " + dstPort);
                        if(check.portCheck(dstPort, allowed_ports)){
                            log.info("(UDP) Forbidden port");
                            //Request
                            HttpClient client = HttpClient.newHttpClient();
                            String payload_redirection = "{"
                                + "\"src_ip\": \"" + srcIp + "\","
                                + "\"dst_ip\": \"" + dstIp + "\","
                                + "\"src_port\": \"" + srcPort + "\","
                                + "\"dst_port\": \"" + dstPort + "\","
                                + "\"ovs_id\": \"" + deviceId + "\""
                                + "}";                            
                                HttpRequest request = HttpRequest.newBuilder()
                                .uri(URI.create("http://"+tinIp+":"+tinPort+"/tinmanager/udp/addflow"))
                                .header("Content-Type", "application/json")
                                .POST(HttpRequest.BodyPublishers.ofString(payload_redirection))
                                .build();
                            CompletableFuture<HttpResponse<String>> futureResponse = client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
                            futureResponse.thenAccept(response -> {log.info("Response Code: " + response.statusCode());  log.info("Response Body: " + response.body());});
                            }
                        }
                    
                    }
            }              
            catch (UnknownHostException e){
                log.info ("Error: " + e.getMessage());
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

        public boolean portCheck (int dstPort, int[] allowed_ports){

            for (int i=0; i<allowed_ports.length; i++){
                if (allowed_ports[i] == dstPort){
                    return false;
                }
            }
            return true;
        }
    }
}