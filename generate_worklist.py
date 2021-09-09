import argparse
import re
import os
#import pdb

def parse_num_list(string):
    """
    a custom function to check the antibody carrier position id range as
    inputted from user and outputs as a list if valid
    """

    m = re.match(r'(\d+)(?:-(\d+))?$', string)
    if not m:
        raise argparse.ArgumentTypeError(f"'{string}' is not a range of numbers")
    start = m.group(1)
    end = m.group(2) or start
    return list(range(int(start,10), int(end, 10)+1))

parser = argparse.ArgumentParser(description = 'Generate worklist (*.csv)')
parser.add_argument('-n', '--ncols', metavar = 'NUMBER OF COLUMNS', type = int, nargs = 1, help =
                    'integer number of columns', required = True)
parser.add_argument('-fh', '--filehdl', metavar = 'FILEHANDLER', type = str, nargs = 1,
                    help = 'file handler type, write or append', required = True)
parser.add_argument('-pn', '--pltnbr', metavar = 'PLTNBR', type = int, nargs = 1,
                    help = 'the serial plate number that is destined to be, destination labware suffix', required = True)
parser.add_argument('-sn', '--srcnbr', metavar = 'SRCNBR', type = int, nargs = 1,
                    help = 'the source number that is to be aspirated from, source labware suffix', required = True)
parser.add_argument('-sl', '--srclabw', metavar = 'SRC_LABW', type = str, nargs = 1,
                    help = 'source labware without number suffix', required = True)
parser.add_argument('-dl', '--destlabw', metavar = 'DEST_LABW', type = str,
                    nargs = 1, help = 'destination labware without number suffix', required = True)
parser.add_argument('-v', '--vol', metavar = 'VOLUME', type = float, nargs
                    = 1, help = 'volume for aspirate/dispense', required = True)
parser.add_argument('-r', '--rev', metavar = 'REVERSE', type = str, nargs
                    = '?', help = 't/f whether positions are reversed')
parser.add_argument('-sp', '--srcpos', metavar = 'SRC_POS', type = str, nargs =
                    '+', help = 'source position is alphanumeric or integers (a/i); second argument: max number of positions on carrier')
parser.add_argument('-w', '--wl', metavar = 'WORKLIST', nargs = 1, type = str,
                    help = 'file path to worklist file', required = True)
parser.add_argument('-si', '--single', metavar = 'SINGLE_COLUMN', type = int,
                    nargs = '*', choices = range(1,96), help = 'single column to aspirate and dispense; input integer column number to replace the well column number; second argument is the additional increment to the source index position')
parser.add_argument('-ab', '--antib', metavar = 'NUM_ANTIBODIES', type = int, nargs
                    = '?', help = 'the number of antibodies per plate', required = True)
parser.add_argument('-ser', '--serial', metavar = 'SERIAL_DILUTION', type = str, nargs
                    = '*', help = '(t/f) create a serial dilution worklist with a shifted column to the left; second argument: the last index to stop prior to the waste concatenation')
parser.add_argument('-abs', '--abset', metavar = 'ANTIBODY_SET', type =
                    parse_num_list, nargs = 1, help = 'the set of antibodies that will be used for aspiration from linear rack carrier; requires a range of integers, i.e. 1-8')
parser.add_argument('-z', '--zeropad', metavar = 'ZERO_PADDING', type = int, nargs
                    = 2, choices=range(0,3), help = 'add zero padding for the labware; order is source and then destination; only accepts 0 (single zero padding) or 1 (triplicate zero padding); 2 is for no zero padding or integer number', required = True)
parser.add_argument('-tb', '--tubef', metavar = 'TUBE_FORMAT', type = int, nargs
                    = 3, choices = range(5), help = 'set the position id for tube format (across rows rather than down columns); 0 is to set for source only, 1 is source and destination, 2 is destination only; second argument is to set max based on 40-tube rack or carry on to subsequent racks (0 or 1); third argument is number of rows to exclude in order to account for preceding rack of 6-8 columns (antibodies)')
parser.add_argument('-sq', '--setsq', metavar = 'SET_SEQUENCE', type = int,
                    nargs = 2, choices = range(97), help = 'single integer to set an offset for the sequence within Venus; adds n number of index positions so that the core head will pick up from the middle of the trough')
