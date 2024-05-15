import os
import random
import json
import requests
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from sqlalchemy.orm import sessionmaker
from sqlalchemyDemo import Restaurant,User,Comment, create_session
from flask import (Flask, redirect, render_template, request,abort,abort,
                   send_from_directory, url_for)
                   
              

app = Flask(__name__)
configuration = Configuration(access_token='XfzHRWhMKq91u9q3GFuZnPO/6XsShMHsPr/Nq6L7xZisYVykyB7uwJs+1J2k+wNNcLihTG97Kqifx87tk6zK9sA74URAovG4/7SKqzYMUU7NFWBC92xhwn8MKgja41b5RDuPX1EHw2OqRsOI1F2RmgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d5a1470caf781756d47690619aeb30e8')

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
        
    return 'OK'
    
#@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )
    
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message2(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message = event.message.text;
        userId = event.source.user_id
        userProfile = line_bot_api.get_profile(userId)
        userName = userProfile.display_name
        # user_id = userProfile.user_id
        # status_message = userProfile.status_message
        # language = userProfile.language
        # picture_url = userProfile.picture_url

        #限制指令開頭為#，避免一般對話
        if(len(message) == 0 or  message[0] != "#"):
            return {}

        #文字加工(去左右空白後 切空白) ， 分指令(第一個字串去掉#小寫) 及 參數(第一個以外非空白元素)
        r = message.strip().split(r' ')
        command = r[0][1::].strip().lower()
        args = list(filter(lambda ent:ent.strip()!='',r[1::]))
        response = "系統錯誤"

        print("command : ",command)
        print("args : ",args)

        try:
            session = create_session()
            ### 新增資料 ###
            if  command in ['insert','新增'] :                
                insertRestaurant(session,args,userName)
                response = f"已新增 {len(args)} 筆資料 ： {args}"

            ### 查詢全部 ###
            elif command in ['queryall','查詢全部'] :               
                result = queryRestaurant(session)
                if len(result)==0:
                    response = "查無結果"
                else:
                    resultStr = '\n'.join(list(map(lambda rest: f"""{rest.id} ， {rest.name}""",result)))
                    response = f"查詢結果 : \nID，Name\n{resultStr}"
                # result = map((lambda ent: str(ent[0]) + ". " + ent[1]),queryRestaurant(conn))
                # resultstr = '\n'.join(list(result))
                

            ### 刪除全部 ###
            elif command in ['deleteall','刪除全部'] :               
                deleteall(session)
                response = "餐廳資料已全數刪除"

            ### 刪除單筆 ###
            elif command in 'delete' :     
                result = delete(session,args)    
                resultstr = '\n'.join(result) 
                response = f"已刪除 {len(result)} 筆資料 ： \n{resultstr}"     
                # result = map((lambda ent: str(ent[0])),delete(session,args))
                # #TODO 還需要調整輸出格式
                # resultstr = '\n'.join(list(result))
                # response = f"已刪除 {len(result)} 筆資料 ： \n {resultstr}"

            ### 隨機一筆 ###
            elif command in ['random','吃什麼','吃甚麼'] :               
                result = queryRestaurant(session)
                randomNum = random.randint(0, len(result)-1)
                restaurant = result[randomNum]
                comments= queryComment(session,restaurant.name)
                if len(comments) > 0 :
                    commentsStr = "\n\n".join(list(map(lambda c:f"""{c.user_name} 【{c.score}分】 : {c.comment}""",comments)))
                    response = f"""餐廳名稱 : {restaurant.name}\n\n評論 : \n{commentsStr}"""
                else:
                    response = f"""餐廳名稱 : {restaurant.name}\n\n評論 : 查無評論"""
                # response = str(result[random.randint(0, len(result)-1)][1])
           
            ### 查詢使用者 ###
            elif command in ['queryuser','查詢使用者']:
                result = queryUser(session,args)
                if len(result)==0:
                    response = "查無結果"
                else:
                    response = "ID，Name\n"+'\n'.join(list(map(lambda rest: f"""{rest.id} ， {rest.name}""",result)))
                            ### 查詢使用者 ###
            elif command in ['comment','評論']:
                restaurantName = args[0]
                score = args[1]
                if len(args) == 2 :
                    comment = "不予置評"
                else:
                    comment = args[2]
                insertComment(session,userName,restaurantName,comment,score)
                response = "感謝評論"
            elif command in ['nba']:
                response = getNBA()
            else:
                response = "查無指令"
                
        except Exception as e:
            print(str(e))

        finally:
            session.close()          
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )
        
    response = jsonify(success=True)         
    response.status_code = 200   
    return response

def insertRestaurant(session,names,userName):
    for restName in names:
        session.add(Restaurant(name=restName,create_name=userName))   
    if(len(queryUser(session,[])) == 0):
        insertUser(session,userName)
    
    session.commit()
    # for name in names:
    #     SQL_INSERT = f'''
    #         INSERT INTO RESTAURANT(name) VALUES('{name}')
    #     '''
    #     conn.execute(SQL_INSERT)
    # conn.commit()

def queryUser(session,agrs):
    print(len(agrs))
    if len(agrs) == 0 :
        return session.query(User).all()
    else:
        return session.query(User).filter(User.name in agrs).all()

def insertUser(session,userName):
    session.add(User(name=userName))

def queryRestaurant(session):
    return session.query(Restaurant).all()
    # SQL_QUERYALL = f'''
    #     SELECT id,name FROM RESTAURANT
    # '''   
    # cur = conn.cursor()
    # cur.execute(SQL_QUERYALL)
    # rows = cur.fetchall()
    # return rows

def queryRestaurantByName(session,name):
    return session.query(Restaurant).filter(Restaurant.name == name).first()

def queryRestaurantById(session,id):
    return session.query(Restaurant).filter(Restaurant.id == id).first()

def deleteall(session):
    restaurants = queryRestaurant(session)
    session.delete(restaurants)
    session.commit()
    # SQL_DELETEALL = '''
    #     DELETE FROM RESTAURANT
    # '''
    # conn.execute(SQL_DELETEALL)
    # conn.commit()

def delete(session,nameOrIds): 
    result = []
    for nameOrId in nameOrIds:
        if nameOrId == None:
            restaurants = queryRestaurant(session) 
            result.append(list(map(lambda r:r.name,restaurants)))  
            session.delete(restaurants)         
        elif str(nameOrId).isnumeric():
            restaurant = queryRestaurantById(session,nameOrId)
            result.append(restaurant.name)
            session.delete(restaurant)
        else:    
            restaurant = queryRestaurantByName(session,nameOrId)
            result.append(restaurant.name)
            session.delete(restaurant)
    session.commit()
    return result
    # result = []  
    # cur = conn.cursor() 
    # for nameOrId in nameOrIds:
    #     if nameOrId == None:
    #         SQL_QUERY = f'''
    #             SELECT name FROM RESTAURANT
    #         '''
    #         SQL_DELETE = f'''
    #             DELETE FROM RESTAURANT'
    #         '''
    #     elif str(nameOrId).isnumeric():
    #         SQL_QUERY = f'''
    #              SELECT name FROM RESTAURANT where id = '{nameOrId}'
    #         '''
    #         SQL_DELETE = f'''
    #             DELETE FROM RESTAURANT where id = '{nameOrId}'
    #         '''
    #     else:
    #         SQL_QUERY = f'''
    #              SELECT name FROM RESTAURANT where name = '{nameOrId}'
    #         '''
    #         SQL_DELETE = f'''
    #             DELETE FROM RESTAURANT where name = '{nameOrId}'
    #         '''
    #     cur.execute(SQL_QUERY)
    #     rows = cur.fetchall()
    #     result.append(rows)
    #     conn.execute(SQL_DELETE)
    #     conn.commit()
    # return result

def queryComment(session,restName):
    return session.query(Comment).filter(Comment.restaurantName==restName).all()

def insertComment(session,userName,restName,com,sc):
    session.add(Comment(user_name=userName,restaurantName=restName,comment=com,score=sc))
    session.commit()
    
def getNBA():
    response = requests.get('https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json')
    result = ''
    json = response.json()
    for game in json['scoreboard']['games']:
        result =  result + ' 比賽 : ' + str(game['seriesText']) + '\n'
        result =  result + ' 主隊 : ' + str(game['homeTeam']['teamTricode'])+ '\n'
        result =  result + ' 分數 : ' + str(game['homeTeam']['score'])+ '\n'
        result =  result + ' 客隊 : ' + str(game['awayTeam']['teamTricode'])+ '\n'
        result =  result + ' 分數 : ' + str(game['awayTeam']['score']) + '\n\n'
    return result

if __name__ == '__main__':
   app.run()
