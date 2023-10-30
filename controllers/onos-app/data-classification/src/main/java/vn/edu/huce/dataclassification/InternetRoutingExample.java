package vn.edu.huce.dataclassification;

import org.onlab.packet.Ethernet;
import org.onlab.packet.IpPrefix;
import org.onosproject.app.ApplicationService;
import org.onosproject.core.ApplicationId;
import org.onosproject.net.DeviceId;
import org.onosproject.net.PortNumber;
import org.onosproject.net.flow.*;
import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.PacketProcessor;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;

@Component(immediate = true, service = {InternetRoutingExampleInterface.class})
public class InternetRoutingExample implements InternetRoutingExampleInterface {
    @Reference
    private FlowRuleService flowRuleService;
    @Reference
    private ApplicationService appService;

    @Override
    public void addInternetRoute(PacketContext context) {
        // Create a traffic selector to match packets with a specific destination IP address
        TrafficSelector selector = DefaultTrafficSelector.builder()
                .matchEthType(Ethernet.TYPE_IPV4) // IPv4 packets
                .matchIPDst(IpPrefix.valueOf("0.0.0.0/0")) // Any destination IP address
                .build();

        // Create a traffic treatment to specify the egress port (port to the Internet)
        TrafficTreatment treatment = DefaultTrafficTreatment.builder()
                .setOutput(PortNumber.portNumber(2)) // Egress port to the Internet
                .build();

        ApplicationId appId = appService.getId("vn.edu.huce.data-classification");

        // Create a flow rule with the selector and treatment
        FlowRule flowRule = DefaultFlowRule.builder()
                .forDevice(DeviceId.deviceId("of:0000000000000001")) // Device ID
                .withSelector(selector)
                .withTreatment(treatment)
                .fromApp(appId) // Application name
                .makePermanent() // Permanent rule
                .build();

        // Add the flow rule to the flow rule service
        flowRuleService.applyFlowRules(flowRule);
    }
}
