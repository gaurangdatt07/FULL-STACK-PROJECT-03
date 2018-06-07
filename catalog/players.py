from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Club, Base, Player, User

engine = create_engine('sqlite:///clubinfo.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


User1 = User(name="Gaurang datt", email="gaurangdatt07@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


club1 = Club(name='Real Madrid')

session.add(club1)
session.commit()

player1 = Player(
    name="Keylor Navas", description="The keeper from costa rica ",jersey="1",
                 position="GoalKeeper", club=club1)
session.add(player1)
session.commit()

player2 = Player(
    name="Sergio Ramos", description="A true leader of LOS BLANOCS",
    jersey="4", position="CenterBack", club=club1)

session.add(player2)
session.commit()

player3 = Player(
    name="Marcelo", description=
    " A great player with unparalleled passion for this game",
    jersey="12", position="FullBack", club=club1)

session.add(player3)
session.commit()

player4= Player(
    name="Luka Modic",
    description="A true magician, a composed player and a great passer of the ball",
    jersey="10", position="Midfielder", club=club1)

session.add(player4)
session.commit()

player5 = Player(
    name="Cristiano Ronaldo",
    description="The Best player in this business right now, A true goal scoring machine",
                 jersey="7", position="Striker", club=club1)

session.add(player5)
session.commit()

#Players of Fc Barcelona

club2 = Club(name="Fc Barcelona")

session.add(club2)
session.commit()

player1 = Player(name="Ter stegen",
                 description=
                 "The german keeper who is a great shot stopper and good dribbler with the ball too",
                 jersey="1", position="GoalKeeper", club=club2)
session.add(player1)
session.commit()

player2 = Player(name = "Pique",
                 description="Spain defender with a great areal ability",
                 jersey ="3", position="CenterBack", club=club2)

session.add(player2)
session.commit()

player3 = Player(
                name = "Jordi Alba",
                 description= 
                "He covers the field like no other player, Speed demon this guy is a true engine to have",
                 jersey="18", position="FullBack", club=club2)
session.add(player3)
session.commit()

player4= Player(name="Iniesta",
                description="One of the best midfielders ever, his dribbling,technique is unparalleled",
                jersey="8", position="Midfielder", club=club2)

session.add(player4)
session.commit()

player5 = Player(name = "Messi",
                 description=
                 "Words are less to describe this player.A true genius , anything anyone can do he can do it better",
                 jersey="10", position="Striker", club=club2)
session.add(player5)
session.commit()

#Players of PSG

club3 = Club(name="Paris Saint-Germain")
session.add(club3)
session.commit()
player1 = Player(
                name="kevin Trapp" ,
                 description ="This young german goalkeeper has a great potentiol to be a great player",
                 jersey="1", position="GoalKeeper", club=club3)
session.add(player1)
session.commit()


player2 = Player(name = "Thiago Silva " ,
                 description =
                 "Brazil defender and a true leader.This guy leads not only this club but also his country.",
                 jersey="2", position="CenterBack", club=club3)

session.add(player2)
session.commit()

player3=Player(
    name="Dani Alves", description= "A fullback who is not just a great defender but also can attack on the break,what else do you want from a player.",
                 jersey="32", position="FullBack", club=club3)
session.add(player3)
session.commit()

player4 = Player(name="Angel Di Maria",
                 description=
                 "This argentine has got to potentiol to break an ankle with his dribbling",
                 jersey="11", position="MidFielder", club=club3)
session.add(player4)
session.commit()

print " Players added !!\n Squad is ready Gaffer"
