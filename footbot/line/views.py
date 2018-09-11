# -*- coding:utf-8 -*-

import logging
import datetime
import requests
import json
import random

from django.conf import settings
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseForbidden)

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from linebot import (LineBotApi,
                     WebhookParser,
                     WebhookHandler)
from linebot.models import (MessageEvent,
                            TextMessage,
                            TextSendMessage,
                            StickerMessage,
                            StickerSendMessage)
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from footbot.utils.load_conf import load_conf, write_conf

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

CWB_API_KEY = settings.CWB_API_KEY
VERSION = 'parser'

TAIWAN_FCST = "F-D0047-093"
TAIPEI_ID = "F-D0047-061"
NEW_TAIPEI_ID = "F-D0047-069"

logger = logging.getLogger('testlogger')


def index(request):
    return render(request, "line/index.html", {})


@csrf_exempt
def callback(request):
    logger.info(request)
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            if VERSION == "parser":
                events = parser.parse(body, signature)
                parse_events(events)

            elif VERSION == "handler":
                handler.handle(body, signature)

        except InvalidSignatureError as e:
            logger.error(e, e.message)
            return HttpResponseForbidden()
        except LineBotApiError as e:
            logger.error(e, e.message)
            return HttpResponseBadRequest()

        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def parse_events(events):
    for event in events:
        logger.info(event)

        is_msg_event = isinstance(event, MessageEvent) and isinstance(event.message, TextMessage)
        is_sticker_event = isinstance(event, MessageEvent) and isinstance(event.message, StickerMessage)

        if is_msg_event:
            handle_text_message(event)
        elif is_sticker_event:
            handle_sticker_message(event)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if u"天氣" in event.message.text:
        location = event.message.text.replace("天氣", "").strip()
        location = "大安區" if location == "" else location
        now_weather(event, location)

    elif u"@footbot" in event.message.text:
        message = event.message.text.replace(u"@footbot", "").strip()

        shutup_text = [u"閉嘴", u"安靜"]
        speak_text = [u"說話", u"講話"]
        help_text = [u"help", u"說明"]

        if u'開團' in message:
            field = message.replace("開團", "").strip()
            field = "台科大" if field == "" else field
            open_new_game(event, field)
            return

        elif [text for text in help_text if text == message]:
            help_info = ("footbot為一個很簡單的對話機器人，他主要功能為以下三點：\n"
                         "- 踢球開團: \n"
                         "    說明: 自動開團功能，預設為台科平地團\n"
                         "    指令: '@footbot 開團 [option]'\n"
                         "    範例 1: 輸入'@footbot 開團' -> footbot 會自動開啟台科平地團\n" 
                         "    範例 2: 輸入'@footbot 開團 福和橋' -> footbot 會自動開啟福和橋下平地團\n\n"
                         "- 天氣預報: \n"
                         "    說明: 抓大台北地區的三小時天氣預報功能，預設為大安區\n"
                         "    指令: '天氣 [option]'\n"
                         "    範例 1: 輸入'天氣' -> footbot 會去抓大安區最近三小時內的預報\n" 
                         "    範例 2: 輸入'天氣 永和區' -> footbot 會去抓永和區最近三小時內的預報\n\n" 
                         "- echo: \n"
                         "    說明: 讓footbot變成回聲機器人，預設為關閉\n"
                         "    指令: '@footbot [說話/講話/安靜/閉嘴]'\n"
                         "    範例 1: 輸入:'@footbot 說話' -> footbot會啟動echo功能\n"
                         "    範例 2: 輸入:'@footbot 閉嘴' -> footbot會關閉echo功能\n\n"
                         "- 使用說明: \n"
                         "    說明: 顯示使用說明\n"
                         "    指令: '@footbot [help/說明]'\n"
                         "    範例 1: 輸入:'@footbot help' -> footbot顯示使用說明\n"
                         )
            reply(event.reply_token, help_info)

        elif [text for text in shutup_text if text == message]:
            set_echo(False)
            cring_stickers = [8, 9, 16, 21, 111, 113, 123, 131, 135, 403]
            sticker = StickerSendMessage(package_id=1,
                                         sticker_id=random.choice(cring_stickers))
            line_bot_api.reply_message(event.reply_token, sticker)

        elif [text for text in speak_text if text == message]:
            set_echo(True)
            happy_stickers = [2, 4, 10, 13, 16, 106, 114, 132, 137, 138]
            sticker = StickerSendMessage(package_id=1,
                                         sticker_id=random.choice(happy_stickers))
            line_bot_api.reply_message(event.reply_token, sticker)

    elif load_conf('bot.conf', "ECHO"):
        reply(event.reply_token, event.message.text)


