-- Portal del Colaborador · Cinépolis Sendero Tijuana
-- Estructura de la base de datos (MariaDB/MySQL)
DROP DATABASE IF EXISTS portal_colaborador;
CREATE DATABASE portal_colaborador CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE portal_colaborador;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_amonestacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `motivo` varchar(150) NOT NULL,
  `descripcion` longtext NOT NULL,
  `registrada_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_amonestacion_registrada_por_id_ecdfbc2c_fk_auth_user_id` (`registrada_por_id`),
  KEY `portal_amonestacion_colaborador_id_093d34a4_fk_portal_perfil_id` (`colaborador_id`),
  CONSTRAINT `portal_amonestacion_colaborador_id_093d34a4_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`),
  CONSTRAINT `portal_amonestacion_registrada_por_id_ecdfbc2c_fk_auth_user_id` FOREIGN KEY (`registrada_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_area` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_asistencia` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora_entrada` time(6) NOT NULL,
  `hora_salida` time(6) DEFAULT NULL,
  `estado` varchar(10) NOT NULL,
  `observaciones` varchar(200) NOT NULL,
  `registrada_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asistencia_unica_por_dia` (`colaborador_id`,`fecha`),
  KEY `portal_asistencia_registrada_por_id_711a74b4_fk_auth_user_id` (`registrada_por_id`),
  CONSTRAINT `portal_asistencia_colaborador_id_67463a40_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`),
  CONSTRAINT `portal_asistencia_registrada_por_id_711a74b4_fk_auth_user_id` FOREIGN KEY (`registrada_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_bitacora` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `accion` varchar(20) NOT NULL,
  `modulo` varchar(30) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `fecha_hora` datetime(6) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_bitacora_usuario_id_d7a25fe1_fk_auth_user_id` (`usuario_id`),
  CONSTRAINT `portal_bitacora_usuario_id_d7a25fe1_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_calificacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `estrellas` smallint(5) unsigned NOT NULL CHECK (`estrellas` >= 0),
  `comentario` varchar(200) NOT NULL,
  `fecha` date NOT NULL,
  `calificada_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_calificacion_calificada_por_id_f3f0647f_fk_auth_user_id` (`calificada_por_id`),
  KEY `portal_calificacion_colaborador_id_a5f1cb00_fk_portal_perfil_id` (`colaborador_id`),
  CONSTRAINT `portal_calificacion_calificada_por_id_f3f0647f_fk_auth_user_id` FOREIGN KEY (`calificada_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `portal_calificacion_colaborador_id_a5f1cb00_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_evento` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  `fecha` date NOT NULL,
  `hora` time(6) DEFAULT NULL,
  `lugar` varchar(100) NOT NULL,
  `area_id` bigint(20) DEFAULT NULL,
  `creado_por_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_evento_area_id_e78a8b02_fk_portal_area_id` (`area_id`),
  KEY `portal_evento_creado_por_id_f1693d21_fk_auth_user_id` (`creado_por_id`),
  CONSTRAINT `portal_evento_area_id_e78a8b02_fk_portal_area_id` FOREIGN KEY (`area_id`) REFERENCES `portal_area` (`id`),
  CONSTRAINT `portal_evento_creado_por_id_f1693d21_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_falta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `motivo` varchar(200) NOT NULL,
  `justificada` tinyint(1) NOT NULL,
  `registrada_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_falta_registrada_por_id_496bd817_fk_auth_user_id` (`registrada_por_id`),
  KEY `portal_falta_colaborador_id_29c6275a_fk_portal_perfil_id` (`colaborador_id`),
  CONSTRAINT `portal_falta_colaborador_id_29c6275a_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`),
  CONSTRAINT `portal_falta_registrada_por_id_496bd817_fk_auth_user_id` FOREIGN KEY (`registrada_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_horario` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `hora_entrada` time(6) DEFAULT NULL,
  `hora_salida` time(6) DEFAULT NULL,
  `area_id` bigint(20) NOT NULL,
  `asignado_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `horario_unico_por_dia` (`colaborador_id`,`fecha`),
  KEY `portal_horario_area_id_8c195f18_fk_portal_area_id` (`area_id`),
  KEY `portal_horario_asignado_por_id_29493248_fk_auth_user_id` (`asignado_por_id`),
  CONSTRAINT `portal_horario_area_id_8c195f18_fk_portal_area_id` FOREIGN KEY (`area_id`) REFERENCES `portal_area` (`id`),
  CONSTRAINT `portal_horario_asignado_por_id_29493248_fk_auth_user_id` FOREIGN KEY (`asignado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `portal_horario_colaborador_id_d48bad32_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_incidencia` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `descripcion` longtext NOT NULL,
  `estado` varchar(12) NOT NULL,
  `registrada_por_id` int(11) DEFAULT NULL,
  `colaborador_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `portal_incidencia_registrada_por_id_58783415_fk_auth_user_id` (`registrada_por_id`),
  KEY `portal_incidencia_colaborador_id_1e64ed05_fk_portal_perfil_id` (`colaborador_id`),
  CONSTRAINT `portal_incidencia_colaborador_id_1e64ed05_fk_portal_perfil_id` FOREIGN KEY (`colaborador_id`) REFERENCES `portal_perfil` (`id`),
  CONSTRAINT `portal_incidencia_registrada_por_id_58783415_fk_auth_user_id` FOREIGN KEY (`registrada_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_perfil` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rol` varchar(12) NOT NULL,
  `numero_colaborador` varchar(10) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  `puesto` varchar(60) NOT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_colaborador` (`numero_colaborador`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `portal_perfil_usuario_id_51102028_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_perfil_areas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `perfil_id` bigint(20) NOT NULL,
  `area_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `portal_perfil_areas_perfil_id_area_id_bb6df4aa_uniq` (`perfil_id`,`area_id`),
  KEY `portal_perfil_areas_area_id_3c8fc588_fk_portal_area_id` (`area_id`),
  CONSTRAINT `portal_perfil_areas_area_id_3c8fc588_fk_portal_area_id` FOREIGN KEY (`area_id`) REFERENCES `portal_area` (`id`),
  CONSTRAINT `portal_perfil_areas_perfil_id_2cfba5ed_fk_portal_perfil_id` FOREIGN KEY (`perfil_id`) REFERENCES `portal_perfil` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

