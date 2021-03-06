# nearest_netprint.py  
# by Elisabeth Finkel (finkelelisabeth@gmail.com ; esf76@cornell.edu)
# written May 28, 2018
# last modified Dec 25, 2018
# free for personal use/distribution, ideally with these credits intact

#      if automated upload performed correctly, this message will appear

'''

When run on command line, prints a list of the nearest netprint-enabled printers
    offered by Cornell.
    - You can specify type of printer with argvs 'color' or 'bw'.
    - If you do not specify, you will receive lists for both.
    - Your GPS location is computed automatically - if you think it's inaccurate,
      use argv 'manual' to be prompted for manual coord entry
Requires internet access but no other input.
Note that, as building hours have not yet been inputted, printers suggested to
    you may be in buildings that are closed.
    - Building hours can typically be manually checked via Google Maps or
      departmental websites.
    - If anyone knows an API for that, let me know. Or try it yourself.
Note also that, as most of the coordinates were extracted from another API,
    some of them are likely wrong.
    - Feel free to correct those errors as they arise.
'''


import requests
import json
from math import radians, cos, sin, asin, sqrt
import datetime
import time
import webbrowser
from selenium import webdriver
import os
import sys


# for each printer, store (0: name, 1: text-form location, 2: bw or color info, 3: decimal latitude, 4: decimal longitude, 5: schedule)
# for schedule: {0:[,],1:[,],2:[,],3:[,],4:[,],5:[,],6:[,]} where monday is 0

############################

