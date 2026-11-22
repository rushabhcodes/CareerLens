-- CareerLens schema exported from the verified MySQL database. No user data.

CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE careerlens;

SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_analysishistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `kind` varchar(30) NOT NULL,
  `title` varchar(240) NOT NULL,
  `score` double DEFAULT NULL,
  `detail` json NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  `resume_id` bigint DEFAULT NULL,
  `match_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_analysishistory_user_id_7b6251b8_fk_core_user_id` (`user_id`),
  KEY `core_analysishistory_resume_id_e0ae404b_fk_core_resume_id` (`resume_id`),
  KEY `core_analysishistory_created_at_b0157053` (`created_at`),
  KEY `core_analysishistory_match_id_34b6e32b_fk_core_jobm` (`match_id`),
  CONSTRAINT `core_analysishistory_match_id_34b6e32b_fk_core_jobm` FOREIGN KEY (`match_id`) REFERENCES `core_jobmatchanalysis` (`id`),
  CONSTRAINT `core_analysishistory_resume_id_e0ae404b_fk_core_resume_id` FOREIGN KEY (`resume_id`) REFERENCES `core_resume` (`id`),
  CONSTRAINT `core_analysishistory_user_id_7b6251b8_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_careerrecommendation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `score` double NOT NULL,
  `result` json NOT NULL,
  `engine` varchar(40) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `role_id` bigint NOT NULL,
  `resume_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_careerrecommendation_role_id_e3e160e2_fk_core_careerrole_id` (`role_id`),
  KEY `core_careerrecommendation_resume_id_57092e25_fk_core_resume_id` (`resume_id`),
  CONSTRAINT `core_careerrecommendation_resume_id_57092e25_fk_core_resume_id` FOREIGN KEY (`resume_id`) REFERENCES `core_resume` (`id`),
  CONSTRAINT `core_careerrecommendation_role_id_e3e160e2_fk_core_careerrole_id` FOREIGN KEY (`role_id`) REFERENCES `core_careerrole` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_careerrole` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `description` longtext NOT NULL,
  `category_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  KEY `core_careerrole_category_id_b1548c5e_fk_core_jobcategory_id` (`category_id`),
  CONSTRAINT `core_careerrole_category_id_b1548c5e_fk_core_jobcategory_id` FOREIGN KEY (`category_id`) REFERENCES `core_jobcategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_careerrole_skills` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `careerrole_id` bigint NOT NULL,
  `skill_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_careerrole_skills_careerrole_id_skill_id_be9a4b6b_uniq` (`careerrole_id`,`skill_id`),
  KEY `core_careerrole_skills_skill_id_43436dd7_fk_core_skill_id` (`skill_id`),
  CONSTRAINT `core_careerrole_skil_careerrole_id_708e078c_fk_core_care` FOREIGN KEY (`careerrole_id`) REFERENCES `core_careerrole` (`id`),
  CONSTRAINT `core_careerrole_skills_skill_id_43436dd7_fk_core_skill_id` FOREIGN KEY (`skill_id`) REFERENCES `core_skill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_extractedinformation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `text` longtext NOT NULL,
  `candidate_name` varchar(160) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(60) NOT NULL,
  `sections` json NOT NULL,
  `experience_years` double DEFAULT NULL,
  `warnings` json NOT NULL,
  `resume_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resume_id` (`resume_id`),
  CONSTRAINT `core_extractedinformation_resume_id_e5c05f0c_fk_core_resume_id` FOREIGN KEY (`resume_id`) REFERENCES `core_resume` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_jobcategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_jobdescription` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(160) NOT NULL,
  `company` varchar(160) NOT NULL,
  `description` longtext NOT NULL,
  `experience_years` double DEFAULT NULL,
  `qualification` varchar(240) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_jobdescription_user_id_0dd16d44_fk_core_user_id` (`user_id`),
  CONSTRAINT `core_jobdescription_user_id_0dd16d44_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_jobmatchanalysis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `score` double NOT NULL,
  `result` json NOT NULL,
  `engine` varchar(40) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `job_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `resume_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_jobmatchanalysis_job_id_ab18e03b_fk_core_jobdescription_id` (`job_id`),
  KEY `core_jobmatchanalysis_user_id_2acd06b2_fk_core_user_id` (`user_id`),
  KEY `core_jobmatchanalysis_resume_id_5f7dccdb_fk_core_resume_id` (`resume_id`),
  KEY `core_jobmatchanalysis_created_at_c94d5b4b` (`created_at`),
  CONSTRAINT `core_jobmatchanalysis_job_id_ab18e03b_fk_core_jobdescription_id` FOREIGN KEY (`job_id`) REFERENCES `core_jobdescription` (`id`),
  CONSTRAINT `core_jobmatchanalysis_resume_id_5f7dccdb_fk_core_resume_id` FOREIGN KEY (`resume_id`) REFERENCES `core_resume` (`id`),
  CONSTRAINT `core_jobmatchanalysis_user_id_2acd06b2_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_jobrequirement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `importance` varchar(12) NOT NULL,
  `job_id` bigint NOT NULL,
  `skill_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_job_skill` (`job_id`,`skill_id`),
  KEY `core_jobrequirement_skill_id_73e962ee_fk_core_skill_id` (`skill_id`),
  CONSTRAINT `core_jobrequirement_job_id_589e0d5c_fk_core_jobdescription_id` FOREIGN KEY (`job_id`) REFERENCES `core_jobdescription` (`id`),
  CONSTRAINT `core_jobrequirement_skill_id_73e962ee_fk_core_skill_id` FOREIGN KEY (`skill_id`) REFERENCES `core_skill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_learningresource` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(180) NOT NULL,
  `url` varchar(200) NOT NULL,
  `level` varchar(40) NOT NULL,
  `skill_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_skill_resource` (`skill_id`,`url`),
  CONSTRAINT `core_learningresource_skill_id_6fd2cce8_fk_core_skill_id` FOREIGN KEY (`skill_id`) REFERENCES `core_skill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `headline` varchar(160) NOT NULL,
  `location` varchar(120) NOT NULL,
  `career_goal` varchar(240) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `core_profile_user_id_bf8ada58_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_resume` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(160) NOT NULL,
  `file` varchar(100) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_size` int unsigned NOT NULL,
  `quality_score` smallint unsigned NOT NULL,
  `quality_report` json NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_resume_user_id_b7bd5f45_fk_core_user_id` (`user_id`),
  KEY `core_resume_created_at_e18e53b0` (`created_at`),
  CONSTRAINT `core_resume_user_id_b7bd5f45_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`),
  CONSTRAINT `core_resume_chk_1` CHECK ((`file_size` >= 0)),
  CONSTRAINT `core_resume_chk_2` CHECK ((`quality_score` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_resumeskill` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `evidence` varchar(500) NOT NULL,
  `resume_id` bigint NOT NULL,
  `skill_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_resume_skill` (`resume_id`,`skill_id`),
  KEY `core_resumeskill_skill_id_d014adc4_fk_core_skill_id` (`skill_id`),
  CONSTRAINT `core_resumeskill_resume_id_77d3339c_fk_core_resume_id` FOREIGN KEY (`resume_id`) REFERENCES `core_resume` (`id`),
  CONSTRAINT `core_resumeskill_skill_id_d014adc4_fk_core_skill_id` FOREIGN KEY (`skill_id`) REFERENCES `core_skill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_skill` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` varchar(15) NOT NULL,
  `aliases` json NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_skill_related_skills` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `from_skill_id` bigint NOT NULL,
  `to_skill_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_skill_related_skill_from_skill_id_to_skill_i_d89267da_uniq` (`from_skill_id`,`to_skill_id`),
  KEY `core_skill_related_skills_to_skill_id_735b56aa_fk_core_skill_id` (`to_skill_id`),
  CONSTRAINT `core_skill_related_s_from_skill_id_854003b3_fk_core_skil` FOREIGN KEY (`from_skill_id`) REFERENCES `core_skill` (`id`),
  CONSTRAINT `core_skill_related_skills_to_skill_id_735b56aa_fk_core_skill_id` FOREIGN KEY (`to_skill_id`) REFERENCES `core_skill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_skillgapanalysis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `gaps` json NOT NULL,
  `roadmap` json NOT NULL,
  `match_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `match_id` (`match_id`),
  CONSTRAINT `core_skillgapanalysi_match_id_a4134044_fk_core_jobm` FOREIGN KEY (`match_id`) REFERENCES `core_jobmatchanalysis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_user_groups_user_id_group_id_c82fcad1_uniq` (`user_id`,`group_id`),
  KEY `core_user_groups_group_id_fe8c697f_fk_auth_group_id` (`group_id`),
  CONSTRAINT `core_user_groups_group_id_fe8c697f_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `core_user_groups_user_id_70b4d9b8_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `core_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_user_user_permissions_user_id_permission_id_73ea0daa_uniq` (`user_id`,`permission_id`),
  KEY `core_user_user_permi_permission_id_35ccf601_fk_auth_perm` (`permission_id`),
  CONSTRAINT `core_user_user_permi_permission_id_35ccf601_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `core_user_user_permissions_user_id_085123d3_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_core_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_core_user_id` FOREIGN KEY (`user_id`) REFERENCES `core_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS=1;