parser.add_argument('-rf', '--ref', metavar = 'REF_ISO_COS_VIA', type = int,
                    nargs = 2, choices = range(0,9), help = 'number of rows to skip in order to create the sequence of isoref, ref, costain, viability; second argument is the starting row integer based number, second argument is what integer row number to start at')
parser.add_argument('-bf', '--buffer', metavar = 'ADD_BUFFER', type = int,
                    nargs = 2, choices = range(1,89), help = 'integer number to designate the starting column for the buffer asp/disp step or stamp; second argument is for starting column position for destiantion')
parser.add_argument('-cw', '--concwaste', metavar = 'CONCAT_WASTE', type = int,
                    nargs = 2, choices = range(2), help = '0 is for False and 1 is for True; concatenating the waste labware to the end of the serial titration worklist; second argument is to set a shift or not for serial dilution (related to --serial arg)')
parser.add_argument('-srd', '--serdown', metavar = 'SERIALDILUTE_DOWN', type = int, nargs = 3, choices = range(13), help = 'first argument is what column to change for alphanumeric wellids, second argument is the number to shift the source wellid, third argument is the number to shift the destination wellid')
parser.add_argument('-add', '--addsd', metavar = 'ADD_SOURCE_DEST', type = str, nargs = '+', choices = [x + y for x in [chr(l) for l in range(65,73)] for y in [chr(l) for l in range(65,73)]] + [str(x) for x in range(9)], help = 'first argument is the location where to change the pid (0=source, 1=destination, 2=both); second argument is to add to the source or destination position id a certain number of positions to shift it; the third and fourth argment are the source & destination column numbers to start at; fifth argument is concentration of both well id prefix for alphanumeric to change the original well id to, should be a letter such as AH')

headers = ["SOURCE_POSITION","SOURCE_LABWARE","DESTINATION_POSITION","DESTINATION_LABWARE","VOL"]
CR = "\n"
args = parser.parse_args()
parentdir = "C:\\Users\\10322096\\Documents\\data_files\\hamilton_worklist_tests"


def LETTERS():
    """
    create a dictionary of well id's (position ids) as the keys and the index number as the values
    """

    letters = dict()
    indices = dict()
    cnt = 0
    for i in range(1,13):
        for l in 'ABCDEFGH':
            wid = f"{l}{i}"
            letters[wid] = cnt
            indices[cnt] = wid
            cnt += 1
    return letters, indices

def generate_fields(well_type, CR, last_row, well_positions_tuple):
    """
    main function to generate each row for the worklist file. inputs the
    position id based on alphanumeric or integer based.
    """
    
    worklist = []
    if well_type == 'a':
        #print(well_positions_tuple)
        for ncol in range(*well_positions_tuple):
            for letter in row_letters:
                src_well_id = f"{letter}{ncol}"
                #if src_well_id == last_row:    CR = ""
                worklist.append(f"{src_well_id},{srclabw},{src_well_id},{destlabw},{args.vol[0]}{CR}")        
    elif well_type == 'i':
        assert len(args.srcpos) == 2, "required second argument for source position, max carrier positions"
        i = 1
        for ncol in range(*well_positions_tuple):
            for letter in row_letters:
                dest_well_id = f"{letter}{ncol}"
                #if dest_well_id == last_row:
                #    CR = ""
                src_well_id = i % max_pos
                if src_well_id == 0:
                    src_well_id = max_pos
                worklist.append(f"{src_well_id},{srclabw},{dest_well_id},{destlabw},{args.vol[0]}{CR}")
                i+=1
    last_row = worklist[-1].rstrip()
    worklist = worklist[:-1]    
    worklist.append(last_row)
    return worklist


def shift_wellid(worklist):
    """
    shift the well id or position id of the current labware (serial titration
    plate) 96-w format, one column over. This is for the high to low serial
    dilution step
    """

    new_worklist = []
    for r in worklist:
        row = r.split(",")
        wellid = int(row[2][1]) - 1
        replace_wellID = re.sub("[A-Z]{1}\d+", f"{row[2][0]}{wellid}", row[2])
        new_row = f"{row[0]},{row[1]},{replace_wellID},{row[3]},{row[4]}"
        new_worklist.append(new_row)
    last_row = new_worklist[-1].rstrip()
    new_worklist = new_worklist[:-1]    
    new_worklist.append(last_row)
    return new_worklist


