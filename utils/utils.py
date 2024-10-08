import asyncio
import traceback

from selenium.common.exceptions import TimeoutException

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bypass.CloudflareBypasser import CloudflareBypasser

import pandas as pd
import io
import os
import keyboard
import math
import asyncio
import DrissionPage
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Actions

import time


project_dir = os.path.dirname(os.path.abspath(__file__))


def build_query_by_dialog_data(query : dict):
    result = ""
    html_content = ""
    if (query['years'].split()[0] == query['years'].split()[1]):
        result = result + query['query'] + f" AND PUBYEAR = {query['years'].split()[0]}"
    else:
        result = result + query['query'] + f" AND PUBYEAR > {query['years'].split()[0]}" + f" AND PUBYEAR < {query['years'].split()[1]}"

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

def downloads_done(folder_id):
    # Формируем абсолютный путь на основе заданной папки загрузки
    download_dir = os.path.expanduser(f"/Users/user/Documents/scopus_files/{folder_id}")
    file_path = os.path.join(download_dir, 'scopus.ris')
    while not os.path.isfile(file_path):
        time.sleep(5)


def set_prefs(folder_id):
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    download_dir = os.path.expanduser(f"/Users/user/Documents/scopus_files/{folder_id}")

    co = ChromiumOptions()
    co.set_browser_path(chrome_path)

    co.set_pref("download.default_directory", download_dir)
    co.set_pref("download.prompt_for_download", False)
    co.set_pref("directory_upgrade", True)
    co.set_pref("safebrowsing.enabled", True)
    co.set_pref("profile.default_content_setting_values.automatic_downloads", 1)

    return co


#result = [нашлось или нет, кол-во, самые новые, самые старые, самые цитируемые]
async def download_scopus_file(query : dict, folder_id: str, flag, future):

    text_query = build_query_by_dialog_data(query)
    num = '2500'

    co = set_prefs(folder_id=folder_id)

    try:
        browser = ChromiumPage(co)
        ac = Actions(browser)
        browser.get('https://www.scopus.com/search/form.uri?display=advanced')
        cf_bypasser = CloudflareBypasser(browser)
        cf_bypasser.bypass()

        time.sleep(6)
        keyboard.press_and_release('esc')
        try:
            try:
                time.sleep(2)
                browser('Accept all cookies').click()
            except:
                pass
            try:
                time.sleep(2)
                browser('Maybe later').click()
                time.sleep(2)
            except:
                pass
            sign_in_button = browser('Sign in').click()
            print("Sign-in button clicked")
            time.sleep(5)
            try:
                browser.ele('xpath://*[@id="bdd-password"]').input('miki00789')
                ac.key_down('RETURN')
            except:
                try:
                    browser('Accept all cookies').click()
                    time.sleep(2)
                except:
                    pass
                browser.ele('@id:bdd-email').click()
                browser.ele('@id:bdd-email').input('username')
                browser.ele('@id:bdd-email').click()
                keyboard.press_and_release('space')
                keyboard.press_and_release('backspace')
                continue_button = browser('Continue').click()
                time.sleep(5)
                browser.ele('xpath://*[@id="bdd-password"]').input('passwd')
                ac.key_down('RETURN')
            time.sleep(5)

            print("Email entered and submitted")
            
            print("Login successful")
        except DrissionPage.errors.NoRectError:
            try:
                elem = browser.ele('@id:contentEditLabel')
                print ("Page is ready!")
            except TimeoutException:
                browser.quit()
                print ("Loading took too much time!")
        except Exception as e:
            print('Error while logging in', e)
            traceback.print_exc()
            browser.quit()

        time.sleep(3)

        try:
            try:
                browser('Clear form').click()
            except:
                pass
            elem = browser.ele('@id:contentEditLabel')
            elem.input(text_query)
            browser.ele('xpath://*[@id="advSearch"]/span[1]').click()
        except Exception as e:
            print('Error while logging in', e)
            traceback.print_exc()
            browser.quit()

        result = []

        #нашлось или не нашлось
        
        time.sleep(6)
        try:
            elem = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[1]/div[3]/div/div/div[1]/h2')
            result.append(True)
        except NoSuchElementException:
            print("net statey")
            future.set_result([False])
            browser.quit()
            flag.set()
            return
            
        
        result.append(elem.text.split()[0])
        print(elem.text)
    
    # choose show 50
        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[2]/div/div/label/select/option[3]')
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")
            browser.quit()
        elem.click()
        time.sleep(3)

    
    # show all abstract
        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/button/span')
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")
            browser.quit()
        elem.click()
        time.sleep(3)

        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table')
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

        

        time.sleep(6)
        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[10]/td/div/div/button')
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
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select/option[2]')
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")
            browser.quit()
        elem.click()
        time.sleep(5)

        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table')
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
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select/option[3]')
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")
            browser.quit()
        elem.click()
        time.sleep(5)

        try:
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table')
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

        future.set_result(result)
        flag.set()
        await asyncio.sleep(3)
        print("flag was set and now we are waiting")
        await flag.wait()
        
        if (future.result() == False):
            browser.quit()
            return


    #  ----------------------

        # export button
        #elem = browser.find_element(By.XPATH, '/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[1]/span/button/span[1]')  # Find the search box
        try:
            elem = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[1]/span/button/span[1]')
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")
            browser.quit()
        elem.click()

        time.sleep(2)
        # "my ris settings" button
        try:
            browser('RIS').click()
            #elem = browser.ele('xpath://*[@id="menu-cvdqxc5om6"]/div[1]/button[2]/span')
            print ("Page is ready!")
        except TimeoutException:
            browser.quit()
            print ("Loading took too much time!")

        elem.click()

        # нажатие кнопки выбора кол-ва
        try:
            elem = browser.ele('xpath://*[@id="select-range"]')
            print ("Page is ready!")
        except TimeoutException:
            browser.quit()
            print ("Loading took too much time!")

        elem.click()    

        #левая и права границы
        try:
            elem_left = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/label/input')
            elem_right = browser.ele('xpath://*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div/label/input')
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
            time.sleep(5)
            elem = browser.ele('xpath:/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[2]/div/div/span[2]/div/div/button')
            print ("Page is ready!")
        except TimeoutException:
            browser.quit()
            print ("Loading took too much time!")

        elem.click()
        time.sleep(5)
        downloads_done(folder_id)
        flag.set()
        await asyncio.sleep(1.5)
        browser.quit()
        return
    except:
        print("kakoyto trouble")
        future.set_result([False])
        browser.quit()
        flag.set()
        return
