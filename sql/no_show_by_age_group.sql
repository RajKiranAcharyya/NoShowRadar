SELECT age_group AS appointment_group, COUNT(*) AS total_appointments, ROUND(100.0 * AVG(no_show), 1) AS no_show_rate_pct FROM appointments GROUP BY age_group ORDER BY CASE age_group WHEN '0-12' THEN 1 WHEN '13-18' THEN 2 WHEN '19-35' THEN 3 WHEN '36-50' THEN 4 WHEN '51-65' THEN 5 WHEN '66+' THEN 6 ELSE 7 END;