def concat_waste(last_column, curr_wrklst):
    """
    concatenate the waste destination position for the last step of serial
    dilution, gets rid of the volume in last (low) concentration
    """

    positions = []
    CR = "\n"
    positions.append(CR)
    index = 0
    i = 0
    if args.srcpos[0] == 'i':
        index = len(curr_wrklst) + 1
    for letter in row_letters:
        if letter == row_letters[-1]:
            CR = ""
        if index > len(curr_wrklst):
            prefix = index + i
        else:
            prefix = f"{letter}{last_column}"
        positions.append(f"{prefix},{srclabw},{i+41},ST_L_NE_stack_0006,{args.vol[0]}{CR}")
        i += 1
    return positions

def set_wellid_number(worklist):
    """
    set the position id for the antibody well positions based on the integer
    number that is passed in. Used for single column aspirate/dispense to start
    the serial dilution. This is for the starting high concentration
    """
    new_worklist = []
    src_adder = 0

    try:
        abset = args.abset[0] # list of the range
        abset_range = len(abset)
        if abset[0] > 32:
            src_adder = 1
            abset = [x-32 for x in abset] # need this to move on to next labware that starts index at 1 again
    except Exception as e:
        print(f'error: {e}')

    for i, row in enumerate(worklist):
        row_ = row.split(",")
        if args.single: #replace column with new number specified
            row_[2] = re.sub("\d+", str(args.single[0]), row_[2])
        try:
            index = abset[i % abset_range]
            srclw = row_[1][:-1]
            srcnbr = int(row_[1][len(srclw)]) + src_adder
            srclw = f"{srclw}{srcnbr}"
            # print(f'{i} - {index} - {srclw}')
        except Exception as e:
            print(f'error  {e}')
            if args.srcpos[0] == "a" and args.serial[0].lower() == "t":
                # would be a nbr 1 colm -> 6 colm for 48 DWP                
                index = f"{row[0][0]}1"
            else:
                index = int(row_[0])
            srclw = row_[1]
            if srclabw.startswith("Ham"):
                #print('test')
                if len(args.single) > 1:
                    index += int(args.single[1])
        new_row = f"{index},{srclw},{row_[2]},{row_[3]},{row_[4]}"
        new_worklist.append(new_row)
    return new_worklist

def set_tube_format(worklist):
    """
    set the position id for tube vertical tube rack format. The well positions
    will be down rows of tube rack A1,A2,A3... etc. two args: 1) 0,1,2 for src
    and destination max limit; 2) allow to carry on to next rack (for 8 columns
    of antibodies rather than 5)
    """
    new_worklist = []
    colnbrs = [x for x in range(1,args.antib+1)]
    rletters = [[x]*args.antib for x in row_letters[:5]] # 5 is max rows of 40 tube rack
    rletters = [l for sl in rletters for l in sl] # [A,A,A,...B,B,B,... C,C,C...]
    #print(rletters)
    len_rletters = len(rletters)
    row_idx = args.tubef[0]
    # 1 means source and dest, 0 is source only, 2 is dest only
    both_lw = False
    if row_idx == 0:
        lw_idx = 1
    elif row_idx == 1:
        both_lw = True
        row_idx = 0
        lw_idx = 1
        lw_idx2 = 3
    elif row_idx == 2:
        lw_idx = 3
    # if index based
    if args.srcpos[0].lower() == 'i':
        row_idx = 2

    for i, row in enumerate(worklist):
        row_ = row.split(",")
        lw = row_[lw_idx]
        if both_lw:
            lw2 = row_[lw_idx2]
        if letters[row_[row_idx]] == 40 and args.tubef[1] == 1:
            # max is 40 tubes (goes up to Letter 'E' only)
            last_row = len(new_worklist)-1
            new_worklist[last_row] = new_worklist[last_row].rstrip() # remove CR
            return new_worklist
        if letters[row_[row_idx]] >= 40:
            # increment the 40Tube rack to next labware id
            try:
                regex = re.search("(.+)(\d{2,})", row_[lw_idx])
                idx_pos = int(regex.group(2)) + 1
                lw = f"{regex.group(1)}{zero_pad}{idx_pos}"
            except Exception:
                lw = row_[lw_idx]
            if both_lw:
                try:
                    regex = re.search("(.+)(\d{2,})", row_[lw_idx2])
                    idx_pos = int(regex.group(2)) + 1
                    lw2 = f"{regex.group(1)}{zero_pad}{idx_pos}"
                except Exception:
                    lw2 = row_[lw_idx2]

        replace_wellID = re.sub("[A-H]\d+", f"{rletters[i % len_rletters]}{colnbrs[i % args.antib]}", row_[row_idx])
        if args.tubef[0] == 2:
            new_row = f"{row_[0]},{row_[1]},{replace_wellID},{lw},{row_[4]}"
        elif args.tubef[0] == 1:
            new_row = f"{replace_wellID},{lw},{replace_wellID},{lw2},{row_[4]}"
        elif args.tubef[0] == 0:
            new_row = f"{replace_wellID},{lw},{row_[2]},{row_[3]},{row_[4]}"

        new_worklist.append(new_row)


    if srclabw.startswith('Serial') or srclabw.startswith('Reformat'):
        new_pid = generate_default_pids()
        new_worklist = [reassign_pid(i, p, new_pid, 'src') for i,p in enumerate(new_worklist)]
    #print(new_worklist)
    return new_worklist

