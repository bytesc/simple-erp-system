/*
 Navicat Premium Data Transfer

 Source Server         : erp
 Source Server Type    : SQLite
 Source Server Version : 3035005
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3035005
 File Encoding         : 65001

 Date: 13/10/2023 23:08:27
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for bom
-- ----------------------------
DROP TABLE IF EXISTS "bom";
CREATE TABLE "bom" (
  "序号" varchar NOT NULL,
  "资产类说明" varchar(255),
  "资产类方向" varchar,
  "资产类汇总序号" varchar,
  "变量名" varchar,
  PRIMARY KEY ("序号")
);

-- ----------------------------
-- Table structure for inventory
-- ----------------------------
DROP TABLE IF EXISTS "inventory";
CREATE TABLE "inventory" (
  "调配基准编号" varchar NOT NULL,
  "父物料名称" varchar,
  "子物料名称" varchar,
  "构成数" integer,
  "配料提前期" integer,
  "供应商提前期" integer,
  PRIMARY KEY ("调配基准编号"),
  FOREIGN KEY ("父物料名称") REFERENCES "supply" ("名称") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("子物料名称") REFERENCES "supply" ("名称") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ----------------------------
-- Table structure for store
-- ----------------------------
DROP TABLE IF EXISTS "store";
CREATE TABLE "store" (
  "物料名称" varchar NOT NULL,
  "工序库存" integer,
  "资材库存" integer,
  PRIMARY KEY ("物料名称"),
  FOREIGN KEY ("物料名称") REFERENCES "supply" ("名称") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ----------------------------
-- Table structure for supply
-- ----------------------------
DROP TABLE IF EXISTS "supply";
CREATE TABLE "supply" (
  "名称" varchar NOT NULL,
  "单位" varchar(255),
  "调配方式" varchar(255),
  "损耗率" float,
  "作业提前期" int,
  PRIMARY KEY ("名称")
);

PRAGMA foreign_keys = true;
