import logging
import json
from aiogram import *
import asyncio
import time
from aiogram.types import chat_permissions, inline_keyboard
import requests
from bs4 import BeautifulSoup
import random
import pymongo
from pymongo import MongoClient
import urllib.parse
from datetime import datetime, timedelta
import string

Admin = '@mayank36'
BotName = 'Chegg unblur by MG'
mainGroupId = -1001612479212
adminGroupId = -1001179487467
logsGroupId = -1001664380876
free = -1001645929935
adminId = 2048662709


botLink = "http://t.me/cheggpremiumunlimitedbot"

username = urllib.parse.quote_plus('MAYANK')
password = urllib.parse.quote_plus('MAYANK')


# url = "mongodb+srv://%s:%s@premiumwarrior.jmt0s.mongodb.net/tgdata"
# cluster = MongoClient(url % (username, password))

# db = cluster["tgdata"]

# collection = db["tgusers"]

url = "mongodb+srv://%s:%s@cluster0.nwd1n.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
cluster = MongoClient(url % (username, password))

db = cluster["TGDATA"]

collection = db["TGDATA"]

# API_TOKEN = '1834750087:AAFfudHVQ5vb-ZyiJr0errhBmUWanleTpo8'
API_TOKEN = '5195517367:AAEggIPeEoCSUqpQeLSud1qzmFy0v4_I7UU'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
client = Dispatcher(bot)


@client.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    print(message.chat.id)
    await message.reply(f"\n\n Hi!\n\n This is {BotName} \n\n want to buy premium contact {Admin} \n\n 4) /mydata to check your validity")


            
@client.message_handler(commands=['mydata'])
async def udata(message: types.Message):
    user = str(message.reply_to_message.from_user.id)
    users = collection.find_one({"userid": user})
    if users == None:
        await message.reply(
            f"sorry You are not a premium member or your premium validity expired \n\n please contact {Admin} for premium subscription")
    else:
        Expdate = users['ExpDate']
        await message.reply(f"\n\n Hi! @{message.from_user.username or message.from_user.first_name} below is your data : \n\n your subscription end on : \n\n {Expdate}")


# @client.message_handler(commands=['price'])
# async def udata(message: types.Message):
#     price_message = "**PRICES AND PACKAGES LIST**\n\n=>285₹ or 4$ for 30days : Unlimited solutions.\n\n=>200₹ 0r 3$ for 15days : unlimited solutions\n\n=>100₹ or 2$ for 10days : unlimited solutions"
#     await message.reply(price_message)


# @client.message_handler(commands=['pay'])
# async def udata(message: types.Message):
#     price_message = "**HOW TO PAY?**\n\n**FOR INDIAN MEMBERS**\n\n1)Check Prices by using this command /price\n\n2)select your package and pay the money to this UPI Id : jaffa4321@apl\n\n3)After your payment completed send screen short to Owner {Admin}\n\nYour package will added as soon as owner sees the screenshort\n\nThat's it Thankyou."
#     await message.reply(price_message)


# @client.message_handler(commands=['tutorial'])
# async def udata(message: types.Message):
#     price_message = "**TUTORIAL**\n\nAfter Your payment completed check this video\n\n "
#     await message.reply(price_message)
all_genid = []


@client.message_handler(commands=['gen', 'genrate'])
async def gen(message: types.Message):
    if message.chat.id == adminGroupId:
        arguments = message.get_args()
        a_data = arguments.split(":")
        gen_amout = a_data[0]
        gen_days = a_data[1]
        for i in range(int(gen_amout)):
            gen = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=10))
            collection.insert_one(
                {"genId": gen, "days": gen_days, "added_by": message.from_user.username or message.from_user.first_name})
        for i in collection.find({"days": gen_days}):
            all_genid.append(i)
        shot_list = list(all_genid)[:int(gen_amout)]
        for g_id in shot_list:
            gg_id = g_id['genId']
            gg_days = g_id['days']
            gg_added_by = g_id['added_by']
            await message.reply(f"/redeem {gg_id}")
            await message.reply(f"days: {gg_days}, added_by: {gg_added_by}")
        all_genid.clear()
    else:
        await message.reply("you cant genrate tokens here you must be in admin group to genrate tokens sorry.!")


