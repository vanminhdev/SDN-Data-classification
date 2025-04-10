package vn.edu.huce.dataclassification.utils;

/**
 * Enum định nghĩa các loại dịch vụ mạng và tham số mặc định
 */
public enum ServiceType {
    // Dịch vụ Web (HTTP, HTTPS)
    // Bộ tham số 1 (mặc định) - Cân bằng
    WEB(1000, 300, 50),
    
    // Dịch vụ Video (streaming video như YouTube, Netflix...)
    VIDEO(3000, 800, 80),
    
    // Dịch vụ VoIP (thoại qua IP, video call)
    VOIP(2000, 500, 100);
    
    /* 
    // Bộ tham số 2 - Tối ưu băng thông
    WEB(800, 250, 40),
    VIDEO(3500, 1000, 70),
    VOIP(1500, 400, 100);
    */
    
    /*
    // Bộ tham số 3 - Ưu tiên trải nghiệm người dùng
    WEB(1200, 400, 60),
    VIDEO(4000, 1200, 85),
    VOIP(2000, 600, 100);
    */
    
    /*
    // Bộ tham số 4 - Tiết kiệm tài nguyên mạng
    WEB(700, 200, 40),
    VIDEO(2500, 600, 75),
    VOIP(1800, 400, 100);
    */
    
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
