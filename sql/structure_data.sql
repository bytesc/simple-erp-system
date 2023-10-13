/*
 Navicat Premium Data Transfer

 Source Server         : erp
 Source Server Type    : SQLite
 Source Server Version : 3035005
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3035005
 File Encoding         : 65001

 Date: 13/10/2023 23:08:07
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
-- Records of bom
-- ----------------------------
INSERT INTO "bom" VALUES ('1', '流动资产', NULL, '', '');
INSERT INTO "bom" VALUES ('2', '货币资金', '+', '16', 'a1');
INSERT INTO "bom" VALUES ('3', '短期投资', '+', '16', ' a3');
INSERT INTO "bom" VALUES ('4', '应收票据', '+', '16', 'a5');
INSERT INTO "bom" VALUES ('5', '应收账款', '+', '7', 'a7');
INSERT INTO "bom" VALUES ('6', '减,坏账准备', '+', '7', 'a9');
INSERT INTO "bom" VALUES ('7', '应收账款净额', '+', '16', 'b1');
INSERT INTO "bom" VALUES ('8', '预付账款', '+', '16', 'a12');
INSERT INTO "bom" VALUES ('9', '应收补贴款', '+', '16', 'a14');
INSERT INTO "bom" VALUES ('10', '其他应收款', '+', '16', 'a16');
INSERT INTO "bom" VALUES ('11', '存货', '+', '16', 'a18');
INSERT INTO "bom" VALUES ('12', '待摊费用', '+', '16', 'a20');
INSERT INTO "bom" VALUES ('13', '待处理流动资产净损失', '+', '16', 'a22');
INSERT INTO "bom" VALUES ('14', '一年内到期的长期债券投资', '+', '16', 'a24');
INSERT INTO "bom" VALUES ('15', '其他流动资产', '+', '16', 'a26');
INSERT INTO "bom" VALUES ('16', '流动资产合计', '+', '35', 'b3');

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
-- Records of inventory
-- ----------------------------
INSERT INTO "inventory" VALUES ('000001', '眼镜', '镜框', 1, 0, 0);
INSERT INTO "inventory" VALUES ('000002', '眼镜', '镜片', 2, 1, 20);
INSERT INTO "inventory" VALUES ('000003', '眼镜', '螺钉', 2, 1, 10);
INSERT INTO "inventory" VALUES ('000004', '镜框', '镜架', 1, 1, 20);
INSERT INTO "inventory" VALUES ('000005', '镜框', '镜腿', 2, 1, 10);
INSERT INTO "inventory" VALUES ('000006', '镜框', '鼻托', 2, 1, 18);
INSERT INTO "inventory" VALUES ('000007', '镜框', '螺钉', 4, 1, 10);
INSERT INTO "inventory" VALUES ('000008', NULL, '眼镜', 1, 0, 0);

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
-- Records of store
-- ----------------------------
INSERT INTO "store" VALUES ('眼镜', 0, 0);
INSERT INTO "store" VALUES ('螺钉', 10, 50);
INSERT INTO "store" VALUES ('镜框', 0, 0);
INSERT INTO "store" VALUES ('镜架', 0, 0);
INSERT INTO "store" VALUES ('镜腿', 10, 20);
INSERT INTO "store" VALUES ('鼻托', 0, 0);
INSERT INTO "store" VALUES ('镜片', 0, 0);

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

-- ----------------------------
-- Records of supply
-- ----------------------------
INSERT INTO "supply" VALUES ('眼镜', '副', '生产', 0.0, 1);
INSERT INTO "supply" VALUES ('螺钉', '个', '采购', 0.1, 0);
INSERT INTO "supply" VALUES ('镜框', '副', '生产', 0.0, 2);
INSERT INTO "supply" VALUES ('镜架', '个', '采购', 0.0, 0);
INSERT INTO "supply" VALUES ('镜腿', '个', '采购', 0.0, 0);
INSERT INTO "supply" VALUES ('鼻托', '个', '采购', 0.0, 0);
INSERT INTO "supply" VALUES ('镜片', '片', '采购', 0.0, 0);

PRAGMA foreign_keys = true;