def reassign_pid(idx, pid_row, pid_list, position):
   if position == 'src':       
       #print(idx,pid_row,pid_list, position)
       return pid_list[idx] + pid_row[pid_row.index(","):]
   elif position == 'dst':
       row_ = pid_row.split(',')
       return f"{row_[0][:2]},{row_[1]},{pid_list[idx]},{row_[3]},{row_[4]}"


def generate_default_pids():
    lets = [[l]*8 for l in 'ABCDEFGH']
    lets = [l for sl in lets for l in sl]
    nbrs = [x for x in range(1,9)]*8
    new_pid = [f"{a}{b}" for a, b in zip(lets, nbrs)]
    return new_pid

def partial_displace(worklist, rows):
    """
    displace partially the worklist for the current 40 tube rack and continue
    in subsequent 40Tube rack. This rack dispalces the first n rows into the
    following labware id rack; rows is the number of rows to skip (1-5)
    """

    adder = 3
    #if args.tubef[2] == 1:
    #    adder += 1
    
    def get_pid(row, idx):
       return row.split(',')[idx]

    # def reassign_pid(idx, pid_row, pid_list):
    #     return pid_list[idx] + pid_row[pid_row.index(","):]
    copy_wl = worklist[:]
    copy_wl[len(copy_wl)-1] = copy_wl[len(copy_wl)-1] + "\n"

    # orig_dst_pid = [get_pid(p, 2) for p in copy_wl]

    #cnt_letter_dct = {k:0 for k in 'ABCDEFGH'}
    num_rows = int(rows*8)
    partial_worklist_bottom = []
    cnt = 0
    for i in range(num_rows):
        dpl_row = copy_wl.pop(i-cnt) # remove first and subsequent up to num_rows
        spl_row = dpl_row.split(",")
        if args.tubef[0] in [1,2]: # if both src/dst or just dst
            letter = spl_row[2][0] # the letter of wellid
            #cnt_letter_dct[letter] += 1 # count the letter
            ord_d_pid = ord(letter) + adder # add three
            ord_d_pid = ord_d_pid % 70
            if ord_d_pid < 65:
                ord_d_pid += 65
            ord_d_pid = chr(ord_d_pid)
            try:
                #dstlw_cnt = int(spl_row[3][-1]) + 1 # get the last suffix num of dest lw cnt
                dstlw_cnt = int(spl_row[3][-1]) 
                if args.tubef[2] > 1:
                    dstlw_cnt += 1
                if ord_d_pid in ['A','B']:
                    dstlw_cnt += 1
            except Exception:
                dstlw_cnt = spl_row[3][-1]
            dstlw = f"{spl_row[3][:-1]}{dstlw_cnt}"
        else:
            dstlw = spl_row[3]
        #print(dstlw)

        if args.tubef[0] in [0,1]: # if just src or only or src/dst
            letter = spl_row[0][0]
            #cnt_letter_dct[letter] += 1
            ord_s_pid = ord(letter) + adder
            ord_s_pid = ord_s_pid % 70
            if ord_s_pid < 65:
                ord_s_pid += 65
            ord_s_pid = chr(ord_s_pid)
            try:
                srclw_cnt = int(spl_row[1][-1]) + 1
                if ord_s_pid in ['A','B']:
                    srclw_cnt += 1
            except Exception:
                srclw_cnt = spl_row[1][-1]

            srclw = f"{spl_row[1][:-1]}{srclw_cnt}"
            spl_row[1] = srclw
            if args.tubef[0] != 1:
                ord_d_pid = spl_row[2][0]
        else:
            ord_s_pid = spl_row[0][0]

        n_row = f"{ord_s_pid}{spl_row[0][1:]},{spl_row[1]},{ord_d_pid}{spl_row[2][1:]},{dstlw},{spl_row[4]}"
        partial_worklist_bottom.append(n_row)
        cnt += 1

    # partial_worklist_bottom = [reassign_pid(i, p, orig_dst_pid, 'dst') for i,p in
    #                            enumerate(copy_wl[:num_rows])]

    # print(cnt_letter_dct)
    # print(sum(cnt_letter_dct.values()))
    rotated_worklist = copy_wl + partial_worklist_bottom
    
    if srclabw.startswith('Serial') or srclabw.startswith('Reformat'):
        new_pid = generate_default_pids()
        rotated_worklist = [reassign_pid(i, p, new_pid, 'src') for i,p in enumerate(rotated_worklist)]

    if destlabw.startswith('Serial') or destlabw.startswith('Reformat'):
        new_pid = generate_default_pids()
        rotated_worklist = [reassign_pid(i, p, new_pid, 'dst') for i,p in enumerate(rotated_worklist)]

    if args.srcpos[0].lower() == 'i':
        if int(rotated_worklist[0][0]) != 1:
            new_pid = [str(x) for x in range(1, int(args.srcpos[1])+1)]*len(rotated_worklist)
            rotated_worklist = [reassign_pid(i, p, new_pid, 'src') for i,p in enumerate(rotated_worklist)]
    
    rotated_worklist[len(rotated_worklist)-1] = rotated_worklist[len(rotated_worklist)-1].rstrip()
    return rotated_worklist

