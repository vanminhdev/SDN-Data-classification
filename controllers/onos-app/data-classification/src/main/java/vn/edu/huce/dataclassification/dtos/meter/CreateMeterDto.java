package vn.edu.huce.dataclassification.dtos.meter;

public class CreateMeterDto {
    private String deviceId;
    private int rate;
    private int burstSize;
    private int prec;

    public CreateMeterDto(String deviceId, int rate, int burstSize, int prec) {
        this.deviceId = deviceId;
        this.rate = rate;
        this.burstSize = burstSize;
        this.prec = prec;
    }

    @Override
    public String toString() {
        return "CreateMeterDto [deviceId=" + deviceId + ", rate=" + rate + ", burstSize=" + burstSize + ", prec=" + prec
                + "]";
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public int getRate() {
        return rate;
    }

    public void setRate(int rate) {
        this.rate = rate;
    }

    public int getBurstSize() {
        return burstSize;
    }

    public void setBurstSize(int burstSize) {
        this.burstSize = burstSize;
    }

    public int getPrec() {
        return prec;
    }

    public void setPrec(int prec) {
        this.prec = prec;
    }

}
