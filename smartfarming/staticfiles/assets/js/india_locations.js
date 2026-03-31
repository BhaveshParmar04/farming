// India States → Districts → Talukas → Villages
const INDIA_LOCATIONS = {
  "Andhra Pradesh": {
    "Anantapur": { "Anantapur": ["Anantapur","Gorantla","Kanaganapalle"], "Dharmavaram": ["Dharmavaram","Tadimarri","Amarapuram"], "Guntakal": ["Guntakal","Kosigi","Rayadurg"] },
    "Chittoor": { "Chittoor": ["Chittoor","Puthalapattu","Gangadhara Nellore"], "Tirupati": ["Tirupati","Renigunta","Chandragiri"], "Madanapalle": ["Madanapalle","Punganur","Pileru"] },
    "East Godavari": { "Kakinada": ["Kakinada","Peddapuram","Samalkot"], "Rajahmundry": ["Rajahmundry","Kovvur","Nidadavole"], "Amalapuram": ["Amalapuram","Mummidivaram","Razole"] },
    "Guntur": { "Guntur": ["Guntur","Mangalagiri","Tadepalle"], "Narasaraopet": ["Narasaraopet","Vinukonda","Sattenapalle"], "Tenali": ["Tenali","Repalle","Bapatla"] },
    "Krishna": { "Vijayawada": ["Vijayawada","Machilipatnam","Gudivada"], "Nuzvid": ["Nuzvid","Nandigama","Jaggayyapeta"], "Tiruvuru": ["Tiruvuru","Mylavaram","Vissannapet"] },
    "Kurnool": { "Kurnool": ["Kurnool","Nandyal","Adoni"], "Alur": ["Alur","Banaganapalle","Pattikonda"], "Yemmiganur": ["Yemmiganur","Mantralayam","Kosigi"] },
    "Nellore": { "Nellore": ["Nellore","Kavali","Gudur"], "Atmakur": ["Atmakur","Kovur","Allur"], "Sullurpeta": ["Sullurpeta","Naidupeta","Venkatagiri"] },
    "Prakasam": { "Ongole": ["Ongole","Chirala","Markapur"], "Kandukur": ["Kandukur","Podili","Giddalur"], "Darsi": ["Darsi","Kanigiri","Cumbum"] },
    "Srikakulam": { "Srikakulam": ["Srikakulam","Narasannapeta","Palakonda"], "Amadalavalasa": ["Amadalavalasa","Etcherla","Rajam"], "Tekkali": ["Tekkali","Kaviti","Mandasa"] },
    "Visakhapatnam": { "Visakhapatnam": ["Visakhapatnam","Bheemunipatnam","Anakapalle"], "Narsipatnam": ["Narsipatnam","Chodavaram","Paderu"], "Araku Valley": ["Araku Valley","Dumbriguda","Hukumpeta"] },
    "Vizianagaram": { "Vizianagaram": ["Vizianagaram","Bobbili","Parvathipuram"], "Salur": ["Salur","Gajapathinagaram","Cheepurupalle"], "Srungavarapukota": ["Srungavarapukota","Jami","Mentada"] },
    "West Godavari": { "Eluru": ["Eluru","Bhimavaram","Tadepalligudem"], "Narsapur": ["Narsapur","Palacole","Narasapuram"], "Jangareddygudem": ["Jangareddygudem","Kovvur","Polavaram"] }
  },
  "Arunachal Pradesh": {
    "Itanagar": { "Itanagar": ["Itanagar","Naharlagun","Nirjuli"], "Banderdewa": ["Banderdewa","Hoj","Doimukh"] },
    "Tawang": { "Tawang": ["Tawang","Lumla","Jang"], "Zemithang": ["Zemithang","Dudunghar","Shakti"] },
    "West Siang": { "Along": ["Along","Rumgong","Kaying"], "Mechuka": ["Mechuka","Tuting","Payum"] }
  },
  "Assam": {
    "Kamrup": { "Guwahati": ["Guwahati","Jalukbari","Dispur"], "Rangia": ["Rangia","Tihu","Nalbari"], "Hajo": ["Hajo","Sualkuchi","Palashbari"] },
    "Dibrugarh": { "Dibrugarh": ["Dibrugarh","Naharkatia","Duliajan"], "Moran": ["Moran","Barbaruah","Lahowal"], "Tingkhong": ["Tingkhong","Chabua","Khowang"] },
    "Jorhat": { "Jorhat": ["Jorhat","Mariani","Titabor"], "Teok": ["Teok","Majuli","Jorhat East"] },
    "Nagaon": { "Nagaon": ["Nagaon","Hojai","Lumding"], "Raha": ["Raha","Kaliabor","Samaguri"] },
    "Sonitpur": { "Tezpur": ["Tezpur","Dhekiajuli","Biswanath Chariali"], "Rangapara": ["Rangapara","Sootea","Gohpur"] }
  },
  "Bihar": {
    "Patna": { "Patna": ["Patna","Danapur","Phulwari"], "Patna Sahib": ["Patna Sahib","Barh","Bakhtiyarpur"], "Masaurhi": ["Masaurhi","Paliganj","Bikram"] },
    "Gaya": { "Gaya": ["Gaya","Bodh Gaya","Sherghati"], "Aurangabad": ["Aurangabad","Daudnagar","Rafiganj"], "Nawada": ["Nawada","Rajauli","Warsaliganj"] },
    "Muzaffarpur": { "Muzaffarpur": ["Muzaffarpur","Kanti","Motipur"], "Sitamarhi": ["Sitamarhi","Dumra","Pupri"], "Vaishali": ["Hajipur","Lalganj","Mahua"] },
    "Bhagalpur": { "Bhagalpur": ["Bhagalpur","Naugachia","Kahalgaon"], "Banka": ["Banka","Amarpur","Katoria"] },
    "Darbhanga": { "Darbhanga": ["Darbhanga","Benipur","Baheri"], "Madhubani": ["Madhubani","Jhanjharpur","Phulparas"] }
  },
  "Chhattisgarh": {
    "Raipur": { "Raipur": ["Raipur","Arang","Abhanpur"], "Durg": ["Durg","Bhilai","Patan"], "Rajnandgaon": ["Rajnandgaon","Dongargarh","Khairagarh"] },
    "Bilaspur": { "Bilaspur": ["Bilaspur","Mungeli","Takhatpur"], "Korba": ["Korba","Katghora","Pali"], "Janjgir": ["Janjgir","Champa","Sakti"] },
    "Bastar": { "Jagdalpur": ["Jagdalpur","Tokapal","Bastar"], "Kondagaon": ["Kondagaon","Narayanpur","Dantewada"] }
  },
  "Goa": {
    "North Goa": { "Panaji": ["Panaji","Mapusa","Calangute"], "Bicholim": ["Bicholim","Sanquelim","Pernem"], "Bardez": ["Bardez","Calangute","Candolim"] },
    "South Goa": { "Margao": ["Margao","Vasco da Gama","Ponda"], "Quepem": ["Quepem","Canacona","Sanguem"], "Salcete": ["Salcete","Benaulim","Colva"] }
  },
  "Gujarat": {
    "Ahmedabad": { "Daskroi": ["Sarkhej","Vatva","Narol","Odhav"], "Detroj-Rampura": ["Detroj","Rampura","Bavla"], "Dholka": ["Dholka","Dholera","Bagodara"], "Sanand": ["Sanand","Viramgam","Changodar"], "Ahmedabad City": ["Maninagar","Ghatlodia","Bopal","Chandkheda"] },
    "Surat": { "Surat City": ["Surat","Udhna","Katargam","Varachha"], "Bardoli": ["Bardoli","Mahuva","Vyara"], "Mandvi": ["Mandvi","Mangrol","Umarpada"], "Olpad": ["Olpad","Kamrej","Palsana"] },
    "Vadodara": { "Vadodara City": ["Vadodara","Makarpura","Waghodia"], "Karjan": ["Karjan","Dabhoi","Padra"], "Savli": ["Savli","Shinor","Desar"], "Chhota Udaipur": ["Chhota Udaipur","Kawant","Naswadi"] },
    "Rajkot": { "Rajkot City": ["Rajkot","Gondal","Jetpur"], "Jasdan": ["Jasdan","Vinchhiya","Paddhari"], "Kotda Sangani": ["Kotda Sangani","Lodhika","Dhoraji"], "Morbi": ["Morbi","Wankaner","Halvad"] },
    "Gandhinagar": { "Gandhinagar": ["Gandhinagar","Mansa","Kalol"], "Dehgam": ["Dehgam","Rancharda","Pethapur"], "Mansa": ["Mansa","Kadi","Vijapur"] },
    "Anand": { "Anand": ["Anand","Vallabh Vidyanagar","Karamsad"], "Khambhat": ["Khambhat","Borsad","Petlad"], "Umreth": ["Umreth","Tarapur","Sojitra"] },
    "Mehsana": { "Mehsana": ["Mehsana","Unjha","Visnagar"], "Kheralu": ["Kheralu","Satlasana","Vadnagar"], "Vijapur": ["Vijapur","Becharaji","Kadi"] },
    "Banaskantha": { "Palanpur": ["Palanpur","Deesa","Dhanera"], "Danta": ["Danta","Ambaji","Amirgadh"], "Tharad": ["Tharad","Vav","Radhanpur"] },
    "Patan": { "Patan": ["Patan","Sidhpur","Chanasma"], "Harij": ["Harij","Sami","Radhanpur"], "Sankheshwar": ["Sankheshwar","Shankheshwar","Sami"] },
    "Kutch": { "Bhuj": ["Bhuj","Anjar","Gandhidham"], "Mandvi": ["Mandvi","Mundra","Abdasa"], "Rapar": ["Rapar","Nakhatrana","Lakhpat"] },
    "Amreli": {
      "Amreli": ["Amreli","Chhapra","Damnagar","Kunkavav","Vadia","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Rampur","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Mota Khijadiya","Nana Khijadiya","Rajula","Savarkundla","Savar","Pipavav"],
      "Bagasara": ["Bagasara","Barvala","Khirasara","Sanosara","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Mota Khijadiya","Nana Khijadiya","Rajpara","Vadiya","Pipli","Sukhpur","Rampur","Chhapra","Kunkavav","Vadia","Damnagar"],
      "Babra": ["Babra","Chhapra","Kunkavav","Vadia","Damnagar","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Rampur","Vadiya","Khodiyar","Anandpur","Bhimora"],
      "Dhari": ["Dhari","Mota Dahisara","Nana Dahisara","Rampur","Sukhpur","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Mota Khijadiya","Nana Khijadiya","Rajpara","Vadiya","Pipli","Barvala","Sanosara","Khirasara","Chhapra","Kunkavav","Vadia","Damnagar","Khambha"],
      "Jafrabad": ["Jafrabad","Pipavav","Savar","Rajula","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Rampur","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad"],
      "Khambha": ["Khambha","Pipli","Rajpara","Vadiya","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Mota Dahisara","Nana Dahisara","Rampur","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Mota Khijadiya","Nana Khijadiya","Chhapra","Kunkavav","Vadia","Damnagar"],
      "Kukavav": ["Kukavav","Vadia","Rampur","Chhapra","Kunkavav","Damnagar","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar"],
      "Lathi": ["Lathi","Hadmatiya","Mota Khijadiya","Nana Khijadiya","Rajpara","Vadiya","Pipli","Sukhpur","Barvala","Sanosara","Khirasara","Mota Dahisara","Nana Dahisara","Rampur","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Chhapra","Kunkavav","Vadia","Damnagar","Khambha"],
      "Lilia": ["Lilia","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Rampur","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Mota Khijadiya","Nana Khijadiya","Chhapra","Kunkavav","Vadia","Damnagar"],
      "Rajula": ["Rajula","Jafrabad","Pipavav","Savar","Khambha","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Rampur","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Mota Khijadiya","Nana Khijadiya"],
      "Savarkundla": ["Savarkundla","Khambha","Rampur","Vadia","Chhapra","Kunkavav","Damnagar","Rajpara","Hadmatiya","Sukhpur","Barvala","Sanosara","Khirasara","Pipli","Mota Dahisara","Nana Dahisara","Vadiya","Khodiyar","Anandpur","Bhimora","Galiyavad","Jesar","Kukavav","Liliya","Mota Khijadiya","Nana Khijadiya"]
    },
    "Bhavnagar": { "Bhavnagar": ["Bhavnagar","Sihor","Palitana"], "Gariadhar": ["Gariadhar","Talaja","Mahuva"], "Ghogha": ["Ghogha","Vallabhipur","Umrala"] },
    "Jamnagar": { "Jamnagar": ["Jamnagar","Dwarka","Khambhalia"], "Kalavad": ["Kalavad","Lalpur","Dhrol"], "Jodiya": ["Jodiya","Bhanvad","Okha"] },
    "Junagadh": { "Junagadh": ["Junagadh","Keshod","Veraval"], "Mangrol": ["Mangrol","Una","Kodinar"], "Visavadar": ["Visavadar","Talala","Sutrapada"] },
    "Porbandar": { "Porbandar": ["Porbandar","Ranavav","Kutiyana"] },
    "Surendranagar": { "Surendranagar": ["Surendranagar","Wadhwan","Chotila"], "Dhrangadhra": ["Dhrangadhra","Halvad","Limbdi"], "Lakhtar": ["Lakhtar","Sayla","Muli"] },
    "Narmada": { "Rajpipla": ["Rajpipla","Nandod","Dediapada"], "Garudeshwar": ["Garudeshwar","Tilakwada","Sagbara"] },
    "Bharuch": { "Bharuch": ["Bharuch","Ankleshwar","Jambusar"], "Vagra": ["Vagra","Amod","Hansot"], "Jhagadia": ["Jhagadia","Netrang","Valia"] },
    "Navsari": { "Navsari": ["Navsari","Gandevi","Chikhli"], "Jalalpore": ["Jalalpore","Vansda","Khergam"] },
    "Valsad": { "Valsad": ["Valsad","Vapi","Pardi"], "Umbergaon": ["Umbergaon","Dharampur","Kaprada"] },
    "Tapi": { "Vyara": ["Vyara","Songadh","Nizar"], "Uchchhal": ["Uchchhal","Valod","Dolvan"] },
    "Dahod": { "Dahod": ["Dahod","Limkheda","Garbada"], "Devgadh Baria": ["Devgadh Baria","Fatepura","Zalod"] },
    "Panchmahal": { "Godhra": ["Godhra","Halol","Kalol"], "Lunawada": ["Lunawada","Santrampur","Morva Hadaf"] },
    "Mahisagar": { "Lunawada": ["Lunawada","Balasinor","Khanpur"], "Santrampur": ["Santrampur","Kadana","Virpur"] },
    "Aravalli": { "Modasa": ["Modasa","Bayad","Dhansura"], "Malpur": ["Malpur","Meghraj","Bhiloda"] },
    "Sabarkantha": { "Himmatnagar": ["Himmatnagar","Idar","Talod"], "Prantij": ["Prantij","Khedbrahma","Vadali"] },
    "Kheda": { "Nadiad": ["Nadiad","Kapadvanj","Matar"], "Mahudha": ["Mahudha","Thasra","Kathlal"] },
    "Botad": { "Botad": ["Botad","Gadhada","Barwala"] },
    "Morbi": { "Morbi": ["Morbi","Wankaner","Tankara"] },
    "Devbhoomi Dwarka": { "Dwarka": ["Dwarka","Khambhalia","Bhanvad"] },
    "Gir Somnath": { "Veraval": ["Veraval","Somnath","Una"] }
  },
  "Haryana": {
    "Ambala": { "Ambala": ["Ambala City","Ambala Cantonment","Barara"], "Naraingarh": ["Naraingarh","Mullana","Shahzadpur"] },
    "Faridabad": { "Faridabad": ["Faridabad","Ballabhgarh","Tigaon"], "Palwal": ["Palwal","Hathin","Hodal"] },
    "Gurugram": { "Gurugram": ["Gurugram","Manesar","Pataudi"], "Sohna": ["Sohna","Nuh","Tauru"] },
    "Hisar": { "Hisar": ["Hisar","Hansi","Barwala"], "Fatehabad": ["Fatehabad","Tohana","Ratia"] },
    "Karnal": { "Karnal": ["Karnal","Nilokheri","Assandh"], "Panipat": ["Panipat","Samalkha","Israna"] },
    "Rohtak": { "Rohtak": ["Rohtak","Meham","Kalanaur"], "Jhajjar": ["Jhajjar","Bahadurgarh","Beri"] },
    "Sonipat": { "Sonipat": ["Sonipat","Gohana","Kharkhoda"], "Kundli": ["Kundli","Murthal","Gannaur"] },
    "Yamunanagar": { "Yamunanagar": ["Yamunanagar","Jagadhri","Bilaspur"], "Radaur": ["Radaur","Chhachhrauli","Sadhaura"] }
  },
  "Himachal Pradesh": {
    "Shimla": { "Shimla": ["Shimla","Rampur","Rohru"], "Theog": ["Theog","Jubbal","Kotkhai"] },
    "Kangra": { "Dharamsala": ["Dharamsala","Palampur","Nurpur"], "Dehra": ["Dehra","Jawali","Indora"] },
    "Mandi": { "Mandi": ["Mandi","Sundernagar","Jogindernagar"], "Sarkaghat": ["Sarkaghat","Chachyot","Karsog"] },
    "Kullu": { "Kullu": ["Kullu","Manali","Banjar"], "Anni": ["Anni","Nirmand","Sainj"] }
  },
  "Jharkhand": {
    "Ranchi": { "Ranchi": ["Ranchi","Hatia","Kanke"], "Bundu": ["Bundu","Tamar","Silli"] },
    "Dhanbad": { "Dhanbad": ["Dhanbad","Jharia","Sindri"], "Topchanchi": ["Topchanchi","Govindpur","Nirsa"] },
    "Jamshedpur": { "Jamshedpur": ["Jamshedpur","Jugsalai","Mango"], "Boram": ["Boram","Potka","Baharagora"] },
    "Bokaro": { "Bokaro": ["Bokaro Steel City","Chas","Petarbar"], "Gomia": ["Gomia","Bermo","Chandankiyari"] }
  },
  "Karnataka": {
    "Bangalore Urban": { "Bangalore": ["Bangalore","Yelahanka","Whitefield"], "Anekal": ["Anekal","Attibele","Sarjapur"] },
    "Mysuru": { "Mysuru": ["Mysuru","Nanjangud","T Narasipura"], "Hunsur": ["Hunsur","Piriyapatna","K R Nagar"] },
    "Belagavi": { "Belagavi": ["Belagavi","Gokak","Chikodi"], "Athani": ["Athani","Raibag","Hukkeri"] },
    "Dharwad": { "Dharwad": ["Dharwad","Hubli","Kundgol"], "Kalghatgi": ["Kalghatgi","Navalgund","Annigeri"] },
    "Tumkur": { "Tumkur": ["Tumkur","Tiptur","Gubbi"], "Madhugiri": ["Madhugiri","Pavagada","Koratagere"] },
    "Dakshina Kannada": { "Mangaluru": ["Mangaluru","Puttur","Sullia"], "Bantwal": ["Bantwal","Belthangady","Kadaba"] },
    "Shivamogga": { "Shivamogga": ["Shivamogga","Bhadravati","Sagar"], "Soraba": ["Soraba","Shikaripura","Hosanagara"] }
  },
  "Kerala": {
    "Thiruvananthapuram": { "Thiruvananthapuram": ["Thiruvananthapuram","Neyyattinkara","Attingal"], "Nedumangad": ["Nedumangad","Varkala","Chirayinkeezhu"] },
    "Ernakulam": { "Ernakulam": ["Ernakulam","Aluva","Perumbavoor"], "Kothamangalam": ["Kothamangalam","Muvattupuzha","Piravom"] },
    "Kozhikode": { "Kozhikode": ["Kozhikode","Vadakara","Koyilandy"], "Thamarassery": ["Thamarassery","Perambra","Koduvally"] },
    "Thrissur": { "Thrissur": ["Thrissur","Chalakudy","Kodungallur"], "Kunnamkulam": ["Kunnamkulam","Guruvayur","Irinjalakuda"] },
    "Palakkad": { "Palakkad": ["Palakkad","Ottapalam","Shoranur"], "Mannarkkad": ["Mannarkkad","Alathur","Chittur"] }
  },
  "Madhya Pradesh": {
    "Bhopal": { "Bhopal": ["Bhopal","Berasia","Phanda"], "Huzur": ["Huzur","Sehore","Ashta"] },
    "Indore": { "Indore": ["Indore","Mhow","Depalpur"], "Sanwer": ["Sanwer","Hatod","Manpur"] },
    "Gwalior": { "Gwalior": ["Gwalior","Morar","Lashkar"], "Bhitarwar": ["Bhitarwar","Dabra","Pichhore"] },
    "Jabalpur": { "Jabalpur": ["Jabalpur","Sihora","Patan"], "Kundam": ["Kundam","Shahpura","Majholi"] },
    "Ujjain": { "Ujjain": ["Ujjain","Nagda","Mahidpur"], "Tarana": ["Tarana","Khachrod","Ghatiya"] },
    "Rewa": { "Rewa": ["Rewa","Mauganj","Teonthar"], "Sirmaur": ["Sirmaur","Hanumana","Naigarhi"] },
    "Sagar": { "Sagar": ["Sagar","Banda","Rahatgarh"], "Khurai": ["Khurai","Deori","Rehli"] }
  },
  "Maharashtra": {
    "Mumbai City": { "Mumbai": ["Colaba","Bandra","Andheri","Borivali","Kurla"] },
    "Mumbai Suburban": { "Andheri": ["Andheri","Jogeshwari","Vile Parle"], "Borivali": ["Borivali","Kandivali","Malad"], "Kurla": ["Kurla","Ghatkopar","Vikhroli"] },
    "Pune": { "Pune": ["Pune","Pimpri","Chinchwad"], "Haveli": ["Hadapsar","Khadki","Wagholi"], "Maval": ["Maval","Talegaon","Lonavala"], "Baramati": ["Baramati","Indapur","Daund"] },
    "Nashik": { "Nashik": ["Nashik","Deolali","Igatpuri"], "Niphad": ["Niphad","Sinnar","Dindori"], "Malegaon": ["Malegaon","Satana","Chandwad"] },
    "Nagpur": { "Nagpur": ["Nagpur","Kamptee","Hingna"], "Ramtek": ["Ramtek","Parseoni","Mouda"], "Umred": ["Umred","Bhiwapur","Kuhi"] },
    "Aurangabad": { "Aurangabad": ["Aurangabad","Paithan","Gangapur"], "Kannad": ["Kannad","Sillod","Soegaon"], "Vaijapur": ["Vaijapur","Khuldabad","Phulambri"] },
    "Solapur": { "Solapur": ["Solapur","Akkalkot","Pandharpur"], "Barshi": ["Barshi","Mohol","Malshiras"], "Mangalvedhe": ["Mangalvedhe","Sangola","Karmala"] },
    "Kolhapur": { "Kolhapur": ["Kolhapur","Ichalkaranji","Jaysingpur"], "Karvir": ["Karvir","Hatkanangle","Shirol"], "Panhala": ["Panhala","Kagal","Radhanagari"] },
    "Satara": { "Satara": ["Satara","Karad","Wai"], "Patan": ["Patan","Mahabaleshwar","Jawali"], "Khatav": ["Khatav","Koregaon","Phaltan"] },
    "Sangli": { "Sangli": ["Sangli","Miraj","Kupwad"], "Walwa": ["Walwa","Shirala","Palus"], "Jat": ["Jat","Atpadi","Kavthe Mahankal"] },
    "Raigad": { "Alibag": ["Alibag","Pen","Panvel"], "Mahad": ["Mahad","Poladpur","Mangaon"], "Uran": ["Uran","Karjat","Khalapur"] },
    "Thane": { "Thane": ["Thane","Kalyan","Dombivli"], "Bhiwandi": ["Bhiwandi","Shahapur","Murbad"], "Ulhasnagar": ["Ulhasnagar","Ambernath","Badlapur"] },
    "Amravati": { "Amravati": ["Amravati","Achalpur","Daryapur"], "Chandur Bazar": ["Chandur Bazar","Morshi","Warud"], "Anjangaon": ["Anjangaon","Dharni","Chikhaldara"] },
    "Akola": { "Akola": ["Akola","Akot","Telhara"], "Balapur": ["Balapur","Patur","Murtizapur"] },
    "Washim": { "Washim": ["Washim","Malegaon","Risod"], "Mangrulpir": ["Mangrulpir","Karanja","Manora"] },
    "Yavatmal": { "Yavatmal": ["Yavatmal","Wani","Pusad"], "Darwha": ["Darwha","Digras","Ner"], "Umarkhed": ["Umarkhed","Mahagaon","Kelapur"] },
    "Nanded": { "Nanded": ["Nanded","Deglur","Mukhed"], "Hadgaon": ["Hadgaon","Kinwat","Bhokar"], "Loha": ["Loha","Naigaon","Kandhar"] },
    "Latur": { "Latur": ["Latur","Udgir","Ausa"], "Nilanga": ["Nilanga","Chakur","Renapur"], "Ahmedpur": ["Ahmedpur","Shirur Anantpal","Jalkot"] },
    "Osmanabad": { "Osmanabad": ["Osmanabad","Tuljapur","Omerga"], "Paranda": ["Paranda","Kalamb","Bhum"] },
    "Beed": { "Beed": ["Beed","Ambejogai","Georai"], "Parli": ["Parli","Patoda","Shirur Kasar"], "Ashti": ["Ashti","Kaij","Dharur"] },
    "Jalna": { "Jalna": ["Jalna","Ambad","Badnapur"], "Partur": ["Partur","Mantha","Bhokardan"] },
    "Parbhani": { "Parbhani": ["Parbhani","Gangakhed","Pathri"], "Jintur": ["Jintur","Manwath","Selu"] },
    "Hingoli": { "Hingoli": ["Hingoli","Sengaon","Kalamnuri"], "Basmath": ["Basmath","Aundha Nagnath","Aundha"] },
    "Buldhana": { "Buldhana": ["Buldhana","Khamgaon","Malkapur"], "Chikhli": ["Chikhli","Mehkar","Lonar"], "Motala": ["Motala","Nandura","Jalgaon Jamod"] },
    "Jalgaon": { "Jalgaon": ["Jalgaon","Bhusawal","Amalner"], "Chalisgaon": ["Chalisgaon","Pachora","Erandol"], "Jamner": ["Jamner","Dharangaon","Muktainagar"] },
    "Dhule": { "Dhule": ["Dhule","Shirpur","Sakri"], "Sindkheda": ["Sindkheda","Shindkheda","Dondaicha"] },
    "Nandurbar": { "Nandurbar": ["Nandurbar","Shahada","Taloda"], "Akkalkuwa": ["Akkalkuwa","Akrani","Nawapur"] },
    "Ahmednagar": { "Ahmednagar": ["Ahmednagar","Shrirampur","Kopargaon"], "Rahata": ["Rahata","Rahuri","Newasa"], "Sangamner": ["Sangamner","Akole","Parner"] },
    "Ratnagiri": { "Ratnagiri": ["Ratnagiri","Chiplun","Khed"], "Guhagar": ["Guhagar","Dapoli","Mandangad"], "Lanja": ["Lanja","Rajapur","Sangameshwar"] },
    "Sindhudurg": { "Kudal": ["Kudal","Sawantwadi","Vengurla"], "Malvan": ["Malvan","Devgad","Kankavli"] },
    "Chandrapur": { "Chandrapur": ["Chandrapur","Warora","Mul"], "Rajura": ["Rajura","Bhadravati","Gondpipri"], "Chimur": ["Chimur","Nagbhid","Sindewahi"] },
    "Gadchiroli": { "Gadchiroli": ["Gadchiroli","Armori","Desaiganj"], "Aheri": ["Aheri","Sironcha","Etapalli"] },
    "Gondia": { "Gondia": ["Gondia","Tirora","Goregaon"], "Arjuni Morgaon": ["Arjuni Morgaon","Amgaon","Deori"] },
    "Bhandara": { "Bhandara": ["Bhandara","Tumsar","Mohadi"], "Sakoli": ["Sakoli","Lakhani","Pauni"] }
  },
  "Manipur": {
    "Imphal East": { "Imphal": ["Imphal","Porompat","Heingang"], "Jiribam": ["Jiribam","Tentha","Keirenphabi"] },
    "Imphal West": { "Lamphel": ["Lamphel","Patsoi","Wangoi"], "Bishnupur": ["Bishnupur","Moirang","Nambol"] }
  },
  "Meghalaya": {
    "East Khasi Hills": { "Shillong": ["Shillong","Cherrapunji","Mawsynram"], "Mawkyrwat": ["Mawkyrwat","Nongstoin","Mairang"] },
    "West Garo Hills": { "Tura": ["Tura","Phulbari","Dalu"], "Selsella": ["Selsella","Tikrikilla","Dadenggre"] }
  },
  "Mizoram": {
    "Aizawl": { "Aizawl": ["Aizawl","Durtlang","Zemabawk"], "Thingsulthliah": ["Thingsulthliah","Kolasib","Saitual"] },
    "Lunglei": { "Lunglei": ["Lunglei","Tlabung","Hnahthial"] }
  },
  "Nagaland": {
    "Kohima": { "Kohima": ["Kohima","Zubza","Kigwema"], "Jakhama": ["Jakhama","Viswema","Mima"] },
    "Dimapur": { "Dimapur": ["Dimapur","Chumukedima","Medziphema"] }
  },
  "Odisha": {
    "Khordha": { "Bhubaneswar": ["Bhubaneswar","Jatni","Khordha"], "Balianta": ["Balianta","Balipatna","Tangi"] },
    "Cuttack": { "Cuttack": ["Cuttack","Choudwar","Athagarh"], "Banki": ["Banki","Tigiria","Baramba"] },
    "Ganjam": { "Berhampur": ["Berhampur","Chhatrapur","Bhanjanagar"], "Aska": ["Aska","Phulbani","Digapahandi"] },
    "Puri": { "Puri": ["Puri","Konark","Nimapara"], "Pipili": ["Pipili","Brahmagiri","Kakatpur"] },
    "Sambalpur": { "Sambalpur": ["Sambalpur","Burla","Hirakud"], "Kuchinda": ["Kuchinda","Rairakhol","Bamra"] }
  },
  "Punjab": {
    "Amritsar": { "Amritsar": ["Amritsar","Ajnala","Baba Bakala"], "Majitha": ["Majitha","Rayya","Jandiala Guru"] },
    "Ludhiana": { "Ludhiana": ["Ludhiana","Khanna","Samrala"], "Jagraon": ["Jagraon","Raikot","Machhiwara"] },
    "Jalandhar": { "Jalandhar": ["Jalandhar","Nakodar","Phillaur"], "Shahkot": ["Shahkot","Lohian","Kartarpur"] },
    "Patiala": { "Patiala": ["Patiala","Rajpura","Nabha"], "Samana": ["Samana","Patran","Sanaur"] },
    "Bathinda": { "Bathinda": ["Bathinda","Rampura Phul","Talwandi Sabo"], "Nathana": ["Nathana","Phul","Maur"] },
    "Mohali": { "Mohali": ["Mohali","Kharar","Dera Bassi"], "Morinda": ["Morinda","Ropar","Anandpur Sahib"] },
    "Gurdaspur": { "Gurdaspur": ["Gurdaspur","Batala","Pathankot"], "Dinanagar": ["Dinanagar","Dhariwal","Dera Baba Nanak"] }
  },
  "Rajasthan": {
    "Jaipur": { "Jaipur": ["Jaipur","Sanganer","Amber"], "Chaksu": ["Chaksu","Phagi","Bassi"], "Shahpura": ["Shahpura","Viratnagar","Kotputli"] },
    "Jodhpur": { "Jodhpur": ["Jodhpur","Phalodi","Bilara"], "Osian": ["Osian","Bhopalgarh","Shergarh"], "Luni": ["Luni","Pipar City","Balesar"] },
    "Udaipur": { "Udaipur": ["Udaipur","Nathdwara","Rajsamand"], "Girwa": ["Girwa","Mavli","Vallabhnagar"], "Salumbar": ["Salumbar","Sarada","Lasadiya"] },
    "Kota": { "Kota": ["Kota","Sangod","Ladpura"], "Ramganj Mandi": ["Ramganj Mandi","Baran","Anta"] },
    "Ajmer": { "Ajmer": ["Ajmer","Kishangarh","Beawar"], "Nasirabad": ["Nasirabad","Pushkar","Kekri"] },
    "Bikaner": { "Bikaner": ["Bikaner","Nokha","Lunkaransar"], "Kolayat": ["Kolayat","Khajuwala","Bajju"] },
    "Alwar": { "Alwar": ["Alwar","Behror","Rajgarh"], "Ramgarh": ["Ramgarh","Laxmangarh","Kishangarh Bas"] },
    "Bharatpur": { "Bharatpur": ["Bharatpur","Deeg","Nagar"], "Kumher": ["Kumher","Nadbai","Weir"] },
    "Sikar": { "Sikar": ["Sikar","Fatehpur","Laxmangarh"], "Neem Ka Thana": ["Neem Ka Thana","Srimadhopur","Khandela"] }
  },
  "Sikkim": {
    "East Sikkim": { "Gangtok": ["Gangtok","Ranipool","Pakyong"], "Rongli": ["Rongli","Aritar","Rhenock"] },
    "West Sikkim": { "Gyalshing": ["Gyalshing","Legship","Soreng"] }
  },
  "Tamil Nadu": {
    "Chennai": { "Chennai": ["Chennai","Ambattur","Avadi"], "Tambaram": ["Tambaram","Pallavaram","Chrompet"] },
    "Coimbatore": { "Coimbatore": ["Coimbatore","Tiruppur","Pollachi"], "Mettupalayam": ["Mettupalayam","Annur","Sulur"] },
    "Madurai": { "Madurai": ["Madurai","Melur","Usilampatti"], "Thirumangalam": ["Thirumangalam","Peraiyur","Kalligudi"] },
    "Salem": { "Salem": ["Salem","Mettur","Omalur"], "Attur": ["Attur","Yercaud","Gangavalli"] },
    "Tiruchirappalli": { "Tiruchirappalli": ["Tiruchirappalli","Srirangam","Lalgudi"], "Musiri": ["Musiri","Thuraiyur","Manapparai"] },
    "Tirunelveli": { "Tirunelveli": ["Tirunelveli","Palayamkottai","Nanguneri"], "Ambasamudram": ["Ambasamudram","Cheranmahadevi","Tenkasi"] },
    "Vellore": { "Vellore": ["Vellore","Katpadi","Gudiyatham"], "Arakkonam": ["Arakkonam","Arcot","Sholinghur"] },
    "Erode": { "Erode": ["Erode","Bhavani","Gobichettipalayam"], "Perundurai": ["Perundurai","Sathyamangalam","Anthiyur"] }
  },
  "Telangana": {
    "Hyderabad": { "Hyderabad": ["Hyderabad","Secunderabad","Kukatpally"], "LB Nagar": ["LB Nagar","Uppal","Hayathnagar"] },
    "Rangareddy": { "Rangareddy": ["Rangareddy","Shamshabad","Rajendranagar"], "Chevella": ["Chevella","Vikarabad","Tandur"] },
    "Warangal": { "Warangal": ["Warangal","Hanamkonda","Kazipet"], "Narsampet": ["Narsampet","Parkal","Mulugu"] },
    "Karimnagar": { "Karimnagar": ["Karimnagar","Huzurabad","Jagtial"], "Sircilla": ["Sircilla","Vemulawada","Koratla"] },
    "Nizamabad": { "Nizamabad": ["Nizamabad","Bodhan","Armoor"], "Banswada": ["Banswada","Kamareddy","Yellareddy"] },
    "Khammam": { "Khammam": ["Khammam","Kothagudem","Bhadrachalam"], "Sattupalle": ["Sattupalle","Madhira","Wyra"] }
  },
  "Tripura": {
    "West Tripura": { "Agartala": ["Agartala","Mohanpur","Jirania"], "Majlishpur": ["Majlishpur","Bishalgarh","Sonamura"] },
    "North Tripura": { "Dharmanagar": ["Dharmanagar","Kailashahar","Kumarghat"] }
  },
  "Uttar Pradesh": {
    "Lucknow": { "Lucknow": ["Lucknow","Malihabad","Bakshi Ka Talab"], "Mohanlalganj": ["Mohanlalganj","Gosainganj","Sarojini Nagar"] },
    "Agra": { "Agra": ["Agra","Firozabad","Fatehabad"], "Kheragarh": ["Kheragarh","Bah","Etmadpur"] },
    "Varanasi": { "Varanasi": ["Varanasi","Sarnath","Ramnagar"], "Pindra": ["Pindra","Chiraigaon","Arajiline"] },
    "Kanpur": { "Kanpur": ["Kanpur","Bilhaur","Ghatampur"], "Kalyanpur": ["Kalyanpur","Bithoor","Shivrajpur"] },
    "Allahabad": { "Allahabad": ["Allahabad","Phulpur","Soraon"], "Meja": ["Meja","Handia","Karchhana"] },
    "Meerut": { "Meerut": ["Meerut","Hapur","Modinagar"], "Sardhana": ["Sardhana","Kithore","Mawana"] },
    "Mathura": { "Mathura": ["Mathura","Vrindavan","Govardhan"], "Chhata": ["Chhata","Mant","Baldeo"] },
    "Gorakhpur": { "Gorakhpur": ["Gorakhpur","Deoria","Kushinagar"], "Sahjanwa": ["Sahjanwa","Campierganj","Gola"] },
    "Bareilly": { "Bareilly": ["Bareilly","Pilibhit","Shahjahanpur"], "Faridpur": ["Faridpur","Nawabganj","Baheri"] },
    "Moradabad": { "Moradabad": ["Moradabad","Rampur","Sambhal"], "Amroha": ["Amroha","Hasanpur","Gajraula"] }
  },
  "Uttarakhand": {
    "Dehradun": { "Dehradun": ["Dehradun","Rishikesh","Doiwala"], "Vikasnagar": ["Vikasnagar","Chakrata","Kalsi"] },
    "Haridwar": { "Haridwar": ["Haridwar","Roorkee","Laksar"], "Bhagwanpur": ["Bhagwanpur","Manglaur","Narsan"] },
    "Nainital": { "Nainital": ["Nainital","Haldwani","Ramnagar"], "Bhimtal": ["Bhimtal","Dhari","Okhalkanda"] },
    "Almora": { "Almora": ["Almora","Ranikhet","Someshwar"], "Dwarahat": ["Dwarahat","Chaukhutia","Salt"] }
  },
  "West Bengal": {
    "Kolkata": { "Kolkata": ["Kolkata","Howrah","Dum Dum"], "Jadavpur": ["Jadavpur","Behala","Tollygunge"] },
    "North 24 Parganas": { "Barasat": ["Barasat","Basirhat","Bangaon"], "Barrackpore": ["Barrackpore","Titagarh","Khardah"] },
    "South 24 Parganas": { "Alipore": ["Alipore","Diamond Harbour","Kakdwip"], "Baruipur": ["Baruipur","Sonarpur","Jaynagar"] },
    "Murshidabad": { "Berhampore": ["Berhampore","Jiaganj","Lalbagh"], "Kandi": ["Kandi","Khargram","Burwan"] },
    "Bardhaman": { "Bardhaman": ["Bardhaman","Asansol","Durgapur"], "Kalna": ["Kalna","Katwa","Memari"] },
    "Hooghly": { "Chinsurah": ["Chinsurah","Serampore","Chandannagar"], "Arambagh": ["Arambagh","Goghat","Khanakul"] },
    "Nadia": { "Krishnanagar": ["Krishnanagar","Ranaghat","Kalyani"], "Chakdaha": ["Chakdaha","Santipur","Nabadwip"] },
    "Jalpaiguri": { "Jalpaiguri": ["Jalpaiguri","Alipurduar","Dhupguri"], "Mal": ["Mal","Nagrakata","Matiali"] },
    "Darjeeling": { "Darjeeling": ["Darjeeling","Siliguri","Kurseong"], "Mirik": ["Mirik","Jorebunglow","Kalimpong"] }
  }
};
