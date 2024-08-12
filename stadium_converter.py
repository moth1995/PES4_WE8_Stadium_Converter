import struct, io, zlib, os, sys, traceback, logging
from pathlib import Path

"""
0 -> 0
1 -> 1
2 -> 2
3 -> 3
4 -> 4
5 -> 5
6 -> 7
7 -> NOT NEEDED, SKIP
8 -> 10
9 -> 11
10 -> 12
11 -> 13
12 -> 14
13 -> 17
14 -> NOT NEEDED, SKIP
15 -> NOT NEEDED, SKIP
16 -> NOT NEEDED, SKIP
17 -> NOT NEEDED, SKIP
18 -> NOT NEEDED, SKIP
19 -> NOT NEEDED, SKIP
20 -> NOT NEEDED, SKIP
21 -> NOT NEEDED, SKIP
22 -> 23
23 -> 24
24 -> 25
25 -> 26
26 -> 27
"""

ZLIB_MAGIC_NUMBER = bytearray([0x00, 0x06, 0x01, 0x00])
FOLDER_MAGIC_NUMBER = bytearray([0x00, 0x06, 0x00, 0x00])

STAD_NAMES = {
    0: 'Sapporo Dome (Kanji Dome)',
    1: 'Kashima Soccer Stadium (Dietro Monte)',
    2: 'Yokohama International/Nissan Stadium (Porto Folio)',
    3: 'Nagai Stadium (Queensland Park)',
    4: 'Olympic Stadium (Haze Hills)',
    5: 'Oita Bank Dome (Occhio del Mar)',
    6: 'Club House/TRAINING GROUND',
    7: 'San Siro (Lombardi Colosseum)',
    8: 'Camp Nou (Catalonia Stadium)',
    9: 'Highbury (North East Stadium)',
    10: 'Amsterdam Arena (Orange Arena)',
    11: 'Olympiastadion (Bayern Stadium)',
    12: 'Stade Louis II (Monaco Stadium)',
    13: 'Old Trafford (Trad Brick Stadium)',
    14: 'Seoul World Cup Stadium (Nakhon Ratchasima)',
    15: 'Estadio Alberto J. Armando/La Bombonera (Gran Chaco)',
    16: 'Vodacom Park Stadium/Free State (Cuito Canavale)',
    17: 'Estadio Nacional/Columbus Crew (Amerigo Atlantis)',
    18: 'Stadio Delle Alpi (Old Lady Stadium)',
    19: 'Stadio Olimpico (Cesar Stadium)',
    20: 'Ennio Tardini (Emelia Stadium)',
    21: 'Stamford Bridge (Blue Bridge Stadium)',
    22: 'Anfield Stadium (Red Cauldron)',
    23: 'Parc des Princes (Lutecia Park)',
    24: 'Stade Velodrome (Massilia Stadium)',
    25: 'Westfalenstadion (Borussia Stadion)',
    26: 'Rasunda Stadium (Stockholm Arena)',
    27: 'St. James Park (Magpie Park)',
    28: 'De Kuip Stadium (Rotterdam Stadion)',
}

STAD_SHORT_NAME = {
  0: 'stj01',
  1: 'stj02',
  2: 'stj07',
  3: 'stj12',
  4: 'stj16',
  5: 'stj30',
  6: 'stw00',
  7: 'stw01',
  8: 'stw02',
  9: 'stw03',
  10: 'stw04',
  11: 'stw05',
  12: 'stw06',
  13: 'stw07',
  14: 'stw08',
  15: 'stw09',
  16: 'stw10',
  17: 'stw11',
  18: 'stw12',
  19: 'stw13',
  20: 'stw14',
  21: 'stw15',
  22: 'stw16',
  23: 'stw17',
  24: 'stw18',
  25: 'stw20',
  26: 'stw21',
  27: 'stw22',
  28: 'stw23',
}

FOLDERS_NAMES = [
    "1_day_fine",
    "2_day_rain",
    "4_night_fine",
    "5_night_rain",
]

CROWD_FILES_NAMES = [
    "crowd_a0.str",
    "crowd_a1.str",
    "crowd_a2.str",
    "crowd_a3.str",
    "crowd_h0.str",
    "crowd_h1.str",
    "crowd_h2.str",
    "crowd_h3.str",
]

