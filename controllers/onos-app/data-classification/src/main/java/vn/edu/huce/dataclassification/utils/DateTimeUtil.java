package vn.edu.huce.dataclassification.utils;

import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class DateTimeUtil {

    public static String GetCurrDateTime() {
        Instant now = Instant.now();

        // Chuyển đổi sang định dạng có thể đọc được
        ZonedDateTime utcTime = now.atZone(ZoneOffset.UTC);
        String formattedTime = utcTime.format(DateTimeFormatter.ISO_INSTANT);

        return  formattedTime;
    }
}
