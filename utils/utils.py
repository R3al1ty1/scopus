import asyncio
import traceback
import random
import pandas as pd
import io
import os
import math
import asyncio
import DrissionPage

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bypass.CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Actions
from dotenv import load_dotenv

from utils.const import PROJECT_DIR, FILTERS_DCT


load_dotenv()

used_ports = []

project_dir = PROJECT_DIR


async def build_query_by_dialog_data(query : dict):
    """Функция для построения запроса в Scopus."""
    result = ""
    html_content = ""

    result += f"{FILTERS_DCT[query['filter_type']]}("
    result += f"{query['query']})"
    if (query['years'].split()[0] == query['years'].split()[1]):
        result = result + f" AND PUBYEAR = {query['years'].split()[0]}"
    else:
        result = result + f" AND PUBYEAR > {query['years'].split()[0]}" + f" AND PUBYEAR < {query['years'].split()[1]}"

    langs = []
    langs_str = ''
    if (query['eng']):
        langs.append('LIMIT-TO ( LANGUAGE , "English" )')
    if (query['ru']):
        langs.append('LIMIT-TO ( LANGUAGE , "Russian" )')
    if (len(langs)):
        langs_str = ' OR '.join(langs)
        langs_str = f' AND ( {langs_str} )'
        result = result + langs_str

    files = []
    files_str = ''
    if (query['conf']):
        files.append('LIMIT-TO ( DOCTYPE , "cp" )')
    if (query['rev']):
        files.append('LIMIT-TO ( DOCTYPE , "re" )')
    if (query['art']):
        files.append('LIMIT-TO ( DOCTYPE , "ar" )')    
    if (len(files)):
        files_str = ' OR '.join(files)
        files_str = f' AND ( {files_str} )'
        result = result + files_str
    print(result)
    return result

#global warning AND PUBYEAR > 1971 AND PUBYEAR < 2026 AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Russian" ) ) AND ( LIMIT-TO ( DOCTYPE , "cp" ) OR LIMIT-TO ( DOCTYPE , "re" ) OR LIMIT-TO ( DOCTYPE , "ar" ) )

async def downloads_done(folder_id):
    max_retries = 26
    download_dir = os.path.expanduser(f"{project_dir}/scopus_files/{folder_id}")
    file_path = os.path.join(download_dir, 'scopus.ris')
    for i in range(max_retries):
        if not os.path.isfile(file_path):
            await asyncio.sleep(2)
        else:
            break

async def generate_port():
    """Создание порта для запуска браузера."""
    while True:
        port = random.randint(9000, 9500)
        if port not in used_ports:
            return port


async def set_prefs(folder_id):
    """Установление парамтеров браузера"""
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    download_dir = os.path.expanduser(f"{project_dir}/scopus_files/{folder_id}")

    co = ChromiumOptions()
    co.set_browser_path(chrome_path)

    co.set_pref("download.default_directory", download_dir)
    co.set_pref("download.prompt_for_download", False)
    co.set_pref("directory_upgrade", True)
    co.set_pref("safebrowsing.enabled", True)
    co.set_pref("profile.default_content_setting_values.automatic_downloads", 1)
    co.set_argument('--start-maximized')
    
    port = await generate_port()
    used_ports.append(port)
    
    co.set_local_port(port)
    
    return co


