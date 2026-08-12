import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost/DamnCRUD-uas2026"
USERNAME = "admin"
PASSWORD = "admin"
TIMEOUT  = 10


def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(TIMEOUT)
    return driver


def login(driver):
    driver.get(f"{BASE_URL}/login.php")
    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, TIMEOUT).until(EC.url_contains("index.php"))


# TC-03
class TestCreateContact:

    def setup_method(self):
        self.driver = get_chrome_driver()
        login(self.driver)

    def teardown_method(self):
        self.driver.quit()

    def test_create_contact_valid(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/create.php")

        assert "Add new contact" in driver.title

        unique_name = f"Budi {int(time.time())}"
        
        driver.find_element(By.ID, "name").send_keys(unique_name)
        driver.find_element(By.ID, "email").send_keys("budi.santoso@test.com")
        driver.find_element(By.ID, "phone").send_keys("081234567890")
        driver.find_element(By.ID, "title").send_keys("Tester")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, TIMEOUT).until(EC.url_contains("index.php"))
        time.sleep(1)

        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
        search_box.send_keys(unique_name)
        time.sleep(1.5)

        visible_rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        assert len(visible_rows) >= 1
        assert unique_name in visible_rows[0].text

    def test_create_contact_empty_name(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/create.php")

        driver.find_element(By.ID, "email").send_keys("kosong@test.com")
        driver.find_element(By.ID, "phone").send_keys("0800000000")
        driver.find_element(By.ID, "title").send_keys("None")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        time.sleep(1)
        assert "create.php" in driver.current_url or "Add new contact" in driver.title


# TC-04
class TestReadContacts:

    def setup_method(self):
        self.driver = get_chrome_driver()
        login(self.driver)

    def teardown_method(self):
        self.driver.quit()

    def test_dashboard_loads_with_table(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")

        table = driver.find_element(By.ID, "employee")
        assert table is not None

        rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        assert len(rows) >= 1

    def test_dashboard_shows_correct_columns(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")

        headers = driver.find_elements(By.CSS_SELECTOR, "#employee thead th")
        header_texts = [h.text.strip() for h in headers]

        for col in ["Name", "Email", "Phone", "Title", "Created"]:
            assert col in header_texts

    def test_search_functionality(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")
        time.sleep(1)

        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
        search_box.send_keys("David")
        time.sleep(1)

        visible_rows = driver.find_elements(
            By.CSS_SELECTOR, "#employee tbody tr:not(.dataTables_empty)"
        )
        assert len(visible_rows) >= 1
        for row in visible_rows:
            assert "david" in row.text.lower()


# TC-05
class TestUpdateContact:

    def setup_method(self):
        self.driver = get_chrome_driver()
        login(self.driver)

    def teardown_method(self):
        self.driver.quit()

    def test_update_contact(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")
        time.sleep(1)

        edit_btn = driver.find_element(By.CSS_SELECTOR, "#employee a.btn-success")
        edit_btn.click()

        WebDriverWait(driver, TIMEOUT).until(EC.url_contains("update.php"))

        name_field = driver.find_element(By.ID, "name")
        name_field.clear()
        name_field.send_keys("Updated Name UAS")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, TIMEOUT).until(EC.url_contains("index.php"))
        time.sleep(1)
        assert "Updated Name UAS" in driver.page_source


# TC-06
class TestDeleteContact:

    def setup_method(self):
        self.driver = get_chrome_driver()
        login(self.driver)
        self._create_temp_contact()

    def teardown_method(self):
        self.driver.quit()

    def _create_temp_contact(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/create.php")
        driver.find_element(By.ID, "name").send_keys("HAPUS INI")
        driver.find_element(By.ID, "email").send_keys("hapus@test.com")
        driver.find_element(By.ID, "phone").send_keys("0000000000")
        driver.find_element(By.ID, "title").send_keys("Temp")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, TIMEOUT).until(EC.url_contains("index.php"))
        time.sleep(1)

    def test_delete_contact(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")
        time.sleep(1)

        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
        search_box.send_keys("HAPUS INI")
        time.sleep(1.5)

        rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        target_row = rows[0] if rows and "HAPUS INI" in rows[0].text else None

        assert target_row is not None

        delete_btn = target_row.find_element(By.CSS_SELECTOR, "a.btn-danger")
        delete_btn.click()

        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept()
        except Exception:
            pass

        WebDriverWait(driver, TIMEOUT).until(EC.url_contains("index.php"))
        time.sleep(1)
        assert "HAPUS INI" not in driver.page_source


# TC-07
class TestUnauthorizedAccess:

    def setup_method(self):
        self.driver = get_chrome_driver()

    def teardown_method(self):
        self.driver.quit()

    def test_index_redirects_to_login_without_session(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/index.php")
        time.sleep(1)

        assert "login.php" in driver.current_url
        form = driver.find_element(By.CSS_SELECTOR, "form.form-signin")
        assert form is not None

    def test_create_redirects_to_login_without_session(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/create.php")
        time.sleep(1)

        assert "login.php" in driver.current_url

    def test_delete_redirects_to_login_without_session(self):
        driver = self.driver
        driver.get(f"{BASE_URL}/delete.php?id=1")
        time.sleep(1)

        assert "login.php" in driver.current_url
