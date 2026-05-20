-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: equipmentdb
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `user` varchar(50) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `due_date` datetime DEFAULT NULL COMMENT '반납 예정일',
  `repair_estimate` datetime DEFAULT NULL COMMENT '수리 완료 예정일',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment`
--

LOCK TABLES `equipment` WRITE;
/*!40000 ALTER TABLE `equipment` DISABLE KEYS */;
INSERT INTO `equipment` VALUES (1,'웨이퍼 세정기','세정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(2,'스핀 코터','코팅장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(3,'포토레지스트 도포기','포토장비','대여중','김도겸','2025-12-09 13:47:22','2025-12-15 13:47:22',NULL),(4,'마스크 얼라이너','노광장비','고장','-','2025-12-09 13:47:39',NULL,'2025-12-12 13:47:39'),(5,'스테퍼(노광기)','노광장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(6,'현상기','포토장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(7,'식각기 (Dry Etcher)','식각장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(8,'RIE 식각기','식각장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(9,'ICP 식각기','식각장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(10,'습식 식각기 (Wet Etcher)','식각장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(11,'증착기 (PVD)','증착장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(12,'스퍼터링 장비','증착장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(13,'증착기 (CVD)','증착장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(14,'ALD 증착기','증착장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(15,'이온 주입기 (Ion Implanter)','공정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(16,'열처리 장비 (Furnace)','열처리','정상','-','2025-11-20 15:38:24',NULL,NULL),(17,'RTP 장비','열처리','정상','-','2025-11-20 15:38:24',NULL,NULL),(18,'CMP 장비','연마장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(19,'플라즈마 클리너','세정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(20,'산화장비 (Oxidation Furnace)','산화장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(21,'확산장비 (Diffusion Furnace)','확산장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(22,'메탈 패터닝 장비','포토장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(23,'웨이퍼 검사기 (Inspection)','검사장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(24,'CD-SEM','검사장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(25,'광학 현미경(OM)','검사장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(26,'프로파일러(Profilometer)','측정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(27,'AFM','측정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(28,'엘립소미터','측정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(29,'전기적 특성 분석기 (Parametric Analyzer)','측정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(30,'프로버 스테이션','측정장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(31,'스크러버 (Scrubber)','환경장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(32,'배기 시스템','환경장비','정상','-','2025-11-20 15:38:24',NULL,NULL),(33,'냉각수 순환장치 (Chiller)','유틸리티','정상','-','2025-11-20 15:38:24',NULL,NULL),(34,'진공 펌프','유틸리티','정상','-','2025-11-20 15:38:24',NULL,NULL),(35,'터보 펌프','유틸리티','정상','-','2025-11-20 15:38:24',NULL,NULL),(36,'로더/언로더 시스템','자동화','정상','-','2025-11-20 15:38:24',NULL,NULL),(37,'EFEM 모듈','자동화','정상','-','2025-11-20 15:38:24',NULL,NULL),(38,'AMHS OHT','자동화','정상','-','2025-11-20 15:38:24',NULL,NULL),(39,'FOUP 오프너','자동화','정상','-','2025-11-20 15:38:24',NULL,NULL),(40,'테스트 노트북','노트북','정상','-','2025-12-09 13:44:00',NULL,NULL);
/*!40000 ALTER TABLE `equipment` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11 12:46:49
