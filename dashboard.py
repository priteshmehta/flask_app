#!/usr/local/bin/python
from flask import Flask, jsonify, make_response, request, abort
from db_manager import DbManager
import time
from config import config
import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('dashboard_service.log')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

app = Flask(__name__)

@app.route('/api/v1')
def index():
    return "Service is running"

@app.route('/api/v1/results', methods=['POST'])
def insert_data():
    account_plan = ''
    account_phase = ''
    tc_results = ''

    #Mandatory keys
    try:
        tc_results = request.json.get("tc_results")
        account_phase = request.json.get("account_phase").lower()
    except Exception as e:
        logger.error("error in getting test results")
        abort(400)

    if account_phase not in {'phase0', 'phase1', 'phase2', 'phase3', 'phase4'}:
        logger.error("Invalid account phase")
        abort(400)

    #optional keys
    try:
        account_plan = request.json.get("account_plan")
    except:
        pass

    db_result_hash = {}
    result_id = str(int(time.time()))  # epoch time
    db = DbManager()
    db.connect(config["db_user"], config["db_password"], config["db_server"], config["db_schema"])

    # Account plan is an optional
    if account_plan.isalpha():
        data = db.get_results("get_plan_id", [account_plan.lower().strip()])
        try:
            db_result_hash["plan"] = int(data[0][0][0])
        except Exception as e:
            logging.info("Invalid account plan. Error: %s", (e))

    # Account phase is mandatory
    data = db.get_results("get_phase_id", [account_phase.lower().strip()])
    try:
        db_result_hash["phase"] = int(data[0][0][0])
    except Exception as e:
        logger.error("Ivalid account phase")
        abort(400)

    try:
        browser = request.json.get("browser")
        (browser_name, browser_ver) = browser.split(':')
        data = db.get_results("get_browser_id", [browser_name.lower().strip(), browser_ver.strip()])
        try:
            db_result_hash["browser"] = int(data[0][0][0])
        except Exception as e:
            logger.debug("Browser not found in db hence inserting it.")
            column_dict = {"browser_name": browser_name, "browser_version": browser_ver}
            db_result_hash["browser"] = db.insert_browser_detail(column_dict)
    except Exception as e:
        logger.info("erro: %s" % (e))


    db_result_hash["test_result_id"] = result_id

    if 'job_name' in request.json:
        db_result_hash["Jenkins_job_name"] = request.json.get("job_name")
    if 'build_number' in request.json:
        db_result_hash["jenkins_build_number"] = request.json.get("build_number")
    if 'test_environment' in request.json:
        db_result_hash["test_environment"] = request.json.get("test_environment")
    if 'test_type' in request.json:
        db_result_hash["test_type"] = request.json.get("test_type")

    db_result_hash["total_tests"] = len(tc_results)
    db_result_hash["test_pass"] = len([tc for tc in tc_results if tc.get("test_status").lower() == "pass"])
    db_result_hash["test_fail"] = len(tc_results) - db_result_hash["test_pass"]
    db_result_hash["test_skip"] = 0  # Not supported in existing automation report
    db_result_hash["git_branch"] = ""  # TBD
    db_result_hash["git_commit"] = ""  # TBD

    # Insert into Database
    if db.insert_data(db_result_hash, tc_results):
        msg = jsonify({'message': "Inserted Successfully"})
        logger.info("Inserted Successfully, Result id: %s" % (result_id))
    else:
        msg = jsonify({'message': "Failed to insert"})
        logger.info("Failed to insert, Result id: %s" % (result_id))

    db.close()
    return msg

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
