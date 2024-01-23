import os
import re
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

chrome_options = webdriver.ChromeOptions()
download_directory = './'
chrome_options.add_argument('--headless=new')

service = ChromeService(executable_path='./chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

login_url_et = os.getenv('login_url_et')
username_et = os.getenv('username_et')
password_et = os.getenv('password_et')


async def login_et(login_url: str, username: str, password: str) -> None:

    try:
        async def login():
            # Login to the ET server
            driver.get(login_url)
            driver.maximize_window()
            driver.find_element(By.ID, "Login1_UserName").send_keys(username)
            driver.find_element(By.ID, "Login1_Password").send_keys(password)
            driver.find_element(By.ID, "Login1_Login").click()

        async def anrp():
            # Download ANRP
            driver.find_element(By.NAME, "Акты").click()
            driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_btnSaveGridView_B").click()
            driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_ASPxTabCondition_T1").click()

            # Check ticks status and correct if needed
            try:
                driver.find_element(By.ID, "ClaimRegNumli1")\
                    .find_element(By.CLASS_NAME, "dxWeb_edtCheckBoxUnchecked")
                driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_ASPxTabCondition_"
                                           "ClaimRegNumPh1_S_D").click()
                driver.find_element(By.ID, "ValidToli1").find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdView"
                                           "Object_ASPxTabCondition_ValidToPh1_S_D").click()
                driver.find_element(By.ID, "DefectivePart1li1").find_element(By.ID, "ctl00_ctl00_phMain_topMain_gird"
                                           "ViewObject_ASPxTabCondition_DefectivePart1Ph1_S_D").click()
                driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_btnSavaParam_B").click()
                driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_btnExport_B").click()
                await asyncio.sleep(10)
            except:
                driver.find_element(By.NAME, "Акты").click()
                driver.find_element(By.ID, "ctl00_ctl00_phMain_topMain_girdViewObject_btnExport_B").click()
                await asyncio.sleep(10)

        # Create NSE check file
        def nse_check() -> None:
            directory_path = r'C:/Users/Barkhatov Sergei/Downloads'
            # Format the current date as a string in the desired format
            current_date = datetime.now().strftime("%d_%m_%y")
            report_anrp = f"exported_{current_date}.xlsx"

            # Read and modify ANRP file into NSE file
            excel_data = pd.read_excel(directory_path + "/" + report_anrp, engine='openpyxl')
            data = pd.DataFrame(excel_data, columns=['Cерийный номер', 'Статус', 'Регистрационный номер'])
            data = data.loc[data['Статус'] == 'Утвержден ECS']
            data['Регистрационный номер'] = data['Регистрационный номер'].str.slice(stop=9)
            data.to_excel(r'C:/Users/Barkhatov Sergei/Downloads/NSE.xlsx', index=False)

        # Delete downloaded files
        def delete_file() -> None:
            directory_path = r'C:/Users/Barkhatov Sergei/Downloads'
            # Format the current date as a string in the desired format
            current_date = datetime.now().strftime("%d_%m_%y")
            report_anrp = f"exported_{current_date}"

            # List all files in the directory
            all_files = sorted(os.listdir(directory_path))

            # Use a list comprehension to find files that match the pattern
            matching_file = [file for file in all_files if re.findall(report_anrp, file)][0]
            try:
                # Attempt to delete the file
                os.remove(directory_path + "/" + matching_file)
                print(f"Файл '{matching_file}' удален.")
            except OSError:
                print(f"Файл '{matching_file}' не найден.")

        # Python version check to run loop correctly
        if sys.version_info < (3, 10):
            loop = asyncio.get_event_loop()
        else:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        # Run the whole process
        async def create_tasks():
            tasks = [
                loop.create_task(login()),
                loop.create_task(anrp()),
            ]
            await asyncio.wait(tasks)

        loop.run_until_complete(create_tasks())
        nse_check()
        delete_file()
        print('Отчет загружен')
        driver.quit()

    except asyncio.TimeoutError:
        print("Не удалось залогиниться")
        driver.quit()
