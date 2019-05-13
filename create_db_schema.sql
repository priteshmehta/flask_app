CREATE DATABASE automation_result_schema;
USE automation_result_schema;
CREATE TABLE automation_result_schema.browser_master(id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), browser_name VARCHAR(100), browser_version VARCHAR(100));
CREATE TABLE automation_result_schema.plan_master(id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), plan_name VARCHAR(100));
CREATE TABLE automation_result_schema.phase_master(id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), phase_name VARCHAR(100));
CREATE TABLE automation_result_schema.test_results_summary(timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,id INT NOT NULL AUTO_INCREMENT,PRIMARY KEY (id), jenkins_job_name VARCHAR(255), 
	test_environment VARCHAR(255),jenkins_build_number VARCHAR(255), git_branch VARCHAR(100), git_commit VARCHAR(65), browser INT, plan INT, phase INT,  test_type VARCHAR(100), test_result_id VARCHAR(50) NOT NULL, 
	total_tests INT  NOT NULL ,test_pass INT  NOT NULL, test_fail INT  NOT NULL, test_skip INT  NOT NULL, FOREIGN KEY (browser) REFERENCES browser_master(id), FOREIGN KEY (plan) REFERENCES plan_master(id),
	FOREIGN KEY (phase) REFERENCES phase_master(id));
CREATE TABLE automation_result_schema.test_results_detail (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id),  test_summary_id INT NOT NULL, test_class VARCHAR(100), test_method VARCHAR(100), test_status VARCHAR(10), root_cause VARCHAR(100), error_log VARCHAR(65000), INDEX result_index (test_summary_id), FOREIGN KEY (test_summary_id) REFERENCES test_results_summary(id) ON DELETE CASCADE);

INSERT INTO automation_result_schema.plan_master (plan_name) VALUES ('lite');
INSERT INTO automation_result_schema.plan_master (plan_name) VALUES ('team');
INSERT INTO automation_result_schema.plan_master (plan_name) VALUES ('enterprise');
INSERT INTO automation_result_schema.plan_master (plan_name) VALUES ('professional');
INSERT INTO automation_result_schema.phase_master (phase_name) VALUES ('phase0');
INSERT INTO automation_result_schema.phase_master (phase_name) VALUES ('phase1');
INSERT INTO automation_result_schema.phase_master (phase_name) VALUES ('phase2');
INSERT INTO automation_result_schema.phase_master (phase_name) VALUES ('phase3');
INSERT INTO automation_result_schema.phase_master (phase_name) VALUES ('phase4');


USE `automation_result_schema`;
DROP procedure IF EXISTS `get_plan_id`;

DELIMITER $$
USE `automation_result_schema`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_plan_id`(IN plan_name_param varchar(64))
BEGIN
	SELECT id  FROM plan_master where plan_master.plan_name = plan_name_param;
END$$

DELIMITER ;


USE `automation_result_schema`;
DROP procedure IF EXISTS `get_phase_id`;

DELIMITER $$
USE `automation_result_schema`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_phase_id`(IN phase_name_param varchar(64))
BEGIN
	SELECT id  FROM phase_master where phase_master.phase_name = phase_name_param;
END$$

DELIMITER ;


USE `automation_result_schema`;
DROP procedure IF EXISTS `get_browser_id`;

DELIMITER $$
USE `automation_result_schema`$$
CREATE PROCEDURE `get_browser_id` (IN browser_name_param varchar(64), IN browser_ver_param varchar(64))
BEGIN
	SELECT id  FROM browser_master where browser_master.browser_name = browser_name_param and  browser_master.browser_version =  browser_ver_param;
END$$

DELIMITER ;