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
    public static long getEpochNano() {
        Instant now = Instant.now();
        long epochSeconds = now.getEpochSecond();
        int nanoAdjustment = now.getNano();

        // Chuyển đổi giây và nano giây thành tổng số nano giây từ Epoch
        return epochSeconds * 1_000_000_000L + nanoAdjustment;
    }
}
