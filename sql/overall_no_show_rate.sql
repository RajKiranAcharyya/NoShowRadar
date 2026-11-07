SELECT 'Overall' AS appointment_group, COUNT(*) AS total_appointments, ROUND(100.0 * AVG(no_show), 1) AS no_show_rate_pct FROM appointments;