@client.message_handler(commands=['remove', 'revoke', 'Remove', 'Revoke'])
async def gen(message: types.Message):
    if message.chat.id == adminGroupId:
        arguments = message.get_args()
        revoke_user = collection.find_one({"userid": arguments})
        print(revoke_user)
        if revoke_user == None:
            await message.reply("User is not exist in database please check your id")
        else:
            collection.delete_one({"userid": arguments})
            await message.reply(
                f"user of id {revoke_user['userid']} sucessfully deleted from database ")
    else:
        await message.reply("you cant use this here sorry.")


@client.message_handler(commands=['redeem', 'Redeem'])
async def redeem(message: types.Message):
    if message.chat.id == mainGroupId:
        keyboard = inline_keyboard.InlineKeyboardMarkup(
            row_width=3)
        button = inline_keyboard.InlineKeyboardButton(
            'Click here', url=botLink)
        keyboard.add(button)
        await message.reply(f"please redeem token in bot Dm", reply_markup=keyboard)
        return
    arguments = message.get_args()
    db_gen_id = collection.find_one({"genId": arguments})
    if db_gen_id == None:
        await message.reply("sent a wrong token or this token is expired,\n\n Dont spam me ah.")
    else:
        try:
            userId = str(message.from_user.id)
            numberOfDays = db_gen_id['days']
            added_by = db_gen_id['added_by']
            print(userId, numberOfDays, arguments)
            await open_account(userId, numberOfDays, message)
            collection.find_one_and_delete({"genId": arguments})
            await bot.send_message(logsGroupId, f"user of id {userId} and userName of @{message.from_user.username or message.from_user.first_name} added succefully in database for {numberOfDays} days \n\n And this user is added by {added_by} \n\n Redeem Code is : {arguments}")
        except Exception as e:
            print(e)


async def open_account(user, numberOfDays, message):
    users = collection.find_one({"userid": user})
    if users != None:
        await bot.send_message(adminId, f"user of id {user} alredy in database")
        return False
    else:
        present = datetime.now()
        string_input_with_date = present + timedelta(days=int(numberOfDays))
        future_s = string_input_with_date.strftime("%d/%m/%Y")
        collection.insert_one(
            {"userid": user, "ExpDate": future_s})

        Invite_link = await bot.create_chat_invite_link(mainGroupId)
        I_link = Invite_link['invite_link']

        await bot.send_message(user, f"Hi you added as a premium member for  {numberOfDays} days \n\nAnd join this bellow private channel to send chegg links \n\n{I_link}\n\n Thankyou")
        await bot.send_message(adminId, f"user of id {user} added succefully in database for {numberOfDays} days \n\n Thankyou")

            
            

            

lock_permissions = {
    'can_send_messages': False,
    'can_send_media_messages': None,
    'can_send_polls': None,
    'can_send_other_messages': None,
    'can_add_web_page_previews': None,
    'can_change_info': None,
    'can_invite_users': None,
    'can_pin_messages': None
}
unlock_permissions = {
    'can_send_messages': True,
    'can_send_media_messages': None,
    'can_send_polls': None,
    'can_send_other_messages': None,
    'can_add_web_page_previews': None,
    'can_change_info': None,
    'can_invite_users': None,
    'can_pin_messages': None
}