async def authorization_scopus(browser, ac):
    """Авторизация Scopus."""
    try:
        try:
            browser.ele('Accept all cookies', timeout=4).click()
        except:
            pass
        try:
            await asyncio.sleep(2)
            browser.ele('Maybe later', timeout=4).click()
        except:
            pass
        sign_in_button = browser.ele('Sign in', timeout=4).click()
        print("Sign-in button clicked")
        try:
            browser.ele('xpath://*[@id="bdd-password"]', timeout=4).input(os.getenv('PASSWORD'))
            await asyncio.sleep(0.5)
            ac.key_down('RETURN')
        except:
            try:
                browser.ele('Accept all cookies', timeout=4).click()
            except:
                pass
            browser.ele('@id:bdd-email', timeout=4).click()
            browser.ele('@id:bdd-email', timeout=4).input(os.getenv('LOGIN'))
            browser.ele('@id:bdd-email', timeout=4).click()
            
            continue_button = browser.ele('Continue', timeout=4)
            continue_button.run_js("document.getElementById('bdd-elsPrimaryBtn').removeAttribute('disabled')")
            continue_button.click()
            browser.ele('xpath://*[@id="bdd-password"]', timeout=4).input(os.getenv('PASSWORD'))
            await asyncio.sleep(0.5)
            ac.key_down('RETURN')
        # await asyncio.sleep(3)

        print("Email entered and submitted")
        
        print("Login successful")
    except DrissionPage.errors.NoRectError:
        try:
            elem = browser.ele('@id:contentEditLabel', timeout=4)
            print ("Page is ready!")
        except TimeoutException:
            browser.quit()
            print ("Loading took too much time!")
    except Exception as e:
        print('Error while logging in', e)
        traceback.print_exc()
        browser.quit()


async def prepare_for_export(browser, result):
    """Поиск по статьям из запроса."""
    # choose show 50
    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[2]/div/div/label/select/option[3]', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()
    elem.click()
    await asyncio.sleep(1.5)


    # show all abstract
    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/button/span', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()
    elem.click()
    await asyncio.sleep(1.5)

    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table', timeout=4)
        print ("Page is ready!")
    except Exception as e:
        print('Error while logging in', e)
        traceback.print_exc()
        browser.quit()
    try:
        html_content = elem.html
    except Exception as e:
        print('Error while logging in', e)
        browser.quit()
        traceback.print_exc()


    #['Unnamed: 0', 'Document title', 'Authors', 'Source', 'Year', 'Citations']
    #'Hide abstract'
    #'View at Publisher. Opens in a new tab.Related documents'
    try:
        df = pd.read_html(io.StringIO(html_content))[0]
        i = 1
        result.append([])
        j = 2
        skip_seventh_row = False
    except Exception as e:
        print('Error while logging in', e)
        traceback.print_exc()
        browser.quit()

    await asyncio.sleep(1.5)
    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[10]/td/div/div/button', timeout=4)
        skip_seventh_row = True
    except NoSuchElementException:
        print("do not skip")


    while (i < df.shape[0]):
        result[j].append({})
        result[j][-1]['Title'] = df['Document title'][i]
        if (not (isinstance(df['Document title'][i + 1], float) and math.isnan(df['Document title'][i + 1]))):
            result[j][-1]['Abstract'] = df['Document title'][i + 1][13:-56]
        result[j][-1]['Authors'] = df['Authors'][i]
        result[j][-1]['Source'] = df['Source'][i]
        result[j][-1]['Year'] = df['Year'][i]
        result[j][-1]['Citations'] = df['Citations'][i]
        if (i == 7 and skip_seventh_row):
            i += 1
        i = i + 3
    print(len(result[2]))


    # change to oldest

    try:
        await asyncio.sleep(1)
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select/option[2]', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()
    elem.click()
    await asyncio.sleep(1.5)

    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()

    df = pd.read_html(io.StringIO(elem.html))[0]
    i = 1
    j = 3
    result.append([])

    while (i < df.shape[0]):
        result[j].append({})
        result[j][-1]['Title'] = df['Document title'][i]
        if (not (isinstance(df['Document title'][i + 1], float) and math.isnan(df['Document title'][i + 1]))):
            result[j][-1]['Abstract'] = df['Document title'][i + 1][13:-56]
        result[j][-1]['Authors'] = df['Authors'][i]
        result[j][-1]['Source'] = df['Source'][i]
        result[j][-1]['Year'] = df['Year'][i]
        result[j][-1]['Citations'] = df['Citations'][i]
        if (i == 7 and skip_seventh_row):
            i += 1
        i = i + 3
    print(len(result[j]))

    # chage to most cited

    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select/option[3]', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()
    elem.click()
    await asyncio.sleep(1.5)

    try:
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()

    df = pd.read_html(io.StringIO(elem.html))[0]
    i = 1
    j = 4
    result.append([])

    while (i < df.shape[0]):
        result[j].append({})
        result[j][-1]['Title'] = df['Document title'][i]
        if (not (isinstance(df['Document title'][i + 1], float) and math.isnan(df['Document title'][i + 1]))):
            result[j][-1]['Abstract'] = df['Document title'][i + 1][13:-56]
        result[j][-1]['Authors'] = df['Authors'][i]
        result[j][-1]['Source'] = df['Source'][i]
        result[j][-1]['Year'] = df['Year'][i]
        result[j][-1]['Citations'] = df['Citations'][i]
        if (i == 7 and skip_seventh_row):
            i += 1
        i = i + 3    
    print(len(result[2]))
        

