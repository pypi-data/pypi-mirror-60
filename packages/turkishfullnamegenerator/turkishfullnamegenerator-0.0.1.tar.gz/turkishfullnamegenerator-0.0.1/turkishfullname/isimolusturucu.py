# -*- coding: utf-8 -*-
import random
kadinisimler=["Nuray","Nehi̇r","Hali̇me","Ayşenur","Ayten","Rabi̇a","Duygu","Gülay","Ni̇sanur","Necla","Ebru","Arzu",
"Sudenaz","Derya","Edanur","Seda","Si̇bel","Emel","Damla","İlayda","Hava",
"Meli̇ke","Sevi̇m","Fatma","Zehra","Nurten","Hacer","Türkan","Gamze","Ayşe",
"Sema","Di̇lara","Yasemi̇n","Şükran","Kader","Nuran","Esma","Yağmur","Çi̇ğdem",
"Ceren","Sila","Kezi̇ban","Hi̇lal","Güler","Berfi̇n","Özlem","Zeli̇ha","Sultan",
"Cansu","Ecri̇n","Tuğçe","Nesli̇han","İlknur","Esmanur","Azra","Gi̇zem","Özge","Eli̇f","Şeri̇fe",
"Sevgi̇","Seher","Zeynep","Yaren","Yildiz","Medi̇ne","Şevval","Di̇lek","Betül","Havva","Si̇nem",
"Asi̇ye","Leyla","Tuğba","Hani̇fe","Buse","Selma","Fadi̇me","Ni̇sa","Hülya","Di̇lan","Sümeyye",
"Semra","Esra","İrem","Sude","Aleyna","Şeyma","Serpi̇l","Kübra","Eylül","Kadri̇ye","Sevda",
"Sani̇ye","Gülten","Tuba","Bahar","Serap","Melek","Gönül","Meli̇sa","Aynur","Eda","Aysel","Songül",
"Merve","Şengül","Ayşegül","Nermi̇n","Hati̇ce","Beyza","Canan","Hayri̇ye","Burcu","Fi̇li̇z","Cemi̇le",
"Pinar","Semanur","Emi̇ne","Meryem","Döndü","Nurcan","Büşra"]

erkekisimleri=["Emi̇r","Serdar","Emi̇rhan","İbrahi̇m","Bayram","Ahmet","Engi̇n","Erdal","Kenan","Si̇nan","Erkan","Faruk",
"Berat","Ramazan","Volkan","Kemal","Erdoğan","Bülent","Eren","Hamza","Sedat","Bariş","İsmet","Özgür","Süleyman",
"Muhammet","İsmai̇l","Selahatti̇n","Hüseyi̇n","Arda","Orhan","Cengi̇z","Muzaffer","Ömer","Hasan","Beki̇r",
"Umut","Selçuk","Serhat","Fati̇h","Abdullah","Burak","Yasi̇n","Yüksel","Mahmut","Emre","Meti̇n",
"Hakan","Ümi̇t","Batuhan","Ni̇hat","Enes","Ali̇","Mert","Şaban","Kaan","Adem","Ferhat","Mustafa",
"Okan","Berkay","Mesut","Ayhan","Firat","Alperen","Emrah","Nuretti̇n","Kerem","Gökhan","Aydin",
"Kadi̇r","Musa","Yilmaz","Cemal","Recep","Yi̇ği̇t","Zeki̇","Erhan","Murat","Ercan","Adnan","Yusuf",
"Mehmet","Samet","Yaşar","Onur","Sali̇h","Baran","Uğur","Serkan","Yunus","Furkan","Oğuzhan","Hali̇l","Osman","Erol","Ari̇f","Efe","Anıl"]

soyadlar=["Taş","Özer","Aktaş","Bozkurt","Keski̇n","Işik","Teki̇n","Kiliç","Turan","Kaya","Yildiz","Şahi̇n","Şen","Aksoy","Can",
"Kurt","Ünal","Ateş","Şi̇mşek","Korkmaz","Öztürk","Acar","Özcan","Özdemi̇r","Kara","Sari","Yilmaz","Avci","Yüksel",
"Polat","Aslan","Aydin","Güneş","Çeli̇k","Güler","Demi̇r","Çeti̇n","Doğan","Yavuz","Erdoğan","Çakir","Köse",
"Kaplan","Koç","Arslan","Özkan","Bulut","Gül","Yildirim","Yalçin"]


def generate_name(gender):
    kullanilacakisimler=[]
    if gender=="kadin" or gender=="kadın" or gender=="woman":
        kullanilacakisimler=kadinisimler
    elif gender=="erkek" or gender=="man":
        kullanilacakisimler=erkekisimleri
    else:
        raise ValueError("gender parameter have to be one of that: kadin, kadın, woman, erkek, man")
    isim=random.choice(kullanilacakisimler)
    soyad=random.choice(soyadlar)
    gobekadi_sansi=random.randint(0,10)
    if gobekadi_sansi<=3:
        gobekisim=isim
        while gobekisim==isim:
              gobekisim=random.choice(kullanilacakisimler)
        isim+=" "+gobekisim      
    return isim+" "+soyad

for i in range(1,10):
    pass
    #print(generate_name("kadin"))
def generate_names(gender,number=10):
    liste=[]
    for i in range(1,number):
        generated=generate_name(gender)
        liste.append(generated)
    return liste    
