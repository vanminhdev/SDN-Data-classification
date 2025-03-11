package vn.edu.huce.dataclassification.utils;

/**
 * Lớp cấu hình QoS cho dịch vụ, cho phép điều chỉnh linh hoạt
 */
public class ServiceConfig {
    private ServiceType serviceType;
    private long rate;
    private long burstSize;
    private int priority;
    private boolean useCustomParams = false;
    
    // Constructor với tham số mặc định từ ServiceType
    public ServiceConfig(ServiceType serviceType) {
        this.serviceType = serviceType;
        this.rate = serviceType.getDefaultRate();
        this.burstSize = serviceType.getDefaultBurst();
        this.priority = serviceType.getDefaultPriority();
    }
    
    // Constructor với tham số tùy chỉnh
    public ServiceConfig(ServiceType serviceType, long rate, long burstSize, int priority) {
        this.serviceType = serviceType;
        this.rate = rate;
        this.burstSize = burstSize;
        this.priority = priority;
        this.useCustomParams = true;
    }
    
    // Getters và Setters
    public ServiceType getServiceType() {
        return serviceType;
    }
    
    public long getRate() {
        return rate;
    }
    
    public void setRate(long rate) {
        this.rate = rate;
        this.useCustomParams = true;
    }
    
    public long getBurstSize() {
        return burstSize;
    }
    
    public void setBurstSize(long burstSize) {
        this.burstSize = burstSize;
        this.useCustomParams = true;
    }
    
    public int getPriority() {
        return priority;
    }
    
    public void setPriority(int priority) {
        this.priority = priority;
        this.useCustomParams = true;
    }
    
    public boolean isUsingCustomParams() {
        return useCustomParams;
    }
    
    // Phương thức để điều chỉnh tham số dựa trên tình trạng mạng
    public void adjustForNetworkStatus(double congestionLevel, double availableBandwidth) {
        if (congestionLevel > 0.8) {
            // Mạng đang tắc nghẽn, giảm thông số
            this.rate = (long) (this.rate * 0.8);
            this.burstSize = (long) (this.burstSize * 0.8);
        } else if (availableBandwidth > 0.7) {
            // Mạng đang rảnh, tăng thông số
            this.rate = (long) (this.rate * 1.2);
            this.burstSize = (long) (this.burstSize * 1.2);
        }
        this.useCustomParams = true;
    }
    
    // Reset về tham số mặc định
    public void resetToDefault() {
        this.rate = serviceType.getDefaultRate();
        this.burstSize = serviceType.getDefaultBurst();
        this.priority = serviceType.getDefaultPriority();
        this.useCustomParams = false;
    }
}
