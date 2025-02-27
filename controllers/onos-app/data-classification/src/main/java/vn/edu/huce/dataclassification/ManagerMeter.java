package vn.edu.huce.dataclassification;

import java.util.HashSet;
import java.util.Set;

import org.onosproject.app.ApplicationService;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.flow.FlowEntry;
import org.onosproject.net.flow.FlowRuleService;
import org.onosproject.net.meter.Band;
import org.onosproject.net.meter.DefaultBand;
import org.onosproject.net.meter.DefaultMeterRequest;
import org.onosproject.net.meter.Meter;
import org.onosproject.net.meter.MeterCellId;
import org.onosproject.net.meter.MeterRequest;
import org.onosproject.net.meter.MeterService;
import org.onosproject.net.meter.MeterStore;
import org.onosproject.net.statistic.FlowStatisticService;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import vn.edu.huce.dataclassification.dtos.meter.CreateMeterDto;
import vn.edu.huce.dataclassification.utils.AppInfo;

@Component(immediate = true, service = { ManagerMeter.class })
public class ManagerMeter {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private MeterStore meterStore;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private MeterService meterService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private ApplicationService appService;

    private ApplicationId appId;

    private FlowStatisticService statsService;

    @Activate
    public void activate() {
        log.info("ManagerMeter Started");
        appId = appService.getId(AppInfo.APP_NAME);
    }

    @Deactivate
    public void deactivate() {
        log.info("ManagerMeter Stopped");
    }

    /**
     * Thêm meter mới hoặc trả về meter ID nếu đã tồn tại meter với cùng tham số
     *
     * @param input Thông tin meter cần tạo
     * @return MeterCellId ID của meter (mới hoặc đã tồn tại)
     */
    public MeterCellId add(CreateMeterDto input) {
        log.info("Applying meter: {}", input);

        DeviceId deviceId = DeviceId.deviceId(input.getDeviceId());
        var meters = meterService.getMeters(deviceId);

        // Kiểm tra xem đã tồn tại meter với cùng tham số chưa
        for (Meter meter : meters) {
            // Kiểm tra từng band trong meter
            for (Band band : meter.bands()) {
                // So sánh thông số với input
                if (band.type() == Band.Type.DROP && 
                    band.rate() == input.getRate() && 
                    band.burst() == input.getBurstSize()) {
                    
                    log.info("Meter với cùng rate={}, burstSize={}, type={} đã tồn tại. Sử dụng meter ID: {}", 
                             input.getRate(), input.getBurstSize(), Band.Type.DROP, meter.id());
                    
                    // Trả về ID của meter đã tồn tại
                    return meter.meterCellId();
                }
            }
        }

        // Nếu không tìm thấy meter trùng lặp, tạo mới
        Set<Band> bandSet = new HashSet<>();

        var bandBuilder = DefaultBand.builder()
                .ofType(Band.Type.DROP)
                .withRate(input.getRate())
                .burstSize(input.getBurstSize())
                .dropPrecedence((short) 0); // không drop packet

        bandSet.add(bandBuilder.build());

        MeterRequest.Builder meterRequest = DefaultMeterRequest.builder()
                .forDevice(deviceId)
                .fromApp(appId)
                .withUnit(Meter.Unit.KB_PER_SEC)
                .withBands(bandSet);

        var meterSubmit = meterService.submit(meterRequest.add());
        var meterId = meterSubmit.meterCellId();
        log.info("Đã tạo meter mới với ID: {}", meterId);
        
        return meterId;
    }
}
