package vn.edu.huce.dataclassification.dtos.data;

import java.util.Date;

/**
 * Dữ liệu thu thập
 */
public class DataFlowDto {
    private String srcIp;
    private String destIp;
    private int srcPort;
    private int destPort;
    private String dateTime;
    public int packageLength;

}