s = requests.Session()
cookie_list = [{
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'cookie': 'optimizelyEndUserId=oeu1645456970243r0.5709479619316735; C=0; O=0; _pxvid=2fac09c8-932a-11ec-a43f-5a497a567757; _omappvp=qwOiyMdEZJ1EiYtcXUntCUn5LKDwli15nVSDZ9csKrUwKtb0v54LUPjc4uUebr2aAf2SX8oXCoSXeZMwjZPXgy2YxG5J0dcm; __gads=ID=8d98b293e74de9d9:T=1645457018:S=ALNI_MZGlNMYsX_GlvZ-46AYU0wKcfNfBw; _ga=GA1.2.813661929.1645537045; _gcl_au=1.1.1389109368.1645537045; _cs_c=0; _fbp=fb.1.1645537046909.1733216053; _ym_d=1645537047; _ym_uid=1641914173296202124; DFID=web|P7zFqSxsOirICr7MJTAj; _rdt_uuid=1645537601809.c5db993b-574d-46f6-b541-f555f9896d7b; _scid=4b6c06ba-6c26-4dd6-a26a-4c7514f74b1c; al_cell=2022-2-18-wt-main-1-control; sbm_country=IN; _pbjs_userid_consent_data=3524755945110770; _pubcid=910a09f8-559e-4670-9c5d-01368b11c4dd; _lr_env_src_ats=false; pbjs-unifiedid=%7B%22TDID%22%3A%22e3072ade-92b7-46e8-bb8d-cd699ac531b3%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222022-01-22T14%3A02%3A16%22%7D; V=9f2ac16cc40bef0d5295a4f56c018d9762163059624dd4.24537432; chgcsdetaintoken=1; chgcsastoken=CsjAYEWWt6PYZ_o-wkDjbAIF5xQNTwBWGv_8xhoAeY9lnNBzA9UhSPFK-Qn46ySAsLwQRLEp_3AJfWLm8jwSxaLZQ7Z-Z3-Va3vot8XPh5rMfof9xtnYKXv78vVqC9tJ; usprivacy=1YNY; forterToken=6093569fde01495fb305f6a08e0cfdaa_1646755065413__UDF43_13ck; chgmfatoken=%5B%20%22account_sharing_mfa%22%20%3D%3E%201%2C%20%22user_uuid%22%20%3D%3E%20d52ab5a0-fcb8-4ec3-b002-13facc9dd263%2C%20%22created_date%22%20%3D%3E%202022-03-08T15%3A58%3A27.834Z%20%5D; id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImR6ZmJ6ZGY3NkBnbWFpbC5jb20iLCJpc3MiOiJodWIuY2hlZ2cuY29tIiwic3ViIjoiZDUyYWI1YTAtZmNiOC00ZWMzLWIwMDItMTNmYWNjOWRkMjYzIiwiYXVkIjoiQ0hHRyIsImlhdCI6MTY0Njc1NTE0NywiZXhwIjoxNjYyMzA3MTQ3LCJyZXBhY2tlcl9pZCI6ImFwdyJ9.ckTu0tIQz2JQZZAvBtlxBTq-XlGTvpEDjePYEtAXS-CYdzQdpkLjwRwxF0O0XbyrTv7O-1nfvDCtihmNGsFLF70hGnpjKNf2GsuarWOF2Wvv-4Lav5WTOpzoOExpNcpSO0tBtptQ8ntSNko8vYETI8UMiXhgy8vjI2lyKtU0oDW-i7ZdNQ41QrmqH3IBDMcyigjQmEh27u0FYOIbZpcLagWP5FwYJdYt1wlO-ruBKo05Vpv4PcDytpc7Od2qmij6B2mWRKTzymAkgziqHF4nneDiq8wOVaKYe2I_0hlY-ZMd04LZh_pzu2uA957bgl6Cyp43QNhw8NKl5uiuRAc3wQ; U=3ce47592a35e4609847aac4dcced63df; exp=A803B%7CC026A%7CA560B%7CA127D; expkey=1ABED2D9A3F077E5C93BB504FFBAD730; _vid_t=P7kjguEKoa7fiP2UZqXR88b6yjz+/5M+QusZ/LqiDiP6ff/tAvUfi2t5Il0WTjPaux1ZjrzHghIEug==; _sctr=1|1646677800000; opt-user-profile=9f2ac16cc40bef0d5295a4f56c018d9762163059624dd4.24537432%252C21052020077%253A21048420088; _sdsat_authState=Hard%20Logged%20In; PHPSESSID=6uq09kefia79kl7966qj8riv62; CSessionID=69e95bc2-2380-49e9-abef-c50036ce7492; SU=NNFMYgJaD7VFtTXrSY5dTmXhsRZ4H6_lSSx77UQULamnIUDqei47bMv0DTto9Ti7pRZksXgcuxWyKOFX3M5wcXjY6xRk-YUqrJnxdvvyrBPFcWu4I-XPoU_k-oRwJfbO; user_geo_location=%7B%22country_iso_code%22%3A%22IN%22%2C%22country_name%22%3A%22India%22%2C%22region%22%3A%22RJ%22%2C%22region_full%22%3A%22Rajasthan%22%2C%22city_name%22%3A%22Jodhpur%22%2C%22postal_code%22%3A%22342001%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-IN%22%2C%22hi-IN%22%2C%22gu-IN%22%2C%22kn-IN%22%2C%22kok-IN%22%2C%22mr-IN%22%2C%22sa-IN%22%2C%22ta-IN%22%2C%22te-IN%22%2C%22pa-IN%22%5D%7D%7D; CVID=169870cb-bef6-49c7-8268-8b4d573643a6; pxcts=c57385d5-a8eb-11ec-a1f1-574b49475047; _pxff_rf=1; _sdsat_cheggUserUUID=d52ab5a0-fcb8-4ec3-b002-13facc9dd263; OptanonConsent=consentId=cdeafacd-1beb-4358-9ed7-3723605f7850&datestamp=Mon+Mar+21+2022+13%3A21%3A31+GMT%2B0530+(India+Standard+Time)&version=6.18.0&interactionCount=1&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false; ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%226f1477ed-63df-e55e-1b18-662f31968892%22%2C%22c%22%3A1641902010716%2C%22l%22%3A1647849091656%7D; ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22d52ab5a0-fcb8-4ec3-b002-13facc9dd263%22%2C%22c%22%3A1646755146426%2C%22l%22%3A1647849091658%7D; CSID=1647849090611; _px3=1ce5f338aeee789e93f706a24ef91dac0f394ab8751f2bd76aaaebdd23b7f59c:EL2M5r+m2AzzWbOhZhcgTCOzm5UYPKpZ7gdAd1eeOoqLSryj4y2brR47OOV3CnKfDUAHWGOZ5FN+Lk22CDVOeQ==:1000:u9gVKC2qW/bVwjSQCXFnRnWXwkp+A3w4crTriMff8svQbLJgGqxtbRkZplJr2IZmwvtNJeDWPYafunMfoW3amRexzKUyRdXTx7udbnjTCag/Cxrvry9hwZcOReTb1FDPdePKEV30CrtT18sYtlwDZQb0GVAs6prJ+dhWG8YhLfj8Ork4ODdU8R0OBsFL4bhNv5YWBGRwYOveFi7azO5ZUA==; _px=EL2M5r+m2AzzWbOhZhcgTCOzm5UYPKpZ7gdAd1eeOoqLSryj4y2brR47OOV3CnKfDUAHWGOZ5FN+Lk22CDVOeQ==:1000:zdhYfYTSxnl4ZU2cNJZTuZHI9RGceaLvSDyjo1Kxn74Bp9rDpOZ2wwpjKFUtfX78JQMJ/G9DP2ocECjtGdd2S8VcE7Md85m2nGu3F0bKnuCiO+yTE+uHVQ7F3fC1YKNOf3kA+60EIMeeD6PdjTck8AMQi1fFIjbSp/xk4qHPdmQ5oQAmf49ihvuleyFR1GXVnA+LAjCxg74rebuygx5gBfmVgo4i53p0SB5eSBbvuuKpTCL9ctX1o5VGEavWdeRGOKdZuz+u07D27tTRwsLa3A==; local_fallback_mcid=72088619449400823167200658732452100511; s_ecid=MCMID|72088619449400823167200658732452100511; mcid=72141475282029839330538722462069057767; ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%2227c7b4bd-d686-becc-2933-4bb0e07dda3f%22%2C%22e%22%3A1647850896544%2C%22c%22%3A1647849091653%2C%22l%22%3A1647849096544%7D; _gid=GA1.2.1024460913.1647849097; _uetsid=bc415b40a8eb11eca66dbb62190468c2; _uetvid=1a79c48072d511ecaaebdb0eee95c6b7; schoolapi=null; IR_gbd=chegg.com; IR_14422=1647849097931%7C0%7C1647849097931%7C%7C; _tq_id.TV-8145726354-1.ad8a=a6cf34eff1a185ef.1645537047.0.1647849099..; _gat=1; _ym_isad=1; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22home%20page%22%5D%7D; _cs_id=f9ae0797-0783-a53b-89a6-fd7f25480b76.1645537052.6.1647849103.1647849103.1.1679701052346; _cs_s=1.0.0.1647850903587; _clck=1sfkio9|1|ezy|0; _clsk=1p3b3qt|1647849104581|1|0|d.clarity.ms/collect',
    
    'origin': 'https://www.chegg.com',
    'accept': 'application/json',
    'content-type': 'application/json',
    "cache-control": "max-age=0",
    "deviceFingerPrintId": "web|A0oUFYO50M5NYadliOz5"
}]



