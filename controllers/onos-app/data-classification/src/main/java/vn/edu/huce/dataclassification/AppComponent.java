/*
 * Copyright 2023-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package vn.edu.huce.dataclassification;

import org.onosproject.app.ApplicationService;
import org.onosproject.cfg.ComponentConfigService;
import org.onosproject.core.ApplicationId;
import org.onosproject.net.DeviceId;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.DefaultFlowRule;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.FlowRuleService;
import org.onosproject.net.packet.PacketProcessor;
import org.onosproject.net.packet.PacketService;
import org.osgi.service.component.ComponentContext;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Modified;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import vn.edu.huce.dataclassification.utils.AppInfo;

//import vn.edu.huce.dataclassification.utils.ApiClient;

import java.util.Dictionary;
import java.util.Properties;

import static org.onlab.util.Tools.get;

/**
 * Skeletal ONOS application component.
 */
@Component(immediate = true, service = { SomeInterface.class }, property = {
        "someProperty=Some Default String Value",
})
public class AppComponent implements SomeInterface {

    private final Logger log = LoggerFactory.getLogger(getClass());

    /**
     * Some configurable property.
     */
    private String someProperty;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected ComponentConfigService cfgService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private ApplicationService appService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected DeviceService deviceService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected FlowRuleService flowRuleService;

    @Reference
    private PacketService packetService;
    private PacketProcessor packetProcessor = new MyPacketProcessor();

    private ApplicationId appId;

    @Activate
    protected void activate() {
        cfgService.registerProperties(getClass());

        appId = appService.getId(AppInfo.APP_NAME);

        if (packetService != null) {
            packetService.addProcessor(packetProcessor, PacketProcessor.director(0));
        }

        // Lấy danh sách tất cả thiết bị (switch)
        deviceService.getDevices().forEach(device -> {
            applyCatchAllFlowRule(device.id());
        });

        log.info("Data Classification is Started");
    }

    @Deactivate
    protected void deactivate() {
        cfgService.unregisterProperties(getClass(), false);
        if (packetService != null) {
            packetService.removeProcessor(packetProcessor);
        }
        log.info("Data Classification is Stopped");
    }

    @Modified
    public void modified(ComponentContext context) {
        Dictionary<?, ?> properties = context != null ? context.getProperties() : new Properties();
        if (context != null) {
            someProperty = get(properties, "someProperty");
        }
        log.info("Data Classification is Reconfigured");
    }

    @Override
    public void someMethod() {
        log.info("Invoked");
    }

    private void applyCatchAllFlowRule(DeviceId deviceId) {
        FlowRule flowRule = DefaultFlowRule.builder()
                .forDevice(deviceId)
                .withSelector(DefaultTrafficSelector.builder().build()) // khớp mọi gói
                .withTreatment(DefaultTrafficTreatment.builder().punt().build()) // đẩy lên controller
                .withPriority(60000) // ưu tiên cao nhất
                .fromApp(appId)
                .makePermanent() // rule không hết hạn
                .build();

        flowRuleService.applyFlowRules(flowRule);
        log.info("Applied catch-all flow rule to device: {}", deviceId);
    }
}