def set_seq(worklist):
    """
    set the seqeuence within venus so that it picks up from the middle of the
    trough and not at the left-most index position. Adds an offset passed by
    setsq argument
    """

    new_worklist = []
    max_pos = args.antib
    if args.setsq[1] > 0:
        max_pos = args.setsq[1]
    limiter = [x for x in range(args.setsq[0], args.setsq[0] + max_pos)]
    for i, row in enumerate(worklist):
        row_ = row.split(",")
        index = limiter[i%len(limiter)]
        new_row = f"{index},{row_[1]},{row_[2]},{row_[3]},{row_[4]}"
        new_worklist.append(new_row)
    return new_worklist

def skip_rows_for_ref(worklist, skip, start):
    """
    set the number of rows to skip for the additional dispense of references,
    iso-references, viability and co-stain. The skip variable is an integer that
    will increment the alphanumeric well id to a new skipped value
    """
    new_worklist = []
    first_row = worklist[start]
    decr_start = 0
    if start > 0:
        decr_start = 1
    row_ = first_row.split(",")
    first_wellid = row_[2]
    first_letter = ord(first_wellid[0])
    # print(first_letter)
    for i in range(start-decr_start, len(worklist)):
        row_ = worklist[i]
        row_ = row_.split(",")
        wellid = row_[2]
        colm = wellid[1:]
        letter = chr(first_letter + skip*i)
        # print(f'{letter}-{i}')
        new_row = f"{row_[0]},{row_[1]},{letter}{colm},{row_[3]},{row_[4]}"
        new_worklist.append(new_row)
    return new_worklist


# def incr_dest_colm(worklist, source_shift, start_col):
def incr_src_colm(worklist, source_shift):
    """
    iterate over worklist list and shift the columns to the start_col integer
    number; for buffer stamp or asp/disp step; or for mixing of several columns
    """

    new_worklist = []
    # start_idx = ((start_col-1)*8)
    # if source_shift == 0:
    #     source_shift += 1
    for i, row in enumerate(worklist):
        row_ = row.split(",")
        # wellid = indices[start_idx+i]
        srcid = source_shift + i
        if srclabw.startswith("Serial") and destlabw.startswith("Serial"):
            srcid = indices[srcid-1]
        dstid = row_[2][0]
        dstid += f"{args.buffer[1]+int(row_[2][1:])}"
        # new_row = f"{srcid},{row_[1]},{wellid},{row_[3]},{row_[4]}"
        new_row = f"{srcid},{row_[1]},{dstid},{row_[3]},{row_[4]}"
        new_worklist.append(new_row)    
    return new_worklist


# def partial_displace(worklist, rows):
#     """
#     displace partially the worklist for the current 40 tube rack and continue
#     the in subsequent 40Tube rack. This rack dispalces the first n rows into the
#     following labware id rack
#     """

#     if srclabw.startswith('Serial'):
#         get_pid = lambda p: p.split(',')[0]
#         orig_src_pid = [get_pid(p) for p in worklist]

#     last_letter = re.search(",([A-H])\d{1,},", worklist[len(worklist)-1]).group(1)
#     ord_last_letter = ord(last_letter)
#     start = ord_last_letter - 64
#     get_index = lambda x: x % 5
#     replacement_pids = [[row_letters[get_index(i)]]*8 for i in range(start, start + 5)]
#     replacement_pids = [l for sl in replacement_pids for l in sl]
#     partial_worklist = ["\n"]
#     start = int(rows*8)
#     unq_letters = set()

#     for i, row in enumerate(worklist[:start]):
#         row_ = row.split(",")
#         regex = re.search("(.+)(\d{2,})", row_[3])
#         idx_pos = int(regex.group(2)) + 1
#         destlw = f"{regex.group(1)}{zero_pad}{idx_pos}"
#         pid = f"{replacement_pids[i]}{row_[2][1:]}"
#         if i > 39-start:
#             unq_letters.add(pid)
#         if pid in unq_letters:
#             destlw = f"{regex.group(1)}{zero_pad}{idx_pos+1}"
#         partial_worklist.append(f"{row_[0]},{row_[1]},{pid},{destlw},{row_[4]}")
#     partial_worklist[len(partial_worklist)-1] = partial_worklist[len(partial_worklist)-1].rstrip()
#     return worklist[start:] + partial_worklist


def reset_well_pos_serial(well_positions_tuple):    
    assert len(args.serial) == 2, "must supply a boolean (t/f) and the last index (int)"
    assert int(args.serial[1]), "second argument must be an integer"
    if args.serial[0].lower()[0] == 't':        
        last_index = int(args.serial[1])
        well_positions_tuple = (ncols, last_index, -1)        
    return well_positions_tuple

def dilute_step_down(worklist, column, src_adder, dst_adder):
    """
    change the well id for source or destination  for downwards dilution step on 96w plate for a particular column. This is for dilution of the isorefs and refs in columns 9-12; LEGO script
    """
    #assert src_adder in [0,1], "can only skip 0 or 1 rows"
    #assert dst_adder in [0,1], "can only skip 0 or 1 rows"

    start_ascii = 65
    start_src = start_ascii + src_adder
    start_dst = start_ascii + dst_adder
    new_worklist = []
    for i, row in enumerate(worklist):
        row_ = row.split(",")
        char_src = chr(start_src + (i*2))
        char_src = f"{char_src}{column}" 
        char_dst = chr(start_dst+ (i*2))
        char_dst = f"{char_dst}{column}"
        new_row = f"{char_src},{row_[1]},{char_dst},{row_[3]},{row_[4]}"
        #print(new_row)
        new_worklist.append(new_row)
    return new_worklist


def incr_pid(worklist, location, adder, src_colm_nbr=0, dst_colm_nbr=0, concat_letters=None):
    """
    increment the position id or well id of the labware, location would either be 0 (source), 1 (destination) or 2 (both), colm_nbr is the starting column number to begin the well id at; in this case it is for the vertically positioned 40-tube rack and Reformat 96-w plate; concat_letters are letters A-H for source and destination starting well ids
    """
    adder = int(adder)
    src_colm_nbr = int(src_colm_nbr)
    dst_colm_nbr = int(dst_colm_nbr)

    if concat_letters:
        src_start_letter, dst_start_letter = (l for l in concat_letters)

    new_worklist = []
    for i, row in enumerate(worklist):
        row_ = row.split(",")
        dst_pid = row_[2]
        dst_colm = int(dst_pid[1:]) + dst_colm_nbr
        dst_letter = dst_pid[0]
        src_pid = row_[0]
        src_letter = src_pid[0]
        if re.search('[A-H]', src_pid):
            src_colm =  int(src_pid[1:]) + src_colm_nbr
        else:
            src_colm = src_pid[1:]
        if location in ["0", "2"]:
            src_ascii_nbr = ord(src_letter)
            src_letter = chr(src_ascii_nbr + adder)
        if location in ["1", "2"]:
            dst_ascii_nbr = ord(dst_letter)
            dst_letter = chr(dst_ascii_nbr + adder)
        if concat_letters:
            src_letter = src_start_letter
            dst_letter = dst_start_letter
        new_row = f"{src_letter}{src_colm},{row_[1]},{dst_letter}{dst_colm},{row_[3]},{row_[4]}"
        new_worklist.append(new_row)
    return new_worklist

if __name__ == "__main__":
    letters, indices = LETTERS()
    row_letters = [chr(i) for i in range(65,65+args.antib)]
    ncols = int(args.ncols[0])
    well_positions_tuple = (1, ncols+1)
    last_row = f'{row_letters[-1]}{ncols}'
    zero_pad = '0'
    srclabw = args.srclabw[0]
    destlabw = args.destlabw[0]

    if args.zeropad[0] == 1:
        zero_pad += '00'

    if args.zeropad[0] != 2:
        srclabw += f'_{zero_pad}'
        srclabw += str(args.srcnbr[0])

    zero_pad = '0'
    if args.zeropad[1] == 1:
        zero_pad += '00'

    if args.zeropad[1] != 2:
        destlabw += f'_{zero_pad}'
        destlabw += str(args.pltnbr[0])

    if args.rev:
        bln_reverse = args.rev[0]
        last_row = f'{row_letters[-1]}2'
        last_index = 1        
        # if passed in 'true'
        #if bln_reverse[0].lower()[0] == 't':

    #print(well_positions_tuple)
    if args.serial:
        bln_concat_waste = bool(args.concwaste[0])
        last_row = f'{row_letters[-1]}{args.serial[1]}'
        well_positions_tuple = reset_well_pos_serial(well_positions_tuple)
    

    well_type = args.srcpos[0].lower()
    if len(args.srcpos) == 2:
        assert int(args.srcpos[1]), "second argument wrong data type"
        max_pos = int(args.srcpos[1])
    with open(os.path.normpath(args.wl[0]), args.filehdl[0]) as f:
    
        if args.filehdl[0] == 'w':
            f.write(",".join(headers) + "\n")
        elif args.filehdl[0] == 'a':
            f.write("\n")
        
        worklist = generate_fields(well_type, CR, last_row, well_positions_tuple)
        
        if args.abset or args.single:
            worklist = set_wellid_number(worklist)        
        if args.ref:
            worklist = skip_rows_for_ref(worklist, args.ref[0], args.ref[1])
        if args.serial:            
            if args.concwaste[1] == 0 and args.serial[1] == "6": # no shift for serial dilution                
                worklist = set_wellid_number(worklist)            
            else:
                worklist = shift_wellid(worklist)
            if bln_concat_waste:
                worklist = worklist + concat_waste(args.serial[1], worklist)
        if args.setsq:
            worklist = set_seq(worklist)
        if args.tubef:
            worklist = set_tube_format(worklist)
            
            worklist = partial_displace(worklist, args.tubef[2])
            #print(worklist)
        if args.buffer:
            worklist = incr_src_colm(worklist, args.buffer[0])
        if args.serdown:
            worklist = dilute_step_down(worklist, args.serdown[0], args.serdown[1], args.serdown[2])
        if args.addsd: # add src dest adders
            if len(args.addsd) > 2:
                worklist = incr_pid(worklist, args.addsd[0], args.addsd[1], args.addsd[2], args.addsd[3], args.addsd[4])
            else:
                worklist = incr_pid(worklist, args.addsd[0], args.addsd[1])

        for row in worklist:
            f.write(row)

    print('-'*30)
    print('completed worklist generation!')
    print('-'*30)
