package vn.edu.huce.dataclassification.rest;

import org.slf4j.Logger;

import org.onosproject.core.CoreService;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;

import static org.slf4j.LoggerFactory.getLogger;

// @Component(immediate = true, service = MyApiManager.class)
// public class MyApiManager {
//     private final Logger log = getLogger(getClass());

//     @Reference(cardinality = ReferenceCardinality.MANDATORY)
//     protected CoreService coreService;

//     public static final String PROVIDER_NAME = "vn.edu.huce.dataclassification.rest";

//     @Activate
//     public void activate() {
//         coreService.registerApplication(PROVIDER_NAME);
//         log.info("Started");
//     }

//     @Deactivate
//     public void deactivate() {
//         log.info("Stopped");
//     }
// }