@client.message_handler(commands=['statues', 's'])
async def account_statues(message: types.Message):
    if message.chat.id == -1001179487467 :
        for i, item in enumerate(cookie_list):
            req = requests.get("https://www.chegg.com/homework-help/questions-and-answers/simulate-following-circuit-qucs-save-simulation-file-results-pdf-file-submit-e-learning-sh-q50117215?trackid=ef79e9639575&strackid=2b896ff805f6", headers=item)
            soup = BeautifulSoup(req.content, 'html.parser')
            qution = soup.find("div", {"class": "ugc-base question-body-text"}, 'html.parser')
            answer = soup.find("div", {"class": "answer-given-body ugc-base"}, 'html.parser')
            if answer == None:
                await message.reply(f"{i} account Notworking")
            else:
                await message.reply(f"{i} account is working")
    


def remove_tags(html):

    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
    soup.find("h2", {"class": "guidance-header"}).decompose()
    soup.find("section", {"id": "general-guidance"}).decompose()
    soup.find("div", {"id": "select-view"}).decompose()
    # return data by retrieving the tag content
    return soup



                
            
                                            
    


                

                
                   
                        
                    
@client.message_handler()
async def chegg(message: types.Message, amount=1):
    if message.chat.id == mainGroupId:
        if message.text.startswith("add"):
            if message.chat.id == -1001612479212:
                data = message.text.split(":", 3)
                userId = data[1]
                numberOfDays = data[2]
                await open_account(userId, numberOfDays, message)
                await message.reply(
                    f"user of id {userId} add succefully in database for {numberOfDays} days \n\n Thankyou")
            else:
                await message.reply(f"Danger You are not an adminstator and you are scamming me and my owner i am reporting you to my owner {Admin}")
                await bot.send_message(1195737015, f"Danger! Scamming add user \n\n USERDATA: \n\n UserName: @{message.from_user.username} \n\n USERID: {message.from_user.id}")

        if "https://www.chegg.com" in message.text:
            print("getting")
            user = str(message.from_user.id)
            u = collection.find_one({"userid": user})
            if u == None:
                await message.reply(
                    f"Sorry You are Not A premium mumber, \n\nPlease send message to {Admin} for premium subscription \n\n PRICE : only 150 rupee (or) 4$ per month \n\n unlimited solutions")
            else:
                Expdate = u['ExpDate']
                present = datetime.now()
                present_s = present.strftime("%d/%m/%Y")
                now = time.strptime(present_s, "%d/%m/%Y")
                exp = time.strptime(Expdate, "%d/%m/%Y")
                if now > exp:
                    await message.reply(f"Oh! Sorry to Say Your premium subscription just now expired. Please Contact {Admin} for renewal")
                    collection.find_one_and_delete({"userid": user})
                    return
                c_headers = random.choice(cookie_list)
                try:
                    if 'https://www.chegg.com' in message.text:
                        await bot.set_chat_permissions(mainGroupId, permissions=lock_permissions)
                        
                              
                        
                      
                        try:
                            if "questions-and-answers" in message.text:
                                req = requests.get(
                                    message.text, headers=c_headers)
                                soup = BeautifulSoup(
                                    req.content, 'html.parser')
                                if "An expert answer will be posted here" in str(soup):
                                    await message.reply ("This question don't have answer yet")
                                qution = soup.find(
                                    "div", {"class": "ugc-base question-body-text"}, 'html.parser')
                                answer = soup.find(
                                    "div", {"class": "answer-given-body ugc-base"}, 'html.parser')
                                
                                answer_by = soup.find_all(
                                    "span", {"class": "answerer-name"}, 'html.parser')
                                for tag in soup.select(".answer-given-body.ugc-base img"):
                                    if 'd2vlcm61l7u1fs.cloudfront.net' in tag['src']:
                                        tag["src"] = "https:" + tag["src"]
                                    
                                      
                                aid = str(req.content).split(
                                    'answerId="')[1].split('" >')[0]
                                print(aid) 
                                like_dislike = requests.post(
                                    'https://www.chegg.com/study/_ajax/contentfeedback/getreview?entityType=ANSWER&entityId=+{}'.format(aid), headers=c_headers)
                                like_soup = like_dislike.json()
                                l1 = (like_soup['review_count'])
                                l2 = (l1['result'])
                                if "0" in l2:
                                    like = (l2['0'])
                                    like_number = (like['count'])
                                else:
                                    like_number = 0
                                if "1" in l2:
                                    dislike = (l2['1'])
                                    dislike_number = (dislike['count'])
                                else:
                                    dislike_number = 0
                                main_html = '''
                                                            <!DOCTYPE html>
                                                            <html lang="en">
                                                            <head>
                                                                <meta charset="UTF-8" />
                                                                <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                                                                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                                                                    <!-- CSS only -->
                                                                   <link
                                                                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"
                                                                    rel="stylesheet"
                                                                    integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6"
                                                                    crossorigin="anonymous"
                                                                    />
                                                                    <title>Powered by Chegg Unblur By Naveen</title>
                                                                </head>
                                                                <style>
                                                                    .body {
                                                                    width: 100px;
                                                                    }
                                                                    .alert {
                                                                    text-align: center;
                                                                    }
                                                                    .qution_header{
                                                                    text-align: center;
                                                                    color: rgb(
                                                                        37, 70, 175);

                                                                    }
                                                                    img {

                                                                max-width: 100%;

                                                                }
                                                                .question{
                                                                    padding: 30px;
                                                                }
                                                                .answer{
                                                                    padding: 30px;
                                                                }
                                                                </style>
                                                                <body>
                                                                    <div class="alert alert-success" role="alert">
                                                                    Powered by Chegg Unblur By Naveen 
                                                                    </div>
                                                                </body>
                                                                <body>
                                                                    <div class="alert alert-danger" role="alert">
                                                                    THIS ANSWER LINK WILL EXPIRE IN 10 MIN
                                                                    </div>
                                                                </body>
                                                                </html>
                                                                '''
                                like_dislike_html = '''
                                                                <section >
                                                                    <div class="container my-3 bg-light">
                                                                    <div class="col-md-12 text-center">
                                                                    <button type="button" class="btn btn-primary">
                                                                        likes <span class="badge bg-secondary">{}</span>
                                                                    </button>
                                                                    <button type="button" class="btn btn-primary">
                                                                        dislikes <span class="badge bg-danger">{}</span>
                                                                    </button>
                                                                    </div>
                                                                </div>
                                                                </section>
                                                                '''
                                answer_given = '''
                                                                <section>
                                                                    <div class="card text-center">
                                                                        <div class="card-header">
                                                                        ANSWER GIVEN BY
                                                                        </div>
                                                                        <div class="card-body">
                                                                        <h5 class="card-title">{}</h5>
                                                                        </div>
                                                                        <div class="card-footer text-muted">
                                                                        Powered by Homework Hub server
                                                                        </div>
                                                                    </div>
                                                                </section>
                                                                '''
                                qution_html = '''
                                                                <section>
                                                                <div class="container my-5">
                                                                    <div
                                                                    class="row p-4 pb-0 pe-lg-0 pt-lg-5 align-items-center rounded-3 border shadow-lg"
                                                                    >
                                                                    <h1 class="qution_header">QUESTION</h1>
                                                                    <div class="question">
                                                                        {}
                                                                    </div>
                                                                    </div>
                                                                    </div>
                                                                </div>
                                                                </section>
                                                                '''
                                answer_html = '''
                                                                <section>
                                                                <div class="container my-5">
                                                                    <div
                                                                    class="row p-4 pb-0 pe-lg-0 pt-lg-5 align-items-center rounded-3 border shadow-lg"
                                                                    >
                                                                    <h1 class="qution_header">ANSWER</h1>
                                                                    <div class="answer">
                                                                        {}
                                                                    </div>
                                                                    </div>
                                                                    </div>
                                                                </div>
                                                                </section>
                                                                '''
                                file = open('Answer.html', 'w',
                                            encoding='utf-8')
                                file.write(str(main_html))
                                file.write(
                                    str(answer_given).format(answer_by))
                                file.write(str(like_dislike_html).format(
                                    like_number, dislike_number))
                                file.write(str(qution_html).format(qution))
                                file.write(str(answer_html).format(answer))
                                file.close()
                                # try:
                                #     url = "https://siasky.net/skynet/skyfile"
                                #     link_files = [
                                #         ('file', ("Answer.html", open(
                                #             './Answer.html', 'rb'), 'text/html'))
                                #     ]
                                #     headers7 = {
                                #         'referrer': 'https://siasky.net/'
                                #     }
                                #     response = requests.request(
                                #         "POST", url, headers=headers7, files=link_files)
                                #     limb = "https://siasky.net/" + \
                                #         response.json()["skylink"]
                                #     keyboard = inline_keyboard.InlineKeyboardMarkup(
                                #         row_width=3)
                                #     button = inline_keyboard.InlineKeyboardButton(
                                #         'Answer', url=limb)
                                #     keyboard.add(button)
                                #     await message.reply(f"✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢\n\n @{message.from_user.username or message.from_user.first_name} please click the below link and download \n\n ✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢", reply_markup=keyboard)
                                # except Exception as e:
                                #     print(e)
                                #     doc = open('Answer.html', 'rb')
                                #     # try:
                                #     #   await bot.send_document(message.from_user.id, doc)
                                #     # except:
                                #     #   await bot.send_document(message.chat.id, doc)
                                #     # await message.reply('dont send another question immediately check @freejaffawarrior ')
                                #     await bot.send_document(message.chat.id, doc, caption=f"✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢\n\n @{message.from_user.username or message.from_user.first_name} the above file is your answer please download \n\n ✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢")
                                doc = open('Answer.html', 'rb')
                                # try:
                                #   await bot.send_document(message.from_user.id, doc)
                                # except:
                                #   await bot.send_document(message.chat.id, doc)
                                # await message.reply('dont send another question immediately check @freejaffawarrior ')
                                await bot.send_document(message.chat.id, doc, caption=f"✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢\n\n @{message.from_user.username or message.from_user.first_name} the above file is your answer please download \n\nyour subscription expires on {Expdate}  \n\n✅🟢✅🟢✅🟢✅🟢✅🟢✅🟢")

                            wait_time = random.randint(60, 120)
                            #wait_time = 60
                            sent = await bot.send_message(message.chat.id, f'Ok.! i will take rest for \n ⏱ {wait_time} sec Uh..😴 ')
                            await asyncio.sleep(wait_time)
                            await bot.edit_message_text('Now i am ready.', message.chat.id, sent.message_id)
                            await bot.set_chat_permissions(mainGroupId, permissions=unlock_permissions)
                        except Exception as e:
                            print(e)
                            await bot.set_chat_permissions(mainGroupId, permissions=unlock_permissions)
                            # await message.reply('your qustion dont have answer or maybe you send a wrong qustion')
                            # await bot.send_message(-1001468490071,f"@{message.from_user.username or message.from_user.first_name}'s question dont have answer or send wrong question , Now another person can ask me solution")
                            await message.reply('🛑❌🛑❌🛑❌🛑❌🛑❌\n\nYour qustion dont have answer or maybe you send a wrong link\n\n🛑❌🛑❌🛑❌🛑❌🛑❌')

                    else:
                        pass
                except Exception as e:
                    print(e)
                    pass
        else:
            allow_ids = [-528128941, adminId, 1462786490]
            if message.from_user.id in allow_ids:
                return
            else:
                m = '''🛑❌🛑❌🛑❌🛑❌🛑❌\n\nplease send only chegg links here\n\n🛑❌🛑❌🛑❌🛑❌🛑❌'''
                send = await message.reply(m)
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                await bot.delete_message(chat_id=message.chat.id, message_id=send.message_id)
    else:
        m = '''🛑❌🛑❌🛑❌🛑❌🛑❌\n\nplease use premium group for chegg answers.\n\nBut here you can check your validity using /mydata\n\nAnd you can redeem your token also here by /redeem <token>\n\n🛑❌🛑❌🛑❌🛑❌🛑❌'''
        await message.reply(m)


if __name__ == '__main__':
    executor.start_polling(client, skip_updates=True)
