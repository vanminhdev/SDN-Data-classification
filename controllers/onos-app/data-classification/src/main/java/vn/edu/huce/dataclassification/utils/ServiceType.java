package vn.edu.huce.dataclassification.utils;

/**
 * Enum định nghĩa các loại dịch vụ mạng và tham số mặc định
 */
public enum ServiceType {
    // Dịch vụ Web (HTTP, HTTPS)
    WEB(1000, 300, 50),
    
    // Dịch vụ Video (streaming video như YouTube, Netflix...)
    VIDEO(3000, 800, 80),
    
    // Dịch vụ VoIP (thoại qua IP, video call)
    VOIP(2000, 500, 100);
    
    private final int defaultRate;    // Tốc độ mặc định (KB/s)
    private final int defaultBurst;   // Burst size mặc định (KB)
    private final int defaultPriority; // Mức độ ưu tiên mặc định

    ServiceType(int defaultRate, int defaultBurst, int defaultPriority) {
        this.defaultRate = defaultRate;
        this.defaultBurst = defaultBurst;
        this.defaultPriority = defaultPriority;
    }
    
    public int getDefaultRate() {
        return defaultRate;
    }
    
    public int getDefaultBurst() {
        return defaultBurst;
    }
    
    public int getDefaultPriority() {
        return defaultPriority;
    }
}
