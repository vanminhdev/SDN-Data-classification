package vn.edu.huce.dataclassification;

import java.lang.module.ModuleDescriptor.Builder;

import org.onlab.packet.IpPrefix;
import org.onlab.packet.TpPort;
import org.onosproject.app.ApplicationService;
import org.onosproject.core.ApplicationId;
import org.onosproject.net.DeviceId;
import org.onosproject.net.flow.DefaultFlowRule;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.FlowRuleService;
import org.onosproject.net.flow.TrafficSelector;
import org.onosproject.net.flow.TrafficTreatment;
import org.onosproject.net.meter.MeterId;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import vn.edu.huce.dataclassification.dtos.flowRule.FlowRuleDto;
import vn.edu.huce.dataclassification.utils.AppInfo;

@Component(immediate = true, service = ApplyFlowRule.class)
public class ApplyFlowRule {
    private final Logger log = LoggerFactory.getLogger(getClass());
    @Reference
    private FlowRuleService flowRuleService;
    @Reference
    private ApplicationService appService;

    public void apply(FlowRuleDto input) {
        log.info("Applying flow rule: {}", input);

        ApplicationId appId = appService.getId(AppInfo.APP_NAME);
        DeviceId deviceId = DeviceId.deviceId(input.getDeviceId());

        // Tạo criteria để match
        var builder = DefaultTrafficSelector.builder();

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
                .meter(MeterId.meterId(0))
                .build();

        // Tạo flow rule
        FlowRule flowRule = DefaultFlowRule.builder()
                .forDevice(deviceId)
                .withSelector(selector)
                .withTreatment(treatment)
                .withPriority(100)
                .fromApp(appId)
                .makeTemporary(60)
                .build();

        // Áp dụng FlowRule vào thiết bị
        flowRuleService.applyFlowRules(flowRule);
    }
}
