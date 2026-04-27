-- SQL Setup para el Proyecto COVID-19 España
-- Este archivo documenta la estructura inicial de la base de datos
-- 1. Creación de la base de datos (Ejecutar manualmente en MySQL)
CREATE DATABASE IF NOT EXISTS covid_spain;
USE covid_spain;
-- Nota: Las tablas 'master_data' y 'daily_stats' se generan y pueblan 
-- automáticamente mediante el Notebook '04_db_loading.ipynb' utilizando 
-- SQLAlchemy y Pandas (to_sql).
-- 2. Estructura esperada de las tablas:
-- master_data: Contiene la unificación de las 3 fuentes (Casos, Hospitales, Vacunas).
-- daily_stats: Resumen diario procesado para consumo del Dashboard en Streamlit.
-- 3. Verificación rápida de carga
-- SELECT COUNT(*) FROM master_data;
-- SELECT * FROM daily_stats LIMIT 10;