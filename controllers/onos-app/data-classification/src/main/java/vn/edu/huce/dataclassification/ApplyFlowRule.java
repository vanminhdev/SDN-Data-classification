package vn.edu.huce.dataclassification;

import org.onlab.packet.IpPrefix;
import org.onlab.packet.TpPort;
import org.onlab.packet.EthType.EtherType;
import org.onlab.packet.Ethernet;
import org.onosproject.app.ApplicationService;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.flow.DefaultFlowRule;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.FlowRuleService;
import org.onosproject.net.flow.TrafficSelector;
import org.onosproject.net.flow.TrafficTreatment;
import org.onosproject.net.meter.MeterId;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import vn.edu.huce.dataclassification.dtos.flowRule.CreateFlowRuleDto;
import vn.edu.huce.dataclassification.utils.AppInfo;

@Component(immediate = true, service = { ApplyFlowRule.class })
public class ApplyFlowRule {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private FlowRuleService flowRuleService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private ApplicationService appService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected CoreService coreService;

    private ApplicationId appId;

    @Activate
    public void activate() {
        coreService.registerApplication(AppInfo.APP_NAME);
        appId = appService.getId(AppInfo.APP_NAME);
        log.info("ApplyFlowRule Started");
    }

    @Deactivate
    public void deactivate() {
        log.info("ApplyFlowRule Stopped");
    }

    public void apply(CreateFlowRuleDto input) {
        log.info("Applying flow rule: {}", input);

        DeviceId deviceId = DeviceId.deviceId(input.getDeviceId());

        // Tạo criteria để match
        var builder = DefaultTrafficSelector.builder();

        builder.matchEthType(Ethernet.TYPE_IPV4);

        // Nếu có IP thì match IP
        if (input.getIpSrc() != null && !input.getIpSrc().isEmpty()) {
            builder.matchIPSrc(IpPrefix.valueOf(input.getIpSrc()));
        }
        if (input.getIpDst() != null && !input.getIpDst().isEmpty()) {
            builder.matchIPDst(IpPrefix.valueOf(input.getIpDst()));
        }

        // Nếu có port thì match port
        if (input.getTcpPortSrc() != 0) {
            builder.matchTcpSrc(TpPort.tpPort(input.getTcpPortSrc()));
        }
        if (input.getTcpPortDst() != 0) {
            builder.matchTcpDst(TpPort.tpPort(input.getTcpPortDst()));
        }
        if (input.getUdpPortSrc() != 0) {
            builder.matchUdpSrc(TpPort.tpPort(input.getUdpPortSrc()));
        }
        if (input.getUdpPortDst() != 0) {
            builder.matchUdpDst(TpPort.tpPort(input.getUdpPortDst()));
        }

        TrafficSelector selector = builder.build();

        // Tạo action để forward gói tin
        TrafficTreatment treatment = DefaultTrafficTreatment.builder()
                .meter(MeterId.meterId(1))
                .build();

        // Tạo flow rule
        FlowRule flowRule = DefaultFlowRule.builder()
                .forDevice(deviceId)
                .withSelector(selector)
                .withTreatment(treatment)
                .withPriority(40000)
                .fromApp(appId)
                .makeTemporary(60)
                .build();

        // Áp dụng FlowRule vào thiết bị
        flowRuleService.applyFlowRules(flowRule);
    }
}
