package vn.edu.huce.dataclassification.utils;

import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class DateTimeUtil {

    public static String getCurrDateTime() {
        Instant now = Instant.now();

        // Chuyển đổi sang định dạng có thể đọc được
        ZonedDateTime utcTime = now.atZone(ZoneOffset.UTC);

        return utcTime.format(DateTimeFormatter.ISO_INSTANT);
    }

    /**
    * Lấy thời gian ở định dạng Unix Epoch chính xác đến nano giây
    */
    public static double getEpochSecond() {
        Instant now = Instant.now();
        long epochSeconds = now.getEpochSecond();
        int nanoAdjustment = now.getNano();

        // Kết hợp thành giá trị thập phân
        return (double) epochSeconds + (nanoAdjustment / 1_000_000_000.0);
    }
}