NAMES_CONVERTION = {
    "1_day_fine" : "df",
    "2_day_rain" : "dr",
    "4_night_fine" : "nf",
    "5_night_rain" : "nr",
    "crowd_a0.str" : "au_aw0.bin",
    "crowd_a1.str" : "au_aw1.bin",
    "crowd_a2.str" : "au_aw2.bin",
    "crowd_a3.str" : "au_aw3.bin",
    "crowd_h0.str" : "au_ho0.bin",
    "crowd_h1.str" : "au_ho1.bin",
    "crowd_h2.str" : "au_ho2.bin",
    "crowd_h3.str" : "au_ho3.bin",
    "stad1_main.bin" : "base.bin",
    "stad2_entrance.bin" : "data.bin",
    "stad3_adboards.bin" : "kb.bin",
}

ADBOARDS_4_FILE_NAMES = [
    "st_kb_tc_adikon.bin", #WE8I
    "st_kb_tc_deu.bin",
    "st_kb_tc_eng.bin",
    "st_kb_tc_eng_old.bin", #WE8IK
    "st_kb_tc_esp.bin",
    "st_kb_tc_fra.bin",
    "st_kb_tc_ita.bin",
    "st_kb_tc_konami.bin",
    "st_kb_tc_we8u.bin", #WE8I
    "st_kb_tc_we8um.bin", #WE8I
]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def read_file_to_buf(loc:str):
    file = open(loc, "rb")
    buf = file.read()
    file.close()
    return buf

def unzlib(file):
    file.seek(32)
    return io.BytesIO(zlib.decompress(file.read()))

def rezlib(file):
    file.seek(0,2)
    decompressed_size = file.tell()
    file.seek(0,0)
    compressed_buffer = zlib.compress(file.read(), level=9)
    tmp = io.BytesIO()
    tmp.write(ZLIB_MAGIC_NUMBER)
    tmp.write(struct.pack("<I", len(compressed_buffer)))
    tmp.write(struct.pack("<I", decompressed_size))
    tmp.write(bytearray([0]*20))
    tmp.write(compressed_buffer)
    tmp.seek(0)
    return tmp.read()




def fix_stadium_mdls(file, extra_buff1, extra_buff2):

    total_files, toc_offset = struct.unpack("<2I", file.read(8))
    
    file.seek(toc_offset)
    offsets = struct.unpack("<%dI" % total_files, file.read(total_files * 4))
    
    TOTAL_FILES_PES4_WE8 = 30
    new_offsets = [0] * TOTAL_FILES_PES4_WE8
    
    new_offsets[0:7] = offsets[0:7]
    new_offsets[10:15] = offsets[8:13]
    new_offsets[17] = offsets[13]
    new_offsets[23:28] = offsets[22:27]
    
    file.seek(0,2)
    new_offsets[28] = file.tell()
    file.write(extra_buff1)

    new_offsets[29] = file.tell()
    file.write(extra_buff2)

    file.seek(0)
    file.write(struct.pack("<I", TOTAL_FILES_PES4_WE8))
    file.seek(toc_offset)
    file.write(struct.pack("<%dI" % TOTAL_FILES_PES4_WE8, *new_offsets))
    
    file.seek(0)
    
    return file


def adboard_6to4(file_path, new_name):

    ad_template_path = resource_path("resources/ad.bin")


    file = open(file_path, "rb")
    file.read(32)
    total_files, toc_offset = struct.unpack("<2I", file.read(8))
    toc_offset +=32
    file.seek(toc_offset)
    files_offsets = (x + 32 for x in struct.unpack("<%dI" % total_files, file.read(total_files * 4)))
    
    adboard_files = []
    
    for file_offset in files_offsets:
        file.seek(file_offset)
        file.read(32)
        base_pos = file.tell()
        _, _, offset, offset_2 = struct.unpack("<4I", file.read(16))
        file.seek(offset + base_pos)
        _, size = struct.unpack("<2I", file.read(8))
        file.seek(offset + base_pos)
        tmp = unzlib(io.BytesIO(file.read(size+32)))
        _,_, ad_offset = struct.unpack("<3I", tmp.read(12))
        tmp.seek(ad_offset)
        adboard_files.append(tmp.read())
    
    file.close()
        
    new_adboard_mdls = io.BytesIO()
    new_adboard_mdls.write(struct.pack("<4I", 3, 8, 32, 32 + len(adboard_files[0])))
    new_adboard_mdls.write(bytearray([0]*16))
    
    
    for ad_file in adboard_files:
        new_adboard_mdls.write(ad_file)
        
        
    new_adboard_mdls.seek(0)
    
    cinematics = open(ad_template_path, "rb")
    cinematics_buff = cinematics.read()
    cinematics.close()

    new_adboard_mdls_buff = rezlib(new_adboard_mdls)

    
    o_file = open(new_name, "wb")
    o_file.write(FOLDER_MAGIC_NUMBER)
    o_file.write(struct.pack("<I", 16 + len(new_adboard_mdls_buff) + len(cinematics_buff)))
    o_file.write(bytearray([0]*24))
    o_file.write(struct.pack("<4I", 2, 8, 16, 16 +  len(new_adboard_mdls_buff)))
    o_file.write(new_adboard_mdls_buff)
    o_file.write(cinematics_buff)
    o_file.close()
    
    