async def export_file(browser, flag, folder_id, result):
    """Экспортирование файла."""
    # export button
    try:
        elem = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[1]/span/button/span[1]', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
        browser.quit()
    elem.click()

    # await asyncio.sleep(2)
    # "my ris settings" button
    try:
        browser.ele('RIS', timeout=4).click()
        print ("Page is ready!")
    except TimeoutException:
        browser.quit()
        print ("Loading took too much time!")

    elem.click()

    # нажатие кнопки выбора кол-ва
    try:
        elem = browser.ele('xpath://*[@id="select-range"]', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        browser.quit()
        print ("Loading took too much time!")

    elem.click()    

    #левая и права границы
    try:
        elem_left = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/label/input', timeout=4)
        elem_right = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div/label/input', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        browser.quit()
        print ("Loading took too much time!")    

    num = result[1]
    num = num.replace(',', '')
    num = min(2500, int(num))
    elem_left.input("1")
    elem_right.input(str(num))  

    # "export" (finish) button
    try:
        # await asyncio.sleep(3)
        elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[2]/div/div/span[2]/div/div/button', timeout=4)
        print ("Page is ready!")
    except TimeoutException:
        browser.quit()
        print ("Loading took too much time!")

    elem.click()


#result = [нашлось или нет, кол-во, самые новые, самые старые, самые цитируемые]
async def download_scopus_file(query: dict, folder_id: str, flag, future):
    """Функция обработки запроса пользователя."""
    result = []
    text_query = await build_query_by_dialog_data(query)
    num = '2500'

    co = await set_prefs(folder_id=folder_id)

    try:
        browser = ChromiumPage(co)
        ac = Actions(browser)
        browser.set.timeouts(base=3, page_load=3)
        browser.get('https://www.scopus.com/search/form.uri?display=advanced')
        cf_bypasser = CloudflareBypasser(browser)
        await cf_bypasser.bypass()

        # await asyncio.sleep(3)

        await authorization_scopus(browser=browser, ac=ac)

        # await asyncio.sleep(3)

        try:
            try:
                browser.ele('Clear form', timeout=4).click()
            except:
                pass
            elem = browser.ele('@id:contentEditLabel', timeout=4)
            elem.input(text_query)
            browser.ele('xpath://*[@id="advSearch"]/span[1]', timeout=4).click()
        except Exception as e:
            print('Error while logging in', e)
            traceback.print_exc()
            browser.quit()

        #нашлось или не нашлось
        
        # await asyncio.sleep(3)
        try:
            elem = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[1]/div[3]/div/div/div[1]/h2', timeout=4)
            result.append(True)
        except NoSuchElementException:
            print("net statey")
            future.set_result([False])
            browser.quit()
            flag.set()
            return
            
        
        result.append(elem.text.split()[0])
        print(elem.text)

    #  ----------------------

        await prepare_for_export(browser=browser, result=result)

        future.set_result(result)
        flag.set()
        # await asyncio.sleep(3)
        
        if (future.result() == False):
            browser.quit()
            return

        print("flag was set and now we are waiting")
        await flag.wait()

        await export_file(browser=browser, flag=flag, folder_id=folder_id, result=result)

        res = await downloads_done(folder_id)
        if res:
            flag.set()

        browser.quit()
        return
    except:
        print("kakoyto trouble")
        traceback.print_exc()
        future.set_result([False])
        browser.quit()
        flag.set()
        return