printers_bw = [
    ['aap-nyc-1bw','NYTech (direct print; card reader)','campus-bw, campus-color','40.7558','-73.9562',None],
    ['aap-sib-1bw','Sibley Hall - 3rd Floor Lab (Barclay Jones)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-sib-3bw','Sibley Hall - 2nd Floor Lab (ADMS) (direct print; card reader?)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-sib-4bw','Sibley Hall - 3rd Floor Balcony (inside dome) (direct print; card reader?)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-tjaden-1bw','Tjaden Hall - Take elev. to 2W (direct print or card reader)','campus-bw, campus-color','42.4509025','-76.4853131',None],
    ['afr-lib1','Africana Library','campus-bw, campus-color','42.4573916','-76.4822137',{0:[9,23],1:[9,23],2:[9,23],3:[9,23],4:[9,17],5:[13,17],6:[16,23]}],
    ['appel1','Appel Commons Community Center - 1st Floor','campus-bw',42.4535925,-76.4764187,{0:[9,22],1:[9,22],2:[9,22],3:[9,22],4:[9,22],5:[11,22],6:[12,22]}],
    ['becker-nprint1','Becker House - Room G39 - Computer Lab - North wing - Ground floor','campus-bw','42.448204','-76.4894583',None],
    ['becker-nprint2','Becker House - Computer lab - North wing - Ground floor Room# G39','campus-bw','42.448204','-76.4894583',None],
    ['bin1','Statler Hall 365 - by the lab monitor desk - fourth from window','campus-bw','42.4454727','-76.48206789999999',None],
    ['bin2','Statler Hall 365 - by the lab monitor desk - third from window','campus-bw','42.4454727','-76.48206789999999',None],
    ['bin3','Statler Hall 365 - by the lab monitor desk - second from window','campus-bw','42.4454727','-76.48206789999999',None],
    ['catherwood-lnge','Catherwood Library - 136 Ives Hall - First Floor Lounge','campus-bw, campus-color','42.4472562','-76.4811158',None],
    ['catherwood-np1/catherwood-np2/catherwood-np3','Catherwood Library - 236 Ives Hall - Reference Area','campus-bw, campus-color','42.4472562','-76.4811158',None],
    ['cisuglab','Gates Hall - Room G33 (CS majors/staff only. direct print; no card reader?)','campus-bw','42.4449769','-76.4810912',None],
    ['cit-carp-1bw/cit-carp-3bw','Carpenter Hall Computer Lab - Main Floor','campus-bw, campus-color','42.444767','-76.484124',{0:[0,600],1:[0,600],2:[0,600],3:[0,600],4:[0,600],5:[0,600],6:[0,600]}],
    ['cit-carp-4bw/cit-carp-5bw','Carpenter Hall Computer Lab - Second Floor Hallway','campus-bw, campus-color','42.444767','-76.484124',{0:[0,600],1:[0,600],2:[0,600],3:[0,600],4:[0,600],5:[0,600],6:[0,600]}],
    ['cit-mann220a-1bw/cit-mann220a-2bw','Mann Library Computer Lab - Room 220A - Second Floor','campus-bw, campus-color','42.448766','-76.4763118',None],
    ['cit-ph318-1bw/cit-ph318-2bw','Phillips Hall Computer Lab - Room 318','campus-bw, campus-color','42.4445768','-76.4820529',None],
    ['cit-rpcc-1bw/cit-rpcc-2bw','Robert Purcell Community Center - RPCC - Computer Lab - Room 207','campus-bw, campus-color','42.4562967','-76.4783146',{0:[9,23.99],1:[9,23.99],2:[9,23.99],3:[9,23.99],4:[9,23.99],5:[11,23.99],6:[12,23.99]}],
    ['cit-surge-1bw','Ag Quad - Academic Surge B - Room 159','campus-bw, campus-color','42.4488081','-76.4780298',None],
    ['cit-upson-1bw/cit-upson-2bw','Upson Hall - Room 225','campus-bw, campus-color','42.4439852','-76.4828736',None],
    ['cit-uris-1bw/cit-uris-2bw','Uris Library - Tower Room Computer Lab - Downstairs from Entrance','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['cit-uris-3bw','Uris Library - Electronic Classroom - Room B05','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['cit-wsh-1bw/cit-wsh-2bw','Willard Straight Hall - Computer Lab - Basement Level','campus-bw, campus-color','42.4465919','-76.4856765',{0:[9,16],1:[9,16],2:[9,16],3:[9,16],4:[9,16],5:[0,-1],6:[0,-1]}],
    ['ciw2','District of Columbia - Cornell in Washington','campus-bw, campus-color','42.4358405','-76.493497',None],
    ['cook-nprint1','Alice Cook House - Computer Lab','campus-bw','42.4489805','-76.4896109',None],
    ['dss-mps-lab1','MPS Statistics computing lab room Mallot 301A - card reader door access for MPS students only','campus-bw','42.4479101','-76.4800518',None],
    ['gs1','Goldwin Smith Hall - Room 338 (direct print; card reader?)','campus-bw','42.44907329999999','-76.4835344',None],
    ['gs3','Goldwin Smith Hall – Room 213 (direct print; card reader?)','campus-bw','42.44907329999999','-76.4835344',None],
    ['hollister1','Hollister 202 CEE Undergrad Lounge (direct print; card reader?)','campus-bw','42.4443332','-76.4847092',None],
    ['house5','Rose House - Computer Lab - Room# 110','campus-bw','42.4477928','-76.4888006',None],
    ['ilr-lab1/ilr-lab2','Ives Hall - Room 118 - Computer Lab','campus-bw, campus-color','42.4472571','-76.4811162',{0:[8,23],1:[8,23],2:[8,23],3:[8,23],4:[8,17],5:[0,0],6:[14,23]}],
    ['keeton-nprint1','Keeton House - Room 151 - Computer Lab','campus-bw','42.4467158','-76.4894902',None],
    ['kroch-lib1','Kroch Library - 1st floor Asia reading room','campus-bw, campus-color','42.4477741','-76.4841596',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['laprinter2','Kennedy Hall - Room 467 (direct print; card reader?)','campus-bw','42.4482603','-76.4793974',None],
    ['law-lib1','Law Library - 3rd floor','campus-bw','42.4438549','-76.48577239999997',{0:[8,20],1:[8,20],2:[8,20],3:[8,20],4:[8,17],5:[11,17],6:[12,20]}],
    ['mann1/mann2/mann3','Mann Library - First Floor','campus-bw, campus-color','42.4487577','-76.47631179999999',{0:[8,24],1:[8,24],2:[8,24],3:[8,24],4:[8,18],5:[12,19],6:[12,24]}],
    ['mann6','Mann Library - 2nd Floor','campus-bw, campus-color','42.448766','-76.47631179999999',{0:[8,24],1:[8,24],2:[8,24],3:[8,24],4:[8,18],5:[12,19],6:[12,24]}],
    ['math-lib2','Mallott Hall - Math Library - Fourth Floor','campus-bw','42.4482224','-76.4802083',{0:[8,20],1:[8,20],2:[8,20],3:[8,20],4:[8,20],5:[0,0],6:[13,22]}],
    ['mcfaddin1/mcfaddin2','McFaddin - Room G22 - Computer Lab','campus-bw','42.447337', '-76.487931',None],
    ['morrison-1','Morrison Hall - Animal Science Undergraduate Student Lounge - Room 140 (direct print; card reader?)','campus-bw','42.446309','-76.469368',None],
    ['mseugrad','Bard Lab 247 (direct print; card reader?)','campus-bw','42.4439614','-76.5018807',None],
    ['mth-372/mth-373/mth-374/mth-375','Myron Taylor Hall 2nd Floor Computer Lab (direct print; card reader?)','campus-bw','42.444460','-76.486113',None],
    ['mth-ilj','Myron Taylor Hall International Law Journal Office (direct print; card reader?)','campus-bw','42.444460','-76.486113',None],
    ['mth-jlpp','Myron Taylor Hall Journal Law and Public Policy Office (direct print; card reader?)','campus-bw','42.444460','-76.486113',None],
    ['mth-lawreview','Myron Taylor Hall Law Review Office (direct print; card reader?)','campus-bw','42.444460','-76.486113',None],
    ['mth-studentorg','Myron Taylor Hall Student Organizations Office (direct print; card reader?)','campus-bw','42.444460','-76.486113',None],
    ['music-lib1','Music Library - 3rd floor Lincoln Hall','campus-bw, campus-color','42.4501817','-76.4833675',{0:[9.0,22.0],1:[9.0,22.0],2:[9.0,22.0],3:[9.0,22.0],4:[9.0,17.0],5:[12.0,5.0],6:[14.0,22.0]}],
    ['olin-lib1/olin-lib2/olin-lib3/olin-lib4','Olin Library - behind the reference desk','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['olin-lib6','Olin Library - B12','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['olin-lib7','Olin Library - 5th floor Grad Study','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['orie-netprint2','Rhodes Hall - Room 453 (direct print; no card reader)','campus-bw',42.4433613,-76.4812668,None],
    ['orie-netprint3','Rhodes Hall - Room 421 (moved to 411? direct print; no card reader)','campus-bw',42.4433613,-76.4812668,None],
    ['physci-lib1','Clark Hall - Physical Sciences Library','campus-bw, campus-color','42.4497606','-76.4812001',{0:[0,1000],1:[0,1000],2:[0,1000],3:[0,1000],4:[0,1000],5:[0,1000],6:[0,1000]}],
    ['sage-205/sage-205-bw2','Sage Hall - Room 205 Suite - Next to Dean\'s Office','campus-bw, campus-color','42.4458918','-76.4833009',None],
    ['sage-301-bw','Sage Hall Library - Room 301 - Third Floor Collaboration Space','campus-bw, campus-color','42.4458947','-76.4832581',None],
    ['sage-basement-a/sage-basement-b','Sage Hall - Basement - Near Student Mailboxes','campus-bw','42.4458918','-76.4833009',None],
    ['sage-lib1-bw/sage-lib2-bw','Sage Hall - Library - First Floor','campus-bw','42.4458918','-76.4833009',{0:[7,21],1:[7,21],2:[7,21],3:[7,21],4:[7,21],5:[7,21],6:[7,21]}],
    ['schwartz1','Schwartz Center - Second Floor - Near elevator (direct print; card reader?)','campus-bw',42.4424328,-76.4859273,None],
    ['sha-grad1','Statler Hall G0032 (direct print; card reader?)','campus-bw',42.4668288,-76.4851556,None],
    ['sha-grad2','Statler Hall 245','campus-bw (direct print; card reader?)',42.4668288,-76.4851556,None],
    ['sha-mslc-front1/sha-mslc-front2/sha-mslc-front3','Nestle Library - west side of reference desk','campus-bw',42.446092,-76.4815932,{0:[8,23.5],1:[8,23.5],2:[8,23.5],3:[8,23.5],4:[8,18.5],5:[12,18.5],6:[12,23.5]}],
    ['sha-mslc-lounge','Statler Hall Ground Floor Student Lounge - North side of room','campus-bw',42.4668288,-76.4851556,None],
    ['sha-mslc-quick','Nestle Library - by the standup "Quick Print" stations','campus-bw',42.446092,-76.4815932,None],
    ['snee-netprint1','Snee Hall Student Lounge','campus-bw','42.443653','-76.484938',None],
    ['tatkon1','South Balch Hall - Tatkon Center - Front Desk','campus-bw','42.453212','-76.479392',{0:[8,23],1:[8,23],2:[8,23],3:[8,23],4:[8,17.5],5:[0,0],6:[15,23]}],
    ['uris-lib1','Uris Library - In Front of Circulation Desk','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['uris-lib3','Uris Library - Austen Room','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['uris-lib5','Uris Library - CL3 Lab','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['vetlib2','Schurman Hall - S1201 (direct print; card reader?)','campus-color','42.4480179','-76.4661765',{0:[7.5,23],1:[7.5,23],2:[7.5,23],3:[7.5,23],4:[7.5,20],5:[10,20],6:[10,23]}],
    ['vetlib3','Schurman Hall - S1201 (direct print; card reader?)','campus-bw','42.4480179','-76.4661765',{0:[7.5,23],1:[7.5,23],2:[7.5,23],3:[7.5,23],4:[7.5,20],5:[10,20],6:[10,23]}],
    ['vm-bilinski-01','Bilinski Lab (direct print; card reader?)','campus-bw','42.4799809','-76.4511259',None],
    ['vm-wiswall-01/vm-wiswall-02','Wiswall Lab (direct print; card reader?)','campus-bw','42.4799809','-76.4511259',None],
    ['whitelab','White Hall - Room B10 (direct print; faculty and grads only)','campus-bw','42.4502416','-76.4853705',None]

]

printers_color = [

    #['aap-mil-1mfp/aap-mil-2mfp/aap-mil-3mfp/aap-mil-4mfp','Milstein Hall - Behind the elevators (2nd floor)','campus-bw, campus-color','42.451232','-76.4836401',None],
    #['aap-nyc-1c','NYTech (direct print; card reader?)','campus-bw, campus-color','42.4439614','-76.5018807',None],
    #['aap-nyc-1mfp','AAP NYC','campus-color','42.4509482','-76.48409099999999',None],
    #['aap-rome-1c','Rome - Italy','campus-bw, campus-color','40.7433036','-73.87694379999999',None],
    ['aap-sib-1c','Sibley Hall - 3rd Floor Lab (Barclay Jones)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-sib-3c','Sibley Hall - 2nd Floor Lab (ADMS) (direct print; card reader?)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-sib-3mfp/aap-sib-4c','Sibley Hall - 3rd Floor Balcony (inside dome) (direct print; card reader?)','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['aap-tjaden-1c','Tjaden Hall - Take elev. to 2W (broken as of spr 2019; direct print or card reader)','campus-bw, campus-color','42.4509025','-76.4853131',{0:[9,16],1:[9,16],2:[9,16],3:[9,16],4:[9,16],5:[0,0],6:[0,0]}],
    ['aep-netprint1','Clark Hall - Room 244 (AEP only) (direct print; card reader?)','campus-bw, campus-color','42.4497606','-76.4812001',None,],
    ['africana-1st-floor','Africana first floor','campus-bw, campus-color','42.457403','-76.482239',{0:[9,23],1:[9,23],2:[9,23],3:[9,23],4:[9,17],5:[13,17],6:[16,23]}],
    ['bin-color','Statler Hall 365 - by the lab monitor desk - closest to window','campus-bw, campus-color',42.4668288,-76.4851556,None],
    ['catherwood-library1','Catherwood Library','campus-bw, campus-color','42.4472562','-76.4811158',None],
    ['catherwood-np4c','Catherwood Library - 236 Ives Hall - Reference Area','campus-bw, campus-color','42.4472562','-76.4811158',None],
    ['cbs-olin-basement-2c','Olin Library','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['cit-carp-2c','Carpenter Hall Computer Lab - Main Floor','campus-bw, campus-color','42.444767','-76.484124',{0:[0,600],1:[0,600],2:[0,600],3:[0,600],4:[0,600],5:[0,600],6:[0,600]}],
    ['cit-mann220a-3c','Mann Library Computer Lab - Room 220A - Second Floor','campus-bw, campus-color','42.448766','-76.476312',{0:[8,24],1:[8,24],2:[8,24],3:[8,24],4:[8,18],5:[12,19],6:[12,24]}],
    ['cit-ph318-3c','Phillips Hall Computer Lab - Room 318','campus-bw, campus-color','42.4445768','-76.4820529',None],
    ['cit-rpcc-3c','Robert Purcell Community Center - RPCC - Computer Lab - Room 207','campus-bw, campus-color','42.4562967','-76.4783146',{0:[9,23.99],1:[9,23.99],2:[9,23.99],3:[9,23.99],4:[9,23.99],5:[11,23.99],6:[12,23.99]}],
    ['cit-upson-3c','Upson Hall - Room 225','campus-bw, campus-color','42.4439852','-76.4828736',None],
    ['cit-uris-4c','Uris Library - Tower Room Computer Lab - Downstairs from Entrance','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['cit-weill-1c','B25 Weill Hall - 237 Tower Road','campus-bw, campus-color','42.4468068','-76.477214',None],
    ['cit-wsh-3c','Willard Straight Hall - Computer Lab - Basement Level','campus-bw, campus-color','42.4465919','-76.4856765',{0:[9,16],1:[9,16],2:[9,16],3:[9,16],4:[9,16],5:[0,-1],6:[0,-1]}],
    ['ciw1','District of Columbia - Cornell in Washington','campus-bw, campus-color','38.908422','-77.048536',None],
    ['csmenglab','Gates Hall - Room G23 (direct print; card reader? under construction as of Spr 2019)','campus-bw, campus-color','42.4449769','-76.4810912',None],
    #['fine-lib2c','Fine Arts Library - B56 Sibley Hall','campus-bw, campus-color','42.4512236','-76.4828622',{0:[9,19],1:[9,19],2:[9,19],3:[9,19],4:[9,17],5:[12,17],6:[13,19]}],
    ['hollister2c','Hollister 202 CEE Undergrad Lounge (direct print; card reader?)','campus-bw, campus-color','42.444368','-76.48463919999999',None],
    ['kroch-lib-2-mfp/kroch-lib-3-mfp','Kroch Library','campus-bw, campus-color','42.447774','-76.484160',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['lacolor1','Kennedy Hall - Room 467 (direct print; card reader?)','campus-bw, campus-color','42.4482603','-76.4793974',None],
    ['law-mfp1','Law','campus-bw, campus-color','42.4438549','-76.48577239999997',{0:[8,20],1:[8,20],2:[8,20],3:[8,20],4:[8,17],5:[11,17],6:[12,20]}],
    ['lincoln-2floor','lincoln-second floor','campus-bw, campus-color','42.4501817','-76.4833675',{0:[9.0,22.0],1:[9.0,22.0],2:[9.0,22.0],3:[9.0,22.0],4:[9.0,17.0],5:[12.0,5.0],6:[14.0,22.0]}],
    ['mann-mfp1/mann-mfp2','Mann','campus-bw, campus-color','42.448766','-76.47631179999999',{0:[8,24],1:[8,24],2:[8,24],3:[8,24],4:[8,18],5:[12,19],6:[12,24]}],
    ['mann4c','Mann Library - First Floor','campus-bw, campus-color','42.448766','-76.47631179999999',{0:[8,24],1:[8,24],2:[8,24],3:[8,24],4:[8,18],5:[12,19],6:[12,24]}],
    ['mann5color','Mann Library - Basement B30 Area','campus-bw, campus-color','42.448766','-76.47631179999999',{0:[8,22],1:[8,22],2:[8,22],3:[8,22],4:[8,17],5:[0,0],6:[0,0]}],
    ['math-lib3c','Mallott Hall - Math Library - Fourth Floor','campus-bw, campus-color','42.4482224','-76.4802083',{0:[8,20],1:[8,20],2:[8,20],3:[8,20],4:[8,20],5:[0,0],6:[13,22]}],
    ['mpslab','Gates Hall - Room G23 (direct print; card reader? under construction as of Spr 2019)','campus-bw, campus-color','42.4449769','-76.4810912',None],
    ['mth-color','Myron Taylor Hall 2nd Floor Computer Lab (direct print; card reader?)','campus-bw, campus-color','42.444460','-76.486113',None],
    ['nytech-netprnt1','Roosevelt Island - Bloomberg Center Room 181 (direct print; card reader?)','campus-color','40.76050310000001','-73.9509934',None],
    ['nytech-netprnt2','NYTech - 111 8th Avenue (direct print; card reader?)','campus-color','42.4439614','-76.5018807',None],
    ['olin-lib-4thfloor','Olin Library - Room 425 - Fourth Floor','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['olin-lib-gradlounge','Olin Library Graduate Lounge','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['olin-lib5c','Olin Library - behind the reference desk','campus-bw, campus-color','42.447905','-76.484293',{0:[8,26],1:[8,26],2:[8,26],3:[8,26],4:[8,22],5:[10,22],6:[10,26]}],
    ['sage-301-color','Sage Hall Library - Room 302 - Third Floor Collaboration Space','campus-bw, campus-color','42.4458947','-76.4832581',None],
    ['sage-lib1-color','Sage Hall - Library - First Floor','campus-bw, campus-color','42.4458918','-76.4833009',None],
    ['sage-mfp1','Sage Johnson First Floor Room 101','campus-bw, campus-color','42.4458947','-76.4832581',None],
    ['sage-mfp2/sage-mfp3','Sage','campus-bw, campus-color','42.4397199','-76.49146619999999',None],
    ['scl-malott','Mallot (?)','campus-bw, campus-color','42.4482224','-76.4802083',None],
    ['sha-mslc-color','Nestle Library - west side of reference desk','campus-bw, campus-color','42.445541','-76.48215429999999',None],
    ['sibley1-b56','Sibley','campus-bw, campus-color','42.4509802','-76.4840158',None],
    ['sips-ps170-1c','Plant Science Building - Room 170','campus-bw, campus-color','42.4483258','-76.4770262',None],
    ['uris-lib-mfp1','Uris Library Austen Room','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['uris-lib-mfp2','Uris Main Library (direct print; card reader?)','campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['uris-lib2c','Uris Library - In Front of Circulation Desk','campus-bw, campus-color','42.447905','-76.484293',{0:[8,25],1:[8,25],2:[8,25],3:[8,25],4:[8,21],5:[12,21],6:[10,25]}],
    ['vetlib5','Schurman Hall - S1201 (direct print; card reader?)','campus-bw, campus-color','42.4480179','-76.4661765',None],
    ['vetschool-library1','Vet School Library','campus-bw, campus-color','42.4474921','-76.4658424',{0:[7.5,23],1:[7.5,23],2:[7.5,23],3:[7.5,23],4:[7.5,20],5:[10,20],6:[10,23]}]

]

TIMEOUT = 15

############################

'''Deprecated; function (and access key in __main__) left here for others' curiosity.'''
def find_me(key):
    '''returns user's coordinates - very imprecise!'''
    # API from https://ipstack.com/documentation
    send_url = 'http://api.ipstack.com/check?access_key='+key
    geo_req = requests.get(send_url)
    geo_json = json.loads(geo_req.text)
    latitude = geo_json['latitude']
    longitude = geo_json['longitude']
    return (latitude,longitude)

def find_me2(browser='S', quiet=False):
    '''Automatically open a Safari/Chrome window and extract GPS information.'''
    if browser=='S':
        driver = webdriver.Safari()
    else:
        source = str(os.getcwd())+'/chromedriver'
        # print(source)
        chrome_options = webdriver.ChromeOptions()
        if quiet:
            chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(source, options=chrome_options)

    ERR_MESSAGE = 'Error finding your location. Check your internet connection.'
    starttime = time.time()
    try:
        driver.get('https://www.gps-coordinates.net/')
        latlong = ''
        tick = time.time()
        while latlong == '' and (time.time()-starttime < TIMEOUT):
            time.sleep(.05)
            elems = driver.find_elements_by_id('latlong')
            if len(elems)>0:
                elem = elems[0]
                latlong = elem.get_attribute('value')
            tock = time.time()
            if tock-tick >= 1:
                tick = tock
                sys.stdout.write('... ')
                sys.stdout.flush()
        driver.close()
        print('')
        if latlong == '':
            print(ERR_MESSAGE)
            print('Connection timed out. Try running without quiet mode.')
            return
        return latlong
    except:
        print(ERR_MESSAGE)
        print('You can also enter your coordinate manually (argv "manual")')
        driver.close()



def gc_dist(lat_1,lon_1,lat_2,lon_2):
    '''find great circle distance (in km) between any two points'''
    # convert decimal degrees to radians
    lat_1, lon_1, lat_2, lon_2 = map(radians, [lat_1, lon_1, lat_2, lon_2])
    # haversine formula
    dlon = lon_2 - lon_1
    dlat = lat_2 - lat_1
    a = sin(dlat/2)**2 + cos(lat_1) * cos(lat_2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    #end of calculation
    #limit decimals
    return km

def min_dist(printers,me_pos,num_printers):
    '''
    for every printer:
        1. find printer location
        2. add printer to list
        3. sort printers and remove one if necessary
    return the list (with length num_printers)
    '''
    # fake distance for debugging - if code is successful, printer with name ''
    # should not be printed to console
    dists = [('',10000000000000,True,None)]
    for printer in printers:
        lat = float(printer[3])
        lon = float(printer[4])
        newdist = gc_dist(me_pos[0],me_pos[1],lat,lon)
        avail = available(printer[5])
        if avail[0]:
            dists.append((printer[1],newdist,avail[0],avail[1]))
        dists.sort(key=(lambda x: x[1]))
        if len(dists)>num_printers:
            dists.pop()
    dists.sort(key=(lambda x: x[1]))
    return dists

def available(schedule):
    '''return value of: printer's building is open. defaults to True.'''
    # TODO: schedules need to be manually entered, and many haven't.
    # --schedule information for cornell buildings is not centrally compiled,
    #   nor stored online in any standardized way
    #
    # schedule has format {0:[9.0,18.0],1:[8,19],...} or
    #          {0:[,],1:[,],2:[,],3:[,],4:[,],5:[,],6:[,]} where monday is 0
    date = time.localtime().tm_wday #date in eastern time
    hour = time.localtime().tm_hour+(time.localtime().tm_min)/60
    try:
        closes_in = int(60 * (schedule[date][1] - hour))
        return ((schedule[date][0] <= hour <= schedule[date][1]-.001),closes_in)
    except:
        return ('maybe',None)

def print_answer(dists):
    '''Print answer'''
    for i in range(len(dists)):
        if str(dists[i][2]) == 'True':
            second_part = 'is open. It closes in about ' + str(dists[i][3]) + ' minutes.\n'
        else:
            second_part = 'might be open.\n'
        time.sleep(0.1)
        print('Option '+str(i+1)+': go to printer \''+dists[i][0]+
                '\', which is '+str(round(dists[i][1],2))+' km away and ' + second_part)

def color(args):
    # return value of: user wants color printers
    # apparently this is fastest syntax - see https://stackoverflow.com/questions/3170055/test-if-lists-share-any-items-in-python
    return not set(args).isdisjoint(['color','c'])

def bw(args):
    # return value of: user wants bw printers
    return not set(args).isdisjoint(['bw','black and white','black-and-white'])


if __name__ == '__main__':
    args = [i.lower() for i in sys.argv]

    # num_printers is the only numerical argv, so any int is num_printers. defaults to 5.
    NUM_PRINTERS_WANTED = 5
    for i in args:
        try:
            NUM_PRINTERS_WANTED = int(i)
            if not 0 < NUM_PRINTERS_WANTED < 50:
                NUM_PRINTERS_WANTED = 5
        except:
            pass

    # find user coordinates
    if any('manual' in x for x in args):
        webbrowser.open_new("https://www.gps-coordinates.net/")
        prompt = 'Enter your coordinates (comma separation)'
        prompt += '\ntry https://www.gps-coordinates.net/\n0 to cancel\nCoors: '
        pos = [float(i.strip()) for i in input(prompt).split(',')]
        if pos == [0]:
            sys.exit()
    else:
        msg = 'Searching for GPS info - please wait a few seconds.'
        msg += '\nIf browser requests any permissions, accept; otherwise don\'t touch computer.'
        print(msg)
        if 'chrome' or 'quiet' in args:
            quiet = 'quiet' in args
            pos = find_me2(browser='C', quiet=quiet)
        else:
            pos = find_me2()

        # give up if selenium error occurs
        if pos is None:
            sys.exit(0)
        print('Found!')
        pos = [float(i) for i in pos.split(',')]
    '''except:
        key = '5458b0ab5799bb832c995cb32879cb85'
        if len(key) == 0:
            key = prompt('API key? (can get for free at https://ipstack.com/product) : ')
        pos = find_me(key)
    '''

    # wait a moment for dramatic effect; then perform distance calculations; then print answers in desired format
    time.sleep(1)
    if bw(args) or not color(args):
        print('black-and-white printers:\n')
        answer_bw = min_dist(printers_bw,pos,NUM_PRINTERS_WANTED)
        print_answer(answer_bw)
    if bw(args) and color(args):
        print('\n\n')
    if color(args) or not bw(args):
        print('color printers:\n')
        answer_color = min_dist(printers_color,pos,NUM_PRINTERS_WANTED)
        print_answer(answer_color)
