import time
import logging
from .base_test import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .cluster_operator import ClusterManager, ConnectCluster
from .interaction_manager import InteractionManager
from tests.attack_suite_scenarios import AttackSuiteScenarios
from selenium.webdriver.common.action_chains import ActionChains
import cv2
import os

logger = logging.getLogger(__name__)

class RuntimeIncident(BaseTest):

    def run(self):
        cluster_manager = ClusterManager(self._driver, self._wait)
        connect_cluster = ConnectCluster(self._driver, self._wait)    

        login_url = self.get_login_url()
        self.login(login_url)

        try:
            logger.info("Running Runtime Incident test")
            # connect_cluster.click_get_started()
            # connect_cluster.connect_cluster_helm()
            # connect_cluster.verify_installation()
            # connect_cluster.view_cluster_button()
            # connect_cluster.view_connected_cluster()
            # self.deploy_attack_suite()
            # time.sleep(10)
            # self.create_app_layer_incident()
            print("Waiting for 120 seconds to allow the attack suite to be deployed...")
            # time.sleep(120)
            self.navigate_to_runtime_incidents()
        finally:
            logger.info("Runtime Incident test completed")

    def deploy_attack_suite(self):
        cluster_manager = ClusterManager(self._driver, self._wait)
        cluster_manager.run_shell_command("kubectl create namespace attack-suite")
        logger.info("Attack suite namespace created")
        time.sleep(1)
        
        # Deploy vulnerable applications for testing
        cluster_manager.run_shell_command("kubectl apply -n attack-suite -f ./tests/scripts/deploy-all.yaml")
        logger.info("Attack suite vulnerable applications deployed successfully")
        print("Waiting for 15 seconds to allow the deployment to complete...")
        time.sleep(15)
        cluster_manager.verify_application_profiles_completed()

    def create_app_layer_incident(self):
        create_incident = AttackSuiteScenarios(self._driver, self._wait)
        create_incident.create_incident("known-lfi.sh")
        logger.info("LFI attack executed successfully")

    def navigate_to_runtime_incidents(self):
        create_incident = AttackSuiteScenarios(self._driver, self._wait)
        
        #application layer incidents

        create_incident.create_incident("known-lfi.sh")
        self.validate_runtime_incident(
            incident_text='Process "python" accessed service account token',
            row_xpath="//tr[td[contains(text(), 'Unexpected access to service account token')]]",
            filter_name="Event name",
            checkbox_name="Unexpected service account token access",
            container_name="secure-python-app",
            canvas_filename="accessed_service_account_token.png",
            expected_image_path = os.path.join("expected_incident_graphs","process_python_accessed_service_account_token.png")
        )
        # unknown layer incidents
        create_incident.create_incident("unknown-ping.sh")
        self.validate_runtime_incident(
            incident_text='Unexpected process "ping" detected',
            row_xpath="//tr[td[contains(text(), 'Unexpected process launched: /bin/ping')]]",
            filter_name="Event name",
            checkbox_name="Unexpected process launched",
            container_name="ping-app",
            canvas_filename="unexpected_process_ping.png",
            expected_image_path = os.path.join("expected_incident_graphs","unexpected_process_ping_detected.png")
        )
        create_incident.create_incident("unknown-cve202432651.sh")
        self.validate_runtime_incident(
            incident_text='Potential server side template injection payload detected on process "python3"',
            row_xpath="//tr[td[contains(text(), 'Strings resembling server-side template injection attempts were detected in the HTTP request.')]]",
            filter_name="Event name",
            checkbox_name="Server-Side Template Injection Attack",
            container_name="changedetection",
            canvas_filename="potential_server_side_injection_python3.png",
            expected_image_path = os.path.join("expected_incident_graphs","potential_server_side_template_injection_payload_detected_python3.png")
        )
        create_incident.create_incident("known-malware-lfi.sh")
        self.validate_runtime_incident(
            incident_text='Unexpected process "tar" detected and exec to pod detected"',
            row_xpath="//tr[td[contains(text(), 'Exec to pod detected on pod secure-python-app-765f756575-zdfpv')]]",
            filter_name="Event name",
            checkbox_name="Exec to pod",
            container_name="secure-python-app",
            canvas_filename="tar_detected_and_exec_to_pod.png",
            expected_image_path = os.path.join("expected_incident_graphs",'tar_detected_and_exec_to_pod_detected.png')
        )
        create_incident.create_incident("known-sqli.sh")
        self.validate_runtime_incident(
            incident_text='Potential SQL injection payload detected on process "python"',
            row_xpath="//tr[td[contains(text(), 'SQL Injection Attempt')]]",
            filter_name="Event name",
            checkbox_name="SQL Injection Attempt",
            container_name="secure-python-app",
            canvas_filename="SQL_injection_python.png",
            expected_image_path = os.path.join("expected_incident_graphs","potential_SQL_injection_python.png")
        )
        self.validate_runtime_incident(
            incident_text='Potential SQL injection payload detected on process "nginx"',
            row_xpath="//tr[td[contains(text(), 'SQL Injection Attempt')]]",
            filter_name="Event name",
            checkbox_name="SQL Injection Attempt",
            container_name="nginx",
            canvas_filename="SQL_injection_nginx.png",
            expected_image_path = os.path.join("expected_incident_graphs", "potential_SQL_injection_nginx.png")
        )
        

    def validate_runtime_incident(self, incident_text, row_xpath, filter_name, checkbox_name, container_name,canvas_filename, expected_image_path):
        driver = self._driver
        interaction_manager = self._interaction_manager
        cluster_manager = ClusterManager(self._driver, self._wait)
        logger.info("waiting for the runtime incidents page to load")
        time.sleep(5)
        interaction_manager.click('threat-detection-left-menu-item', By.ID)
        time.sleep(1)

        self.verify_and_click_incident_by_text(incident_text)


        interaction_manager.click(row_xpath, By.XPATH)
        logger.info("Clicked on the incident row")
        time.sleep(2)

        interaction_manager.click("//span[@class='mdc-tab__text-label' and contains(normalize-space(text()), 'Affected Assets')]", By.XPATH)
        time.sleep(2)
        container=interaction_manager.get_text("//tr[td[contains(text(), 'Container')]]/td[@class='col-value']", By.XPATH)
        if container_name in container:
            logger.info(f"Container name '{container_name}' found in the incident details.")
        else:
            logger.error(f"Container name '{container_name}' not found in the incident details.")
            driver.save_screenshot(f"./failed_to_find_container_{ClusterManager.get_current_timestamp()}.png")
        ClusterManager.press_esc_key(driver)
        time.sleep(1)
        cluster_manager.click_filter_button(filter_name)
        time.sleep(1)
        cluster_manager.click_checkbox_by_name(checkbox_name)
        time.sleep(1)
        ClusterManager.press_esc_key(driver)
        time.sleep(1)
        self.click_on_dynamic_canvas(driver)
        time.sleep(2)
        self.snapshot_canvas(driver, canvas_filename)
        time.sleep(2)

        result = self.are_graphs_structurally_similar(canvas_filename, expected_image_path, match_threshold=120, distance_threshold=20)
        if result:
            logger.info("The incident graph matches the expected reference.")
        else:
            logger.error("The incident graph does NOT match the expected reference.")

    def verify_and_click_incident_by_text(self, expected_text):
        driver = self._driver
        spans = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.mat-mdc-tooltip-trigger.font-bold.font-size-14.line-height-24.armo-text-black-color.truncate-two-lines")))

        for span in spans:
            actual_text = span.text.strip()
            if expected_text in actual_text:
                span.click()
                logger.info(f"Verified and clicked on incident with text: '{expected_text}'")
                return

        logger.error(f"Text '{expected_text}' not found in any incident.")
        driver.save_screenshot(f"./failed_to_click_on_incident_{ClusterManager.get_current_timestamp()}.png")

    def click_on_dynamic_canvas(self, driver):
        try:
            canvas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.chart-container > canvas")))
            driver.execute_script("arguments[0].scrollIntoView(true);", canvas)
            ActionChains(driver).move_to_element_with_offset(canvas, 50, 50).click().perform()
            logger.info("Canvas clicked successfully.")
        except Exception as e:
            logger.error(f"Failed to click canvas: {e}")
            driver.save_screenshot("./failed_canvas_click.png")

    def snapshot_canvas(self, driver, filename="canvas_snapshot.png"):
        try:
            canvas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.chart-container > canvas")))
            driver.execute_script("arguments[0].scrollIntoView(true);", canvas)
            canvas.screenshot(filename)
            logger.info(f"Canvas snapshot saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to capture canvas snapshot: {e}")
            driver.save_screenshot("failed_canvas_snapshot.png")

    @staticmethod
    # def are_graphs_structurally_similar(img_path1: str, img_path2: str, match_threshold: int = 100, distance_threshold: int = 50) -> bool:
    #     img1 = cv2.imread(img_path1, 0)
    #     img2 = cv2.imread(img_path2, 0)
    #     if img1 is None or img2 is None:
    #         raise FileNotFoundError("One or both image paths are invalid.")

    #     orb = cv2.ORB_create()
    #     kp1, des1 = orb.detectAndCompute(img1, None)
    #     kp2, des2 = orb.detectAndCompute(img2, None)

    #     if des1 is None or des2 is None:
    #         logger.warning("No descriptors found in one of the images.")
    #         return False

    #     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #     matches = bf.match(des1, des2)
    #     good_matches = [m for m in matches if m.distance < distance_threshold]

    #     if len(good_matches) > match_threshold:
    #         return True

    #     # Save debug comparison
    #     comparison_image = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=2)
    #     cv2.imwrite(f"./graph_comparison_{ClusterManager.get_current_timestamp()}.png", comparison_image)
    #     return False
    @staticmethod
    def are_graphs_structurally_similar(img_path1: str, img_path2: str, match_threshold: int = 100, distance_threshold: int = 50, size: tuple = (800, 600)) -> bool:
        """
        Compare two graph images after resizing them to a consistent size.

        Args:
            img_path1 (str): First image path.
            img_path2 (str): Second image path.
            match_threshold (int): Number of good matches required to pass.
            distance_threshold (int): ORB match distance threshold.
            size (tuple): The (width, height) to normalize images to.

        Returns:
            bool: True if graphs are visually similar, False otherwise.
        """
        import cv2

        img1 = cv2.imread(img_path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img_path2, cv2.IMREAD_GRAYSCALE)

        if img1 is None or img2 is None:
            raise FileNotFoundError("One or both image paths are invalid.")

        # Normalize resolution
        img1 = cv2.resize(img1, size)
        img2 = cv2.resize(img2, size)

        # ORB detection
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        if des1 is None or des2 is None:
            logger.warning("No ORB descriptors found in one or both images.")
            return False

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        good_matches = [m for m in matches if m.distance < distance_threshold]

        logger.info(f"Good matches found: {len(good_matches)} (threshold: {match_threshold})")

        if len(good_matches) > match_threshold:
            return True

        # Save visual diff if not matching
        comparison_image = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=2)
        timestamp = ClusterManager.get_current_timestamp()
        cv2.imwrite(f"graph_comparison_{timestamp}.png", comparison_image)
        logger.info(f"Graph comparison saved as graph_comparison_{timestamp}.png")
        return False
