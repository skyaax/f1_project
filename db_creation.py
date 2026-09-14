import sqlite3
cursor = sqlite3.connect("f1_data.db")

cursor.executescript("""
        DROP TABLE IF EXISTS race_results;
        DROP TABLE IF EXISTS qualifying_results;
        DROP TABLE IF EXISTS races;
        DROP TABLE IF EXISTS circuits;
        DROP TABLE IF EXISTS constructors;
        DROP TABLE IF EXISTS drivers;

        CREATE TABLE drivers (
            driver_id VARCHAR(20) PRIMARY KEY,
            driver_number INT,
            full_name VARCHAR(100),
            abbreviation VARCHAR(3),
            nationality VARCHAR(50)
        );

        CREATE TABLE constructors (
            constructor_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );

        CREATE TABLE circuits (
            circuit_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            country VARCHAR(50),
            city VARCHAR(100)
        );

        CREATE TABLE races (
            race_id INT PRIMARY KEY,
            season INT NOT NULL,
            round INT NOT NULL,
            race_name VARCHAR(100),
            circuit_id VARCHAR(50) REFERENCES circuits(circuit_id),
            race_date DATE,
            UNIQUE(season, round)
        );

        CREATE TABLE qualifying_results (
            race_id INT REFERENCES races(race_id),
            driver_id VARCHAR(20) REFERENCES drivers(driver_id),
            constructor_id VARCHAR(50) REFERENCES constructors(constructor_id),
            position INT,
            q1 TEXT,
            q2 TEXT,
            q3 TEXT,
            PRIMARY KEY (race_id, driver_id)
        );

        CREATE TABLE race_results (
            race_id INT REFERENCES races(race_id),
            driver_id VARCHAR(20) REFERENCES drivers(driver_id),
            constructor_id VARCHAR(50) REFERENCES constructors(constructor_id),
            grid_position INT,
            finish_position INT,
            points DOUBLE PRECISION,
            laps INT,
            status VARCHAR(50),
            fastest_lap_time DOUBLE PRECISION,
            PRIMARY KEY (race_id, driver_id)
        );
        """)