CREATE DATABASE IF NOT EXISTS app
    CHARACTER SET utf8
    DEFAULT CHARACTER SET utf8
    COLLATE utf8_general_ci
    DEFAULT COLLATE utf8_general_ci
    ;
USE app;

CREATE TABLE CurrentPrices(
    pid         VARCHAR(255),
    cid         VARCHAR(255),
    bid         INT,
    price       DECIMAL(8,2),
    PRIMARY KEY (pid, cid, bid)
);

CREATE TABLE PriceHistory(
    pid         VARCHAR(255),
    cid         VARCHAR(255),
    bid         INT,
    update_date DATE,
    price       DECIMAL(8,2),
    PRIMARY KEY (pid, cid, bid, update_date)
);

CREATE TABLE Products(
    pid         VARCHAR(255),
    cid         VARCHAR(255),
    bid         INT,
    pname       VARCHAR(255),
    manufacturer VARCHAR(255),
    PRIMARY KEY (pid, cid, bid)
);

CREATE TABLE Branches(
    bid         INT,
    cid         VARCHAR(255),
    bname       VARCHAR(255),
    PRIMARY KEY (bid, cid)
);

CREATE TABLE Chains(
    cid         VARCHAR(255),
    cname       VARCHAR(255),
    PRIMARY KEY (cid)
);