import pyxel
import random
import math
from enum import Enum

class App: #ゲーム全体の司令塔
    def __init__(self):
        pyxel.init(256, 256, caption="SIMPLE TOWER DEFENSE", scale="3", fps="60")
        pyxel.load("my_resource.pyxres") #リソースファイルをロード
        #pyxel.mouse(True)
        pyxel.sound(0).set(note='C2', tone="S", volume='3', effect='N', speed=3) #タワー購入
        pyxel.sound(1).set(note='A1', tone="S", volume='3', effect='N', speed=3) #購入負可
        pyxel.sound(2).set(note='C1RA0RF0RE0', tone="S", volume='3', effect='N', speed=3) #味方ダメージ
        pyxel.sound(3).set(note='C3RD3RE3RF3R D3RE3RF3RG3R E3RF3RG3RA3', tone="T", volume='3', effect='N', speed=3) #Levelup
        pyxel.sound(4).set(note="C1RE1", tone="P", volume="2", effect="F", speed=2)
        pyxel.sound(5).set(note="C1RE1RC1RE1R C1RG1RC1RG1R", tone="P", volume="1", effect="F", speed=15)
        pyxel.sound(6).set(note='C1RA0RF0RE0C1RA0RF0RE0C1RA0RF0RE0C1RA0RF0RE0', tone="S", volume='3', effect='F', speed=3) #DEAD
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self): #初期設定
        for i in range(15):
            pyxel.pal(i,i)  #リスタート時の復帰の時、色を元に戻すためのやつ

        pyxel.play(2,5, loop = True)

        self.tower = Tower()
        self.enemy = Enemy()

        self.level = 1

        self.gold, self.income = 0, 0.03
        self.totalgain = 0
        self.selectingtower = 1
        self.selectingx = 0 #1ブロック16xであるが、pyxelの仕様上タイルマップを調べる時はx*2,y*2する。(8bitのため)
        self.selectingy = 0
        self.selecttimer = 0
        self.buyrequest = False
        self.upgraderequest = False
        self.waverequest = True
        self.health = 1 #陣地に入ってしまうと1減る
        self.game_over = False
        self.title = True
        self.titletimer = 60

    def update(self): #ゲーム進行
        if self.title:
            self.titletimer -= 1
            if self.titletimer == -60:
                self.titletimer = 60
            if pyxel.btnp(pyxel.KEY_Q):
                self.title = False
                pyxel.play(2,3)
        if not self.game_over and not self.title:
            self.gold = self.gold + self.income
            self.totalgain = self.totalgain + self.income
            if self.totalgain >= 50 + 400 * (self.level-1) ** 2:
                self.level += 1
                self.income = self.income + self.level ** 2 * 0.01
                pyxel.play(2,3)

            self.input_key()
            for i in range(5): #買えるかどうかの変数を見る
                if self.gold < self.tower.towerset[i][4]:
                    self.tower.towerset[i][5] = False
                else:
                    self.tower.towerset[i][5] = True

            if self.buyrequest:
                self.gold = self.tower.buy(self.gold, self.selectingtower, self.selectingx, self.selectingy)
                self.buyrequest = False
            if self.upgraderequest:
                self.tower.upgrade(self.gold, self.selectingx, self.selectingy)
                self.upgraderequest = False

            self.enemy.spawn(self.totalgain,self.level)
            self.enemy.enemy_move()
            self.gold += self.enemy.enemy_dead()
            if self.enemy.enemy_invade(): #delは敵を消すことについての関数だが、trueが返るのは陣地に入って消えた時だけ
                self.health -= 1
                pyxel.play(2,2)


            self.attackdrawxy = self.attack()

            if self.health <= 0 and not self.game_over:
                self.game_over = True
                pyxel.play(2,6)
                for i in range(15):
                    pyxel.pal(i,random.randint(0,15))
                pyxel.pal(0,0)
                pyxel.pal(8,8)

        if self.game_over:
            if pyxel.btn(pyxel.KEY_Q):
                self.init()

    def draw(self): #画面描画
        if self.title:
            if self.titletimer >= 20:
                i,j,k = 8,9,10
            elif -20 < self.titletimer < 20:
                i,j,k = 10,8,9
            else:
                i,j,k = 9, 10, 8
            pyxel.cls(0)
            pyxel.text(30,60,"XXXXX XXXXX X   X XXXXX XXXXX  ", i)
            pyxel.text(30,64,"  X   X   X X X X X     X   X   ", i)
            pyxel.text(30,68,"  X   X   X XX XX XXXXX XXXXX  ", j)
            pyxel.text(30,72,"  X   X   X X   X X     X X    ", j)
            pyxel.text(30,76,"  X   XXXXX X   X XXXXX X  XX  ", k)

            pyxel.text(60,84,"XXX   XXXXX XXXXX XXXXX X   X  XXX XXXXX", k)
            pyxel.text(60,88,"X  X  X     X     X     XX  X X    X", j)
            pyxel.text(60,92,"X   X XXXX  XXXXX XXXX  X X X  XX  XXXXX", j)
            pyxel.text(60,96,"X  X  X     X     X     X  XX    X X", i)
            pyxel.text(60,100,"XXX   XXXXX X     XXXXX X   X XXX  XXXXX", i)

            if self.titletimer >= 0:
                pyxel.text(90,120,"PRESS Q TO START", 7)

        if not self.title:
            pyxel.cls(7)
            pyxel.bltm(0, 0, 0, 0, 0, 32, 32)
            #右側GUIの描画
            for i in range(5):
                pyxel.blt(168,32+i*24,0,0,16+i*16,16,16,0)
                if self.tower.towerset[i][5]: #買えるかどうかで色を変える
                    availabilitycls = 7
                else:
                    availabilitycls = 9
                pyxel.text(188,33+i*24,"COST:"+str(self.tower.towerset[i][4]),availabilitycls)
                pyxel.text(188,41+i*24,"DMG:"+str(self.tower.towerset[i][3]),availabilitycls)
            pyxel.rectb(166,6+self.selectingtower*24,84,20,0)
            pyxel.text(168,8,"GOLD:"+str(math.floor(self.gold)),7)
            pyxel.text(220,8,"LEVEL:"+str(self.level),7)
            pyxel.text(168,24,"NEXT LEVEL:"+str(math.floor(self.totalgain))+"/"+str(math.floor(50 + 400 * (self.level-1) ** 2)),7)
            for i in range(self.health):
                pyxel.text(168+i*4,16,"V",8)

            self.tower.draw_tower()
            self.enemy.draw_enemy()

            for i in range(len(self.attackdrawxy)):
                pyxel.line(self.attackdrawxy[i][0]*16+8,self.attackdrawxy[i][1]*16+8,self.attackdrawxy[i][2]+8,self.attackdrawxy[i][3]+8,2)


            ## DEBUG:
            #print(self.enemy.enemylist)
            pyxel.rectb(self.selectingx * 16,self.selectingy * 16,16,16,0)

        if self.game_over:
            pyxel.rect(50,80,150,20,0)
            pyxel.text(52,82,"YOU ARE DEAD", 8)
            pyxel.text(52,92,"PRESS Q TO RE-START THE GAME", 8)

    def input_key(self):
        self.selecttimer += 1
        if pyxel.btnp(pyxel.KEY_1):
            self.selectingtower = 1
        if pyxel.btnp(pyxel.KEY_2):
            self.selectingtower = 2
        if pyxel.btnp(pyxel.KEY_3):
            self.selectingtower = 3
        if pyxel.btnp(pyxel.KEY_4):
            self.selectingtower = 4
        if pyxel.btnp(pyxel.KEY_5):
            self.selectingtower = 5
        if pyxel.btn(pyxel.KEY_LEFT) and self.selectingx >= 1 and self.selecttimer >= 8:
            self.selectingx -= 1
            self.selecttimer = 0
        if pyxel.btn(pyxel.KEY_RIGHT) and self.selectingx < 9 and  self.selecttimer >= 8:
            self.selectingx += 1
            self.selecttimer = 0
        if pyxel.btn(pyxel.KEY_UP) and self.selectingy >= 1 and  self.selecttimer >= 8:
            self.selectingy -= 1
            self.selecttimer = 0
        if pyxel.btn(pyxel.KEY_DOWN) and self.selectingy < 15 and  self.selecttimer >= 8:
            self.selectingy += 1
            self.selecttimer = 0
        if pyxel.btnp(pyxel.KEY_Q):
            self.buyrequest = True
        if pyxel.btnp(pyxel.KEY_W):
            self.upgraderequest = True

    def attack(self):
        #cdを1減らして、0になったらsearch→attack. (範囲内の敵を探す→ランダムな敵を狙う)
        drawxy = []
        for i in range(len(self.tower.towerlist)):
            self.tower.towerlist[i][4] -= 1
            if self.tower.towerlist[i][4] <= 0 and not len(self.enemy.enemylist) == 0:
                targetenemyindex = []
                for k in range(self.tower.towerset[self.tower.towerlist[i][0]-1][1]):
                    self.tower.towerlist[i][4] = self.tower.towerset[self.tower.towerlist[i][0]-1][6]
                    x1 = self.tower.towerlist[i][2] * 16 - 8 + self.tower.towerset[self.tower.towerlist[i][0]-1][2] * 16
                    x2 = self.tower.towerlist[i][2] * 16 - 8 - self.tower.towerset[self.tower.towerlist[i][0]-1][2] * 16
                    y1 = self.tower.towerlist[i][3] * 16 - 8 + self.tower.towerset[self.tower.towerlist[i][0]-1][2] * 16
                    y2 = self.tower.towerlist[i][3] * 16 - 8 - self.tower.towerset[self.tower.towerlist[i][0]-1][2] * 16#攻撃範囲のx1,x2,y1,y2を出す
                    for j in range(len(self.enemy.enemylist)):
                        if x2 <= self.enemy.enemylist[j][3] <= x1 and y2 <= self.enemy.enemylist[j][4] <= y1:
                            targetenemyindex.append(j)
                    if len(targetenemyindex) >= 1:
                        who = random.choice(targetenemyindex)
                        self.enemy.enemylist[who][1] -= self.tower.towerset[self.tower.towerlist[i][0]-1][3]
                        drawxy.append([self.tower.towerlist[i][2],self.tower.towerlist[i][3],self.enemy.enemylist[who][3],self.enemy.enemylist[who][4],6]) #攻撃towerのx,y,喰らう相手のx,y
                        pyxel.play(1,4)
        return drawxy


