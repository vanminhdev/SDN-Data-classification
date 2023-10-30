package vn.edu.huce.dataclassification;

import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.PacketProcessor;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component(immediate = true, service = {PacketProcessor.class})
public class NatRoutingPacketProcessor implements PacketProcessor {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private InternetRoutingExampleInterface internetRouting;

    @Override
    public void process(PacketContext context) {
        if (internetRouting != null) {
            log.info("internetRouting is not null");
        }
        //internetRouting.addInternetRoute(context);
    }
}
