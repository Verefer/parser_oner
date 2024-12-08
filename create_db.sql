CREATE DATABASE ParserOlxDB;
USE ParserOlxDB;
CREATE TABLE `balances`
(
    `ID`       BIGINT UNIQUE,
    `balance`  INT         DEFAULT 0,
    `promo`    VARCHAR(15) DEFAULT '',
    `discount` INT         DEFAULT 0
);

CREATE TABLE `usersOlxUa`
(
    `ID`                           BIGINT UNIQUE,
    `status_parsing`               INT          DEFAULT 0, /* 0 - не парсится, 1 - парсится */
    `subscription_to`              DATETIME     DEFAULT CURRENT_TIMESTAMP(), /* время, до которого действительна подписка */
    `registration_announce`        INT          DEFAULT 10000, /* максимальное количество дней со дня регистрации продаца */
    `announce_price`               VARCHAR(30)  DEFAULT '0-1000000',
    `filter_successful_deliveries` INT          DEFAULT 100,
    `interval_create_announce`     INT          DEFAULT 300,
    `auto_text_wa`                 VARCHAR(500) DEFAULT '!',
    `referer_id`                   BIGINT       DEFAULT 0,
    `parse_category`               VARCHAR(500) DEFAULT ''
);

CREATE TABLE `announcementsOlxUa`
(
    `id`                   INT AUTO_INCREMENT PRIMARY KEY,
    `title`                VARCHAR(150),
    `price_value`          INT,
    `price_currency`       VARCHAR(20),
    `description`          VARCHAR(150),
    `city`                 VARCHAR(50),
    `region`               VARCHAR(70),
    `date_create_announce` DATETIME,
    `date_create_account`  DATETIME,
    `photo_url`            VARCHAR(150),
    `page_id`              VARCHAR(20),
    `amount_delivery`      INT,
    `contact_name`         VARCHAR(50),
    `category`             INT,
    `url`                  VARCHAR(200),
    `phone`                VARCHAR(100) DEFAULT '',
    `views`                INT          DEFAULT 0
);
create index announcementsolxua_category_index
    on announcementsolxua (category);

create index announcementsolxua_amount_delivery_index
    on announcementsolxua (amount_delivery);

CREATE TABLE `timeoutProxiesOlxUa`
(
    `proxyID`       INT AUTO_INCREMENT PRIMARY KEY,
    `proxy`         VARCHAR(100),
    `start_timeout` DATETIME DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE `tokensOlxUa`
(
    `TokenId` INT PRIMARY KEY AUTO_INCREMENT,
    `ID`      BIGINT, /* юзер айди человека, имеющего этот токен */
    `token`   VARCHAR(100) UNIQUE
);

CREATE TABLE `proxyOlxUa`
(
    `id`    INT PRIMARY KEY AUTO_INCREMENT,
    `proxy` VARCHAR(100)
);

CREATE TABLE `promoCodes`
(
    `promo`    VARCHAR(15),
    `discount` INT
);

CREATE TABLE `lastParseConsignmentOlxUa`
(
    `ID`       BIGINT UNIQUE, /* ID человека, запустившего парсинг */
    `filename` VARCHAR(100)
);