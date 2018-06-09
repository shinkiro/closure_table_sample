/* 初期化 */
DROP DATABASE IF EXISTS `analyze_tree`;
CREATE DATABASE IF NOT EXISTS `analyze_tree`;
USE `analyze_tree`

CREATE TABLE IF NOT EXISTS `node`
(
    `id` INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `label` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `order_item_node`
(
    `order_item_id` INT,
    `node_id` INT
);

CREATE TABLE IF NOT EXISTS `reference`
(
    `id` INT,
    `parent_id` INT,
    `is_direct` TINYINT(1) 
);

INSERT INTO `node` (`id`, `label`) VALUES
(1, 'root'),
(2, '国内航空券'),
(3, '国外航空券'),
(4, 'ANA'),
(5, 'JAL'),
(6, 'ANA'),
(7, 'JAL');

INSERT INTO `reference` (`id`, `parent_id`, `is_direct`) VALUES
(2, '1', 1),
(4, '1', 0),
(5, '1', 0),
(4, '2', 1),
(5, '2', 1),
(3, '1', 1),
(6, '1', 0),
(7, '1', 0),
(6, '3', 1),
(7, '3', 1);
