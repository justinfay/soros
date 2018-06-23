DROP TABLE IF EXISTS bar;
CREATE TABLE bar(
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    start TIMESTAMP NOT NULL,
    resolution INTERVAL MINUTE NOT NULL,
    open DECIMAL(12, 8) NOT NULL,
    high DECIMAL(12, 8) NOT NULL,
    low DECIMAL(12, 8) NOT NULL,
    close DECIMAL(12, 8) NOT NULL,
    PRIMARY KEY (exchange, symbol, start, resolution)
);