def stad_6to4(file_path, new_name):
    file = open(file_path, "rb")
    file.read(32)
    file.read(8)
    offsets = [x + 32 for x in struct.unpack("<3I",file.read(12))]
    
    files_list = []
    
    for offset in offsets:
        file.seek(offset)
        _, size = struct.unpack("<2I", file.read(8))
        file.seek(offset)
        files_list.append(file.read(size + 32))
    
    file.close()
    
    mdl_29_path = resource_path("resources/mdl_29.bin")
    mdl_30_path = resource_path("resources/mdl_30.bin")
    
    mdl_29 = read_file_to_buf(mdl_29_path)
    mdl_30 = read_file_to_buf(mdl_30_path)
    
    stad_main_4 = fix_stadium_mdls(unzlib(io.BytesIO(files_list[-1])), mdl_29, mdl_30)
    files_list[-1] = rezlib(stad_main_4)
    
    o_file = open(new_name, "wb")
    o_file.write(FOLDER_MAGIC_NUMBER)
    
    total_size = sum(len(file) for file in files_list)
    
    o_file.write(struct.pack("<II", total_size, total_size))
    o_file.write(bytearray([0]*20))
    o_file.write(struct.pack("<5I", 3, 8, 32, 32 + len(files_list[0]), 32 + len(files_list[0]) + len(files_list[1])))
    o_file.write(bytearray([0]*12))
    for file in files_list:
        o_file.write(file)
    o_file.close()
    
def stadiums_names(idx):
    return STAD_NAMES.get(idx, "Invalid argument")    

def process_folder(folder, name):
    current_dir = Path.cwd()
    files = os.listdir(folder)
    weather = NAMES_CONVERTION.get(Path(folder).parts[-1])
    print(weather)
    for file in files:
        file_full_path = "%s/%s" % (folder, file)
        print(file)
        print(file_full_path)
        if file in CROWD_FILES_NAMES:
            source_file = Path(file_full_path)
            destination_file = Path("%s/%s%s_%s" % (current_dir, name, weather, NAMES_CONVERTION.get(file)))
            # copy the source file to the destination with a new name
            destination_file.write_bytes(source_file.read_bytes())
        elif file == "stad1_main.bin":
            new_name = "%s/%s%s_base.bin" % (current_dir, name, weather)
            print(new_name)
            stad_6to4(file_full_path, new_name)
        elif file == "stad3_adboards.bin":
            new_name = "%s/%s%s_kb.bin" % (current_dir, name, weather)
            print(new_name)
            adboard_6to4(file_full_path, new_name)

def process_adboards_tex(folder):
    adboard_full_path = "%s/default.bin" % folder
    print(adboard_full_path)
    if Path(adboard_full_path).is_file():
        current_dir = Path.cwd()
        source_file = Path(adboard_full_path)
        for name in ADBOARDS_4_FILE_NAMES:
            dst_adboard_path = "%s/%s" % (current_dir, name)
            print(dst_adboard_path)
            destination_file = Path(dst_adboard_path)
            destination_file.write_bytes(source_file.read_bytes())


def main():
    logging.basicConfig(filename='%s.log' % "stadium_converter", filemode='w', level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    try:
        dropped_folder = sys.argv[1]
        sub_folders = os.listdir(dropped_folder)
        for key, value in STAD_NAMES.items():
            print("%d - %s" % (key, value))
        while True:
            try:
                user_input = int(input("Please enter the number for the stadium you want to prepare your convertion, enter -1 to cancel: "))
                if 0 <= user_input <= 28:
                    break
                elif user_input == -1:
                    sys.exit()
                else:
                    raise ValueError("Number out of range.")
            except Exception as e:
                print("Invalid input: ", e)
        name = STAD_SHORT_NAME.get(user_input)
        for sub_folder in sub_folders:
            if sub_folder in FOLDERS_NAMES:
                full_path = "%s/%s" % (dropped_folder, sub_folder)
                print(full_path)
                process_folder(full_path, name)
            elif sub_folder == "adboards_tex":
                process_adboards_tex("%s/%s" % (dropped_folder, sub_folder))
    except Exception as e:
        tb_str = traceback.format_exc()
        logging.debug("An error has ocurred while running the script\nError Code: %s\n\nDetail:\n%s" % (e, tb_str)) ## TO DO LOGGING FILE

if __name__ == "__main__":
    main()
    