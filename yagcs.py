# constants
image_path="J:\\DCIM\\1000GRMN"
txt_username="mo***"
txt_password="***"
txt_name_prefix="MoCache: "
txt_description=r"Ein Geocache für cachende Motorradfahrer. Einfach zu finden, nur ranfahren, zugreifen, loggen und weiter. Anspruchsvolle Geocacher suchen sich besser ein anderes Ziel. Bitte Vorsicht an der Straße und eigenen Stift mitbringen!"
txt_reviewer=r"Einfacher Tradi ohne hohen Anspruch."
txt_hint="magnetisch"


# imports
import os
import math
import time
import pprint
import exifread
import requests
import send2trash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



# coovert to decimal degrees
def convert_to_degress(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


# background tile ermitteln
def getBackgroundTile(lat_deg, lon_deg):
    zoom=15
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    smurl = r"http://a.tile.openstreetmap.org/{0}/{1}/{2}.png"
    return smurl.format(zoom, xtile, ytile)


# hole koordinaten aus dem bild, gib decimal und text im GC format
def getGPS(filepath):
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(f)
        latitude = tags.get('GPS GPSLatitude')
        latitude_ref = tags.get('GPS GPSLatitudeRef')
        longitude = tags.get('GPS GPSLongitude')
        longitude_ref = tags.get('GPS GPSLongitudeRef')
        if latitude:
            lat_value = convert_to_degress(latitude)
            if latitude_ref.values != 'N':
                lat_value = -lat_value
        else:
            return {}
        if longitude:
            lon_value = convert_to_degress(longitude)
            if longitude_ref.values != 'E':
                lon_value = -lon_value
        else:
            return {}
        lat_text=str(latitude_ref.values)+str(convert_to_degress(latitude))
        lon_text=str(longitude_ref.values)+str(convert_to_degress(longitude))
        return lat_value, lon_value, lat_text, lon_text
    return {}


# hole den ort, bei der strasse den ref direkt von osm
def reverse_geocode(latlng):
    url="https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+str(latlng[0])+"4&lon="+str(latlng[1])+"&zoom=18&addressdetails=1"
    data = requests.get(url).json()
    pprint.pprint(data)
    osm_keys=['county','town','village','residential','city_district','suburb','hamlet','parking']
    mc_name=""
    for admin_level in osm_keys:
        if admin_level in data:
            mc_name = data[admin_level]
        if admin_level in data['address']:
            mc_name = data['address'][admin_level]
    osm_id=data['osm_id']
    # ref aus overpass holen
    url2 = "https://overpass.kumi.systems/api/interpreter?data=[out:json];way("+str(osm_id)+");out;"
    data2=requests.get(url2).json()
    pprint.pprint(data2)
    osm_keys2=['name','path','road','ref_int','ref']
    mc_road=""
    if len(data2['elements'])>0:
        for road_ref in osm_keys2:
            if road_ref in data2['elements'][0]:
                mc_road = data2['elements'][0][road_ref]
            if road_ref in data2['elements'][0]['tags']:
                mc_road = data2['elements'][0]['tags'][road_ref]
    # zusammenbauen
    mc_road=mc_road.replace(" ","")
    location=mc_name+" ("+mc_road+")"
    return location


# mach mal einen browser auf
def browser_aufmachen():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--start-maximized")
    driver = webdriver.Chrome('c:\\Python36\chromedriver.exe',chrome_options=chromeOptions)
    return (driver)



#
# main
#
for subdir, dirs, files in os.walk(image_path):
    for file in files:
        file_path = subdir + os.sep + file
        if ".jpg" in file_path.lower():

            # koordinaten aus dem bild holen
            print ("Datei:",file_path)
            gps = getGPS(file_path)
            coordline=gps[2]+" "+gps[3]
            print ("Koordinaten:",coordline)

            # adresse holen aus koordinaten
            formatted_address=reverse_geocode(gps)
            background_tile=getBackgroundTile(gps[0],gps[1])
            print ("Geocache-Name:",formatted_address)
            print ("Background:",background_tile)

            # page login
            browser=browser_aufmachen()
            browser.get("https://www.geocaching.com/account/login")
            time.sleep(2)
            browser.find_element_by_id("UsernameOrEmail").send_keys(txt_username)
            browser.find_element_by_id("Password").send_keys(txt_password)
            browser.find_element_by_id("SignIn").click()

            # stage 1
            time.sleep(5)
            browser.get("https://www.geocaching.com/hide/typelocation.aspx")
            time.sleep(2)
            try:
                browser.find_element_by_class_name("ui-dialog-buttonset").click()
                time.sleep(2)
            except:
                pass
            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            browser.find_element_by_id("ct_Traditional").click()
            time.sleep(2)
            browser.find_element_by_id("btnUnderstand").click()
            time.sleep(2)
            browser.find_element_by_id("uxCoordParse").clear()
            browser.find_element_by_id("uxCoordParse").send_keys(coordline)
            time.sleep(3)
            browser.find_element_by_id("searchButton").click()
            time.sleep(5)
            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            browser.find_element_by_id("btnContinue").click()

            # stage 2
            time.sleep(5)
            browser.find_element_by_id("btnContinue").click()

            # stage 3
            time.sleep(2)
            browser.find_element_by_id("ctl00_ContentBody_tbGeocacheName").clear()
            browser.find_element_by_id("ctl00_ContentBody_tbGeocacheName").send_keys(txt_name_prefix+formatted_address)
            browser.find_element_by_id("ctl00_ContentBody_tbBackgroundUrl").clear()
            browser.find_element_by_id("ctl00_ContentBody_tbBackgroundUrl").send_keys(background_tile)
            time.sleep(2)
            cke_frame=browser.find_element(By.TAG_NAME,"iframe")
            browser.switch_to.frame(cke_frame)
            cke_elem=browser.find_element(By.TAG_NAME,"body")
            browser.execute_script("var ele=arguments[0]; ele.innerHTML = '"+txt_description+"';", cke_elem)
            browser.switch_to.default_content()
            time.sleep(1)
            browser.find_element_by_id("tbHint").clear()
            browser.find_element_by_id("tbHint").send_keys(txt_hint)
            browser.find_element_by_id("ctl00_ContentBody_cbAgreement").click()
            browser.find_element_by_id("btnContinue").click()

            # stage 4
            time.sleep(2)
            browser.find_element_by_id("ctl00_ContentBody_imgExampleMicro").click()
            browser.find_element_by_id("ctl00_ContentBody_ctlAttributes_dtlAttributeIcons_ctl20_imgAttribute").click()
            browser.find_element_by_id("ctl00_ContentBody_ctlAttributes_dtlAttributeIcons_ctl47_imgAttribute").click()
            browser.find_element_by_id("btnSubmit").click()

            # upload stage
            time.sleep(5)
            saved_url=browser.current_url
            href_id=""
            contents = browser.find_elements_by_xpath('//a[@href]')
            for content in contents:
                href = content.get_attribute("href")
                if ("log.aspx?id=" in href):
                    href_id=href
            href=href_id.replace("log.aspx","upload.aspx")
            browser.get(href)
            browser.find_element_by_id("ctl00_ContentBody_ImageUploadControl1_uxFileUpload").send_keys(file_path)
            browser.find_element_by_id("ctl00_ContentBody_ImageUploadControl1_uxFileCaption").send_keys("Spoiler")
            browser.find_element_by_id("ctl00_ContentBody_ImageUploadControl1_uxUpload").click()

            # final stage
            time.sleep(10)
            browser.get(saved_url)
            time.sleep(3)
            browser.find_element_by_id("btnSubmit").click()
            time.sleep(2)
            browser.find_element_by_id("reviewerNoteText").send_keys(txt_reviewer)
            browser.find_element_by_id("btnSubmitForReview").click()

            # done
            browser.quit()
            time.sleep(2)
            send2trash.send2trash(file_path)
            print ("Done.")

