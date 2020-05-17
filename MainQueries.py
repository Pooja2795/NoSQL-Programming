from pymongo import MongoClient
from py2neo import Graph
import secrets

#Connection to Mongo database 
try:
    conn = MongoClient()
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

#connection to neo4j database
graph = Graph(host='localhost', port=7687, password="1234")

#Giving options to user and taking input form them   
print("Enter which option you want to choose: ")
print("New Customer? Please type Yes ")
print("Do you want to login? Please type Login ")
 
new_user = input("Enter your option here: ")


#Registration for New customer  
def new_regis():
    db = conn.Music
    collection = db.new_login
 
    new_User_Name = input("Enter Your User_Name: ")
    new_Password = input("Enter Your Password: ")
    new_First_Name = input("Enter Your First_Name: ")
    new_Last_Name = input("Enter Your Last_Name: ")
    new_Email_id =input("Enter Your Email Address: ")
    new_Phone_Number =input("Enter Your Phone_Number: ")
    new_Date_of_Birth =input("Enter Your Date_of_Birth: ")
    new_Place_of_Birth =input("Enter Your Place_of_Birth: ")
    referral_code = input("Do you have referal code? If yes please type Yes:") 

    #If user has referral code 
    if referral_code == "Yes":
        db = conn.Music
        collection_regis = db.new_login
        collection_rew = db.rewards

        refer_id = input("Enter your refer id please: ")
        refer_data = collection_rew.find_one({"referred_with_code": refer_id}, {"referred_with_code":1 ,"_id": 0})
        print(refer_data)
        referred_by_user = input("Enter the user name who referred you: ")

        if refer_data["user_name"] == referred_by_user:
            collection.insert_many(
        [
            {
            "new_UserName" : new_User_Name,
            "new_Password" : new_Password, 
            "new_First_Name" : new_First_Name,
            "new_Last_Name" : new_Last_Name,
            "new_Email_id" : new_Email_id,
            "new_Phone_Number" : new_Phone_Number,
            "new_Date_of_Birth" : new_Date_of_Birth,
            "new_Place_of_Birth" : new_Place_of_Birth,  
            },
        ]
        )
            db = conn.Music     
            collection = db.rewards
            document1 = {
            "user_name":new_User_Name,
            "cash_earned":50,
            "referred_by_code": refer_id
             }
            collection.insert_one(document1)
            print("VERIFIED!!! and also earned cashpoints. ")
        else:
            print("Wrong username. Sorry!")

    #If user does not have referral code
    else:
        collection.insert_many(
        [
        {
            "new_UserName" : new_User_Name,
            "new_Password" : new_Password,
            "new_First_Name" : new_First_Name, 
            "new_Last_Name" : new_Last_Name,
            "new_Email_id" : new_Email_id,
            "new_Phone_Number" : new_Phone_Number,
            "new_Date_of_Birth" : new_Date_of_Birth,
            "new_Place_of_Birth" : new_Place_of_Birth
            },
            ]
            )
        print("You have not earned cash points but your account has been created")
#---------------------------------------------------------------------------------------------------------
# Display all menu options to user and take input from them
def all_menu():
    print("Login successful!!!")
    print("1.Enter this option if you want to listen the top songs from different artists")
    print("2.Enter this option if you want to recommend a song")
    print("3.Refer to your friend and earn some cash points")
    print("4.Search")
    print("5.Create your own playlist")
    print("6.Total cash earned:")
    opt = input("Enter which option you want to choose:")
    if opt ==  "1":
      top_song()
    elif opt == "2":
      getuserdata()
    elif opt== "3":
      reward_code() 
    elif opt== "4":
      search() 
    elif opt== "5":
      create_playlist()
    elif opt== "6":
      total_cash()
    else:
      print("wrong entry")
#----------------------------------------------------------------------------------------------------------           
#Login page if user is not a new customer
login_username = ""

def login_opt():     
   db = conn.Music
   collection1= db.new_login  
   global login_username
   login_username = input("Enter your username: ")
   login_password = input("Enter your password: ")

    #Query for checking the password of the given username provided by user
   cust_password =  collection1.find_one({ 'new_UserName': login_username }, {'_id': 0, 'new_Password' : 1})  
   

   if login_password == cust_password ['new_Password']:
       all_menu()
   else:
       print("Invalid username and password!")

#--------------------------------------------------------------------------------------------------------------
#Provide top songs to user of the given artist
def top_song():
    artist_name = input("Enter which artist songs you want to listen: ")

    query = """ match(a:tracks)-[x:sungBy]->(b:artists{a_name:\"""" + artist_name + """\"})
    where a.rating >= 3
    return a.t_name
    """
    result = graph.run(query).data()

    songs = []

    #List of all the songs of the given artist
    for x in result:
        songs.append(x['a.t_name'])
    songs = list(set(songs))
    print(songs)   

#-------------------------------------------------------------------------------------------------------------
def reward_code():
    
    #Generate random code for reward
    random_code = secrets.token_hex(3)
    
    print(random_code)
    db = conn.Music     
    collection = db.rewards
    
    document1 = {
        "user_name":login_username,
        "cash_earned":100,
        "referred_with_code": random_code
        }
    collection.insert_one(document1)
    print("referred sucessfully")
#--------------------------------------------------------------------------------------------------------------
def search():
    print("Please enter what you want to search")
    s = input("")

    #Return the artist name of the song that user searched
    query = """match(a:tracks{t_name:\""""+ s + """\"})-[x:sungBy]->(b:artists)
    return b.a_name
    """
    result2 = graph.run(query).data()
    print(result2)

    query = """match(a:tracks{t_name:\""""+ s + """\"})
    return a.t_name
    """
    result3 = graph.run(query).data()

    #Creates relationship between song and user if they want to like it
    for s in result3:
        print("Do you want to like this song")
        like = input("")

        if like == "yes":
            query = """ match(u:user{username:\"""" + login_username + """\"})
            match(s:tracks{t_name:\"""" + s['a.t_name'] + """\"})
            merge(u)-[h:likes]->(s)
            """
            graph.run(query)
            print("song liked")
        elif like == "no":
            print("enjoy the music")

#---------------------------------------------------------------------------------------------------------------
#Creates playlist and add the songs that user provided via input
def create_playlist():
    print("please enter playlist name : ")
    playlist_name = input("")

    query = """match(u:user{username:\"""" + login_username + """\"})
    merge(p:playlists{p_name:\"""" + playlist_name + """\"})
    merge(u)-[:has]->(p)
    """
    graph.run(query)
    print("Please type a song you want to add in your playlist : ")
    song_name = input("")

    query = """match(a:tracks{t_name:\""""+ song_name + """\"})
    return a.t_name
    """
    
    result = graph.run(query).data()
    

    for song_name in result:
        query = """match(q:playlists{p_name:\"""" + playlist_name + """\"}) 
        match(s:tracks{t_name:\"""" + song_name['a.t_name'] + """\"}) 
        merge(s)-[:belongsTo]->(q)
        """
        graph.run(query)
        print("song added successfully :)")

#-----------------------------------------------------------------------------------------------------------------
def total_cash():
    
    db = conn.Music
    collection = db.rewards
    
    #It sums up the cash earned point if user has referred any of his friends
    pipeline = [{"$match":{"user_name": login_username}},{"$group": {"_id": None, "sum": {"$sum":"$cash_earned"}}},
                {"$project":{"_id":0 ,"sum":1}}
               ]
    doc = collection.aggregate(pipeline)
    print(doc)
    for x in doc:
        print(x['sum'])
    print(login_username) 

#------------------------------------------------------------------------------------------------------------------
def getuserdata():
  
#connection to neo4j database
    graph = Graph(host='localhost', port=7687, password="1234")

#Asking for recommendation
    print("Do you want to recommend a song to your friend?")
    user = input("")

#list of friends user follows
    if user == "yes":
        query = """
        match(u:user{username:\"""" + login_username + """\"})-[x:follows]->(a:user)
        return a.username
        """
        result = graph.run(query).data()

#variable for storing user's friends data
        user_name = []

        for x in result:
            user_name.append(x["a.username"])
        user_name = list(set(user_name))
        print(user_name)
    
#selecting a friend from the list
        print("Choose a friend you want to recommend a song")
        friend = input("")
    
#list of songs user likes
        if friend in user_name:
            print("Choose a song that you want to recommend")
            query = """
            match(u:user{username:\"""" + login_username + """\"})-[c:likes]->(t:tracks)
            return t.t_name
            """
            result = graph.run(query).data()

#variable to store list of songs
            songs = []
            for y in result:
                songs.append(y["t.t_name"])
            songs = list(set(songs))
            print(songs)

#selecting a song to recommend
            print("select a song")
            song = input("")

            if song in songs:
                query = """
                match(b:user{username: \"""" + friend + """\"}),(s:tracks)
                where s.t_name = \"""" + song + """\"
                merge (b) -[x:recommended {recommendedBy:\"""" + login_username + """\"}]-> (s)
                """
                result = graph.run(query)
                print("Song recommended")
        
        else: 
            print("user not found")

#list of songs user has recommended
    elif user == "no":
        print("Do you want to see which songs you recommended?")
        recommend = input("")

#list of friends of user
        if recommend == "yes":
            print("Select a user")
            query = """
            match(u:user{username:\"""" + login_username + """\"})-[x:follows]->(a:user)
            return a.username
            """
            result = graph.run(query).data()

#variable to store list of user's friends
            u_name = []

            for z in result:
                u_name.append(z["a.username"])
            u_name = list(set(u_name))
            print(u_name)

            user = input("")
#songs recommended by the user
            if user in u_name:
                query = """
                match (u:user{username:\"""" + user + """\"}) -[x:recommended]-> (s:tracks)
                where x.recommendedBy = \"""" + login_username + """\"
                return s.t_name
                """
                result = graph.run(query).data()

#variable to store the songs
                tracks = []

                for x in result:
                    tracks.append(x["s.t_name"])
                tracks = list(set(tracks))
                print(tracks)

#song recommended to which users
        elif recommend == "no":
            print("Do you want to see a particular song recommended to which users")
            users = input("")

#list of tracks user likes
            if users == "yes":
                print("select a song")
                query = """
                match(u:user{username:\"""" + login_username + """\"})-[c:likes]->(t:tracks)
                return t.t_name
                """
                result = graph.run(query).data()
#variable to store tracks
                track = []

                for x in result:
                    track.append(x["t.t_name"])
                track = list(set(track))
                print(track)

                tr = input("")

#track recommended to which users
                if tr in track:
                    query = """
                    match (u:user) -[x:recommended]-> (s:tracks{t_name:\"""" + tr + """\"})
                    where x.recommendedBy = \"""" + login_username + """\"
                    return u.username
                    """
                    result = graph.run(query).data()

#variable to store the list of users
                    user_data = []

                    for y in result:
                        user_data.append(y["u.username"])
                    user_data = list(set(user_data))
                    print("This song is recommended to :", user_data)
        
            elif users == "no":
                print("enjoy the music")
#-----------------------------------------------------------------------------------------------------------------    
if new_user == "Yes":
    new_regis()
elif new_user == "Login":
    login_opt()
   
else:
    print("Please enter proper input and try again")