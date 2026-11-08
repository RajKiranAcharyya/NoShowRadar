SELECT CASE weekday WHEN 0 THEN 'Monday' WHEN 1 THEN 'Tuesday' WHEN 2 THEN 'Wednesday' WHEN 3 THEN 'Thursday' WHEN 4 THEN 'Friday' WHEN 5 THEN 'Saturday' WHEN 6 THEN 'Sunday' ELSE 'Unknown' END AS appointment_group, COUNT(*) AS total_appointments, ROUND(100.0 * AVG(no_show), 1) AS no_show_rate_pct FROM appointments GROUP BY weekday ORDER BY weekday;

