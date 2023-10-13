/*
 Navicat Premium Data Transfer

 Source Server         : erpdata
 Source Server Type    : SQLite
 Source Server Version : 3035005
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3035005
 File Encoding         : 65001

 Date: 12/10/2023 16:51:16
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for bom
-- ----------------------------
DROP TABLE IF EXISTS "bom";
CREATE TABLE "bom" (
  "序 号" varchar(255),
  "资产类说明" varchar(255),
  "资产类 方向" varchar(255),
  "资产类 汇总序 号" varchar(255),
  "变 名" varchar(255)
);

-- ----------------------------
-- Records of bom
-- ----------------------------
INSERT INTO "bom" VALUES ('1', '流动资产:', NULL, '', '');
INSERT INTO "bom" VALUES ('2', '货币资金', '+', '16', 'a1');
INSERT INTO "bom" VALUES ('3', '短期投资', '+', '16', ' a3');
INSERT INTO "bom" VALUES ('4', '应收票据_', '+', '16', 'a5');
INSERT INTO "bom" VALUES ('5', '应收账款', '+', '7', 'a7');
INSERT INTO "bom" VALUES ('6', '减,坏账准备', '+', '7', 'a9');
INSERT INTO "bom" VALUES ('7', '应收账款净额_', '+', '16', 'b1');
INSERT INTO "bom" VALUES ('8', '预付账款', '+', '16', 'a12');
INSERT INTO "bom" VALUES ('9', '_应收补贴款_', '+', '16', 'a14');
INSERT INTO "bom" VALUES ('10', '其他应收款', '+', '16', 'a16');
INSERT INTO "bom" VALUES ('11', '存货', '+', '16', 'a18');
INSERT INTO "bom" VALUES ('12', '_待摊费用', '+', '16', 'a20');
INSERT INTO "bom" VALUES ('13', '待处理流动资产净损失', '+', '16', 'a22');
INSERT INTO "bom" VALUES ('14', '一年内到期的长期债券投资', '+', '16', 'a24');
INSERT INTO "bom" VALUES ('15', '其他流动资产', '+', '16', 'a26');
INSERT INTO "bom" VALUES ('16', '流动资产合计', '+', '35', 'b3');

-- ----------------------------
-- Table structure for compose
-- ----------------------------
DROP TABLE IF EXISTS "compose";
CREATE TABLE "compose" (
  "父物料名称" varchar(255),
  "子物科名称" varchar(255),
  "调配方式" varchar(255),
  "构成数" int,
  "损耗率" int,
  "工序库存" int,
  "资材库存" int,
  "作业提前期" int,
  "配料提前期" int,
  "供应商提前期" int,
  "层数" int
);

-- ----------------------------
-- Records of compose
-- ----------------------------
INSERT INTO "compose" VALUES ('', '眼镜', '生产', 1, 0, 0, 0, 1, 0, 0, 0);
INSERT INTO "compose" VALUES ('眼镜', '镜框', '生产', 1, 0, 0, 10, 2, 0, 0, 1);
INSERT INTO "compose" VALUES ('镜框', '镜架', '采购', 1, 0, 0, 0, 0, 1, 20, 2);
INSERT INTO "compose" VALUES ('镜框', '镜雙', '采购', 2, 0, 10, 20, 0, 1, 10, 2);
INSERT INTO "compose" VALUES ('镜框', '鼻托', '采购', 2, 0, 0, 0, 0, 1, 18, 2);
INSERT INTO "compose" VALUES ('镜框', '螺钉', '采购', 4, 0, 10, 50, 0, 1, 10, 2);
INSERT INTO "compose" VALUES ('眼镜', '螺钉', '采购', 2, 0, 10, 50, 0, 1, 10, 1);
INSERT INTO "compose" VALUES ('眼镜', '镜片', '采购', 2, 0, 0, 0, 0, 1, 20, 1);

-- ----------------------------
-- Table structure for inventory
-- ----------------------------
DROP TABLE IF EXISTS "inventory";
CREATE TABLE "inventory" (
  "调配基 准编号" varchar(255),
  "调配区 代码" varchar(255),
  "父物料 号" varchar(255),
  "父物料 名称" varchar(255),
  "子物料 号" varchar(255),
  "子物料 名称" varchar(255),
  "构成数" varchar(255),
  "配料提 前期" varchar(255),
  "供应商 提前期" varchar(255)
);

-- ----------------------------
-- Records of inventory
-- ----------------------------
INSERT INTO "inventory" VALUES ('000001', 'L001', '20000', '眼镜', '20100', '镜框', '1', '0', '0');
INSERT INTO "inventory" VALUES ('000001', 'L001', '20000', '眼镜', '20300', '镜片', '2', '1', '20');
INSERT INTO "inventory" VALUES ('000001', 'L001', '20000', '眼镜', '20109', '螺钉', '2', '1', '10');
INSERT INTO "inventory" VALUES ('000001', 'L003', '20100', '镜框', '20110', '镜架', '1', '1', '20');
INSERT INTO "inventory" VALUES ('000001', 'L003', '20100', '镜框', '20120', '镜腿', '2', '1', '10');
INSERT INTO "inventory" VALUES ('000001', 'L003', '20100', '镜框', '20130', '鼻托', '2', '1', '18');
INSERT INTO "inventory" VALUES ('000001', 'L003', '20100', '镜框', '20109', '螺钉', '4', '1', '10');

-- ----------------------------
-- Table structure for supply
-- ----------------------------
DROP TABLE IF EXISTS "supply";
CREATE TABLE "supply" (
  "物料号" varchar(255),
  "名称" varchar(255),
  "单位" varchar(255),
  "调配方式" varchar(255),
  "损耗率" varchar(255),
  "作业提前期" varchar
);

-- ----------------------------
-- Records of supply
-- ----------------------------
INSERT INTO "supply" VALUES ('20000', '眼镜', '副', '生产', '0.00', '1');
INSERT INTO "supply" VALUES ('20109', '螺钉', '个', '采购', '0.10', '0');
INSERT INTO "supply" VALUES ('20100', '镜框', '副', '生产', '0.00', '2');
INSERT INTO "supply" VALUES ('20110', '镜架', '个', '采购', '0.00', '0');
INSERT INTO "supply" VALUES ('20120', '镜腿', '个', '采购', '0.00', '0');
INSERT INTO "supply" VALUES ('20130', '鼻托', '个', '采购', '0.00', '0');
INSERT INTO "supply" VALUES ('20300', '镜片', '片', '采购', '0.00', '0');

PRAGMA foreign_keys = true;