class Tower: #タワー管理
    def __init__(self): #[target,range,dmg,rate,Availability(True or False)]
        self.towerlist = [] #[towerID,level(0からスタート),x,y,cooldown]
        self.towerset = [
        [1, 1, 3, 5, 10, True, 60], #[towerid,target,range,dmg,gold,availability, cooldown] bowgun
        [2, 3, 3, 20, 60, True, 90], #witch
        [3, 10, 8, 80, 450, True, 150], #mortar
        [4, 1, 3, 165, 2000, True, 60], #tesla
        [5, 2, 3, 2000, 35000, True, 60], #spitfire
        ]

    def buy(self, gold, select, x, y):
        if gold >= self.towerset[select-1][4] and not self.towercheck(x,y):
            self.towerlist.append([select,0,x,y,self.towerset[select-1][6]]) #[select,level,0,x,y,cooldown]
            gold -= self.towerset[select-1][4]
            pyxel.play(0,0)
            return gold
        else:
            self.buy_refuse()
            return gold

    def towercheck(self,x,y): #Trueなら調べた(x,y)に何かしらのタワーが存在するか、設置できない場所である。
        for i in range(len(self.towerlist)):
            if pyxel.tilemap(0).get(x*2,y*2) == 4: #4はおけないところ(草ブロック)
                return True
            elif x == self.towerlist[i][2] and y == self.towerlist[i][3]:
                self.holder = i
                return True

    def buy_refuse(self):
        pyxel.play(0,1)

    def draw_tower(self):
        for i in range(len(self.towerlist)):
            pyxel.blt(self.towerlist[i][2]*16,self.towerlist[i][3]*16,0,self.towerlist[i][1]*16,self.towerlist[i][0]*16,16,16,0)

class Enemy:
    def __init__(self):
        self.enemylist = [] #[enemyid,health,speed,x,y,d] #dは右下左で0,1,2
        self.enemyset = [
        [1, 15, 10, 2], #[enemyid,health,speed,gold] slime
        [2, 300, 0.2, 10], #stoneboy
        [3, 180, 1, 30], #rabbit
        [4, 1200, 0.4, 90]
        ]
        self.spawntimer = 1

    def spawn(self,gain,level): #一定時間経過するとモンスターを出現させる
        self.spawntimer -= 1
        if self.spawntimer == 0:
            enemyid = random.randint(0+math.floor(level**2/6), 0+(level-1))
            self.enemylist.append([self.enemyset[enemyid][0],
                                self.enemyset[enemyid][1],
                                self.enemyset[enemyid][2],
                                24,
                                -16,
                                1])
            if enemyid == 3:
                self.spawntimer = random.randint(20, math.floor((20+60/level)))
            else:
                self.spawntimer = random.randint(40, math.floor((40+140/level)))

    def enemy_move(self): #現在の敵の数だけ敵を動かす
        for i in range(len(self.enemylist)):

            if self.enemylist[i][5] == 0: #右向きなら右に進む
                self.enemylist[i][3] += self.enemylist[i][2]
            elif self.enemylist[i][5] == 1: #下向きなら下に進む
                self.enemylist[i][4] += self.enemylist[i][2]
            elif self.enemylist[i][5] == 2: #左向きなら左に進む
                self.enemylist[i][3] -= self.enemylist[i][2]

            #方向転換
            if self.enemylist[i][5] == 1 and self.enemylist[i][3] == 24 and 40 > self.enemylist[i][4] >= 24:
                self.enemylist[i][5] = 0
            elif self.enemylist[i][5] == 0 and self.enemylist[i][3] >= 120 and 40 > self.enemylist[i][4] >= 24:
                self.enemylist[i][5] = 1
            elif self.enemylist[i][5] == 1 and self.enemylist[i][3] >= 120 and 90 >self.enemylist[i][4] >= 72:
                self.enemylist[i][5] = 2
            elif self.enemylist[i][5] == 2 and self.enemylist[i][3] <= 24 and 90 > self.enemylist[i][4] >= 72:
                self.enemylist[i][5] = 1
            elif self.enemylist[i][5] == 1 and self.enemylist[i][3] <= 24 and 140 > self.enemylist[i][4] >= 120:
                self.enemylist[i][5] = 0
            elif self.enemylist[i][5] == 0 and self.enemylist[i][3] >= 120 and 140 > self.enemylist[i][4] >= 120:
                self.enemylist[i][5] = 1
            elif self.enemylist[i][5] == 1 and self.enemylist[i][3] >= 120 and 190 > self.enemylist[i][4] >= 168:
                self.enemylist[i][5] = 2
            elif self.enemylist[i][5] == 2 and self.enemylist[i][3] <= 24 and 190 > self.enemylist[i][4] >= 168:
                self.enemylist[i][5] = 1
            elif self.enemylist[i][5] == 1 and self.enemylist[i][3] <= 24 and 240 > self.enemylist[i][4] >= 216:
                self.enemylist[i][5] = 0
            elif self.enemylist[i][5] == 0 and self.enemylist[i][3] >= 120 and 240 > self.enemylist[i][4] >= 216:
                self.enemylist[i][5] = 1

    def enemy_dead(self): #体力が0なら単純に消す
        indexnumber = []
        gold = 0
        for i in range(len(self.enemylist)):
            if self.enemylist[i][1] <= 0:
                indexnumber.append(i)
        for i in range(len(indexnumber)):
            gold += self.enemyset[self.enemylist[i][0]-1][3]
            del self.enemylist[indexnumber[i]]
        return gold

    def enemy_invade(self): #敵が陣地に入る(= yが255以上)と、対象の敵を削除し、trueを返す
        for i in range(len(self.enemylist)):
            if self.enemylist[i][4] >= 255:
                del self.enemylist[i]
                return True

    def draw_enemy(self):
        for i in range(len(self.enemylist)):
            pyxel.blt(self.enemylist[i][3],self.enemylist[i][4],0,0,80+self.enemylist[i][0]*16,16,16,0)
            pyxel.rect(self.enemylist[i][3],self.enemylist[i][4]+ 17,16,1,0)
            pyxel.rect(self.enemylist[i][3],self.enemylist[i][4]+ 17,math.floor(self.enemylist[i][1] / self.enemyset[self.enemylist[i][0]-1][1]*16),1,8)
            #pyxel.rect(self.enemylist[i][3],self.enemylist[i][4],16,16,4)
App()