def set_echo(toggle):
    write_conf('bot.conf', "ECHO", toggle)
    logger.info(load_conf('bot.conf', "ECHO"))


def get_game_day(weekday=3):
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    return get_next_weekday(today, weekday)


def get_game_day_weather_info():
    try:
        game_day = get_game_day(3)
        game_day = game_day.replace(hour=18, minute=0, second=0)

        return get_weather_info(game_day, location="大安區",
                                default_info="目前查無{gd}晚上的大安區天氣預報".format(gd=game_day.strftime("%a")))
    except:
        return ""

def open_new_game(event, field, local='zhtw'):
    game_day = get_game_day(3)

    if local == 'zhtw':

        field_zhtw = "台科大平地足球場"

        if field == "福和橋":
            field_zhtw = "福和橋下永和端平地場"

        logger.info(field)

        game_msg = ("【練球團】{game_day} \n" +
                    field_zhtw + " \n\n"
                    "今晚10:30前有4人以上成團，明晚如下雨則取消，請盡量帶球，能到的請回+1，謝謝 \n\n"
                    ).format(game_day=game_day.strftime("%m/%d 19:30-22:00"))

    else:
        field_enus = "on NTUST hard ground football field"

        if field == "福和橋":
            field_enus = "on hard ground football field under FuHo bridge (Yonghe)"

        logger.info(field)

        game_msg = ("【It's Football Time】{game_day} \n" +
                    field_enus + " \n\n"
                                 "It might rain tmr, but we'll still do a headcount first. "
                                 "If u can come, please reply '+1', thx! "
                                 "If less than 4 people reply '+1' before 10:30pm tonight, the game'll be canceled. \n"
                    ).format(game_day=game_day.strftime("%m/%d 19:30-22:00"))

    weather_info = get_game_day_weather_info()

    reply(event.reply_token, game_msg + weather_info)


def now_weather(event, location):

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    info = get_weather_info(now, location,
                            default_info="目前查無" + location + "天氣")

    reply(event.reply_token, info)


def fetch_forecast(location="大安區"):
    logger.info("get cwb weather forecast")
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/{data_id}"

    try:
        params = dict(Authorization=CWB_API_KEY, locationId=",".join([TAIPEI_ID, NEW_TAIPEI_ID]),
                      locationName=location,
                      format="json", elementName="WeatherDescription")

        req = requests.get(url.format(data_id=TAIWAN_FCST), params=params, verify=False)
        context = json.loads(req.text)

        fcst = None
        for county_fcst in context["records"]["locations"]:
            fcst = next(iter(county_fcst["location"] or []), None)

            if fcst is not None:
                break

        return fcst["weatherElement"] if fcst else None

    except Exception:
        return None


def get_weather_info(target_dt, location="大安區", default_info="目前查無大安區天氣"):
    weather_elems = fetch_forecast(location)
    weather_info = default_info

    if weather_elems is not None:
        first_fcst_time = None
        logger.info("parsing api request")
        for we in weather_elems:
            if not we["elementName"] == "WeatherDescription":
                continue

            for fcst in we["time"]:
                start_time = datetime.datetime.strptime(fcst["startTime"], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(fcst["endTime"], "%Y-%m-%d %H:%M:%S")
                element_value = fcst["elementValue"]

                if len(element_value):
                    weather_desc = element_value[0]['value']
                else:
                    continue

                logger.info(weather_desc)

                # 抓目標時間的1.5小時內預報
                # 例如...1/1 10:00 抓 09:00 ~ 12:00, 1/1 11:30 抓 12:00 ~ 15:00
                delta = target_dt - start_time
                if first_fcst_time is None and abs(delta.days * 24 * 3600 + delta.seconds) <= 4800:

                    first_fcst_time = start_time
                    weather_info = (u"3小時天氣預報 - 預報時間：\n" +
                                    start_time.strftime("%m/%d %H:%M") + " ~ " +
                                    end_time.strftime("%H:%M") + "\n" +
                                    location + u"天氣概況：\n" +
                                    weather_desc)

        logger.info("parsed api request success")
    return weather_info


def get_next_weekday(dt, wd):
    weekday = dt.isoweekday()
    delta_wd = wd - weekday

    if delta_wd < 0:
        delta_wd += 7

    return dt + datetime.timedelta(days=delta_wd)


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # Bot can echo official sticker.
    if event.message.package_id in [str(i) for i in range(1, 5)]:
        line_bot_api.reply_message(event.reply_token,
                                   StickerSendMessage(package_id=event.message.package_id,
                                                      sticker_id=event.message.sticker_id))


@handler.default()
def default(event):
    logger.info(event)

    reply(event.reply_token, 'Currently Not Support None Text Message')


def reply(token, message):
    line_bot_api.reply_message(token, TextSendMessage(text=message))
