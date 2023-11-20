import os.path
import gspread

# The ID of the KKOLOSSUS spreadsheet
SPREADSHEET_ID = "1ZA4nVArbC3upnJDITz1zSU6CrPjOSMh3pvPMlEi_FvU"
# Name of the output
OUTPUT_FILE_NAME = "output.txt"
# Factions list
FACTIONS_LIST = ["Neutral","Aïma","Djaïn","Gaalden","Meli-Akumi"]
# Card template
CARD_TEMPLATE = "[\"XNAMEX\"]={Card=\"XCARDX\",Extension=\"XEXTENSIONX\",Illustrator=\"XILLUSTRATORX\",Faction=\"XFACTIONX\",Cost=XCOSTX,Exalted=XEXALTEDX,Types=XTYPESX,AttackPower=XATTACKX,Endurance=XENDURANCEX,Worship=XWORSHIPX,Traits=XTRAITSX,Effect=\"XEFFECTX\",Adoration=XADORATIONX,Swiftness=XSWIFTNESSX,Runes=XRUNESX,ElementalValue=XELEMVALUEX,ElementalIcons=XELEMICONSX,Locations=XLOCATIONSX},"
TYPES_TEMPLATE = "{\"Shadow\",\"Schemer\"}"
TRAITS_TEMPLATE = "{\"Reach\"}"
TEMPLATE_HEADER_WORSHIPERS = {
    "Name" : "XNAMEX",
    "Illustrator" : "XILLUSTRATORX",
    "Faction" : "XFACTIONX",
    "Cost" : "XCOSTX",
    "Exalted" : "XEXALTEDX",
    "Attack Power" : "XATTACKX",
    "Endurance" : "XENDURANCEX",
    "Worship" : "XWORSHIPX",
    "Effect" : "XEFFECTX"
}
TEMPLATE_HEADER_EVENTS = {
    "Name" : "XNAMEX",
    "Illustrator" : "XILLUSTRATORX",
    "Faction" : "XFACTIONX",
    "Cost" : "XCOSTX",
    "Effect" : "XEFFECTX",
    "Burst" : "XELEMVALUEX",
}
TEMPLATE_DEFAULT = {
    "XEXTENSIONX" : "Core Set",
    "XILLUSTRATORX" : "\"\"",
    "XFACTIONX" : "Neutral",
    "XCOSTX" : "0",
    "XEXALTEDX" : "false",
    "XTYPESX" : "{\"\"}",
    "XATTACKX" : "0",
    "XENDURANCEX" : "0",
    "XWORSHIPX" : "0",
    "XTRAITSX" : "{\"\"}",
    "XEFFECTX" : "",
    "XADORATIONX" : "0",
    "XSWIFTNESSX" : "0",
    "XRUNESX" : "{\"\"}",
    "XELEMVALUEX" : "0",
    "XELEMICONSX" : "{\"\"}",
    "XLOCATIONSX" : "{\"\"}"
}
# Max nb of traits
MAXIMUM_NUMBER_OF_TRAITS = 5


def main():
    gc = gspread.service_account(filename='config/kkolossus-credentials.json')

    # Open a spreadsheet by ID
    sh = gc.open_by_key(SPREADSHEET_ID)

    # Open output file
    os.remove(OUTPUT_FILE_NAME)
    export_tts = open(OUTPUT_FILE_NAME, "a", encoding="utf-8")

    # Write start of the file
    export_tts.write(
        "cardsLibrary={\n"
        "-- Base\n"
        "[\"Default\"]={Card=\"\",Extension=\"\",Illustrator=\"\",Faction=\"Neutral\",Cost=0,Exalted=false,Types={\"\"},AttackPower=0,Endurance=0,Worship=0,Traits={\"\"},Effect=\"\",Adoration=0,Swiftness=0,Runes={\"\"},ElementalValue=0,ElementalIcons=\"\",Locations={\"\"}},\n"
        "--================--\n"
        "-- == CORE SET == --\n"
        "--================--\n"
       )
    
    #==== WORSHIPERS ====
    # Get the sheets
    worshipers = sh.worksheet("WORSHIPERS").get_all_values()
    export_tts.write("-- = WORSHIPERS = --\n")
    # Filter by faction
    for faction in FACTIONS_LIST:
        export_tts.write("-- "+ faction + "\n")
        wsh_filtered = []
        col_faction = getColNumber(worshipers,"Faction")
        for i in worshipers:
            if i[col_faction] == faction:
                wsh_filtered.append(i)
        for wsh in wsh_filtered:
            # Create the line
            line_to_write = CARD_TEMPLATE
            # Name
            line_to_write = line_to_write.replace("XCARDX","Worshiper")
            # Automatic replaces
            for k,v in TEMPLATE_HEADER_WORSHIPERS.items():
                line_to_write = replaceTemplate(worshipers,line_to_write,wsh,k,v)
            # Types
            line_to_write = line_to_write.replace("XTYPESX",getTypesAsDict(getValueByColIntoList(worshipers,"Types",wsh)))
            # Traits
            line_to_write = line_to_write.replace("XTRAITSX",getTraitsAsDict(worshipers,wsh))
            # Finish line
            line_to_write = finishDefaultTemplate(line_to_write)
            export_tts.write(line_to_write+"\n")

    #==== EVENTS ====
    # Get the sheets
    events = sh.worksheet("EVENTS").get_all_values()
    export_tts.write("-- = EVENTS = --\n")
    # Filter by faction
    for faction in FACTIONS_LIST:
        export_tts.write("-- "+ faction + "\n")
        evt_filtered = []
        col_faction = getColNumber(events,"Faction")
        for i in events:
            if i[col_faction] == faction:
                evt_filtered.append(i)
        for evt in evt_filtered:
            # Create the line
            line_to_write = CARD_TEMPLATE
            # Name
            line_to_write = line_to_write.replace("XCARDX","Event")
            # Automatic replaces
            for k,v in TEMPLATE_HEADER_EVENTS.items():
                line_to_write = replaceTemplate(events,line_to_write,evt,k,v)
            # Types
            line_to_write = line_to_write.replace("XTYPESX",getTypesAsDict(getValueByColIntoList(events,"Types",evt)))
            # Traits
            line_to_write = line_to_write.replace("XELEMICONSX",getElemsAsDict(getValueByColIntoList(events,"Elements",evt)))
            # Finish line
            line_to_write = finishDefaultTemplate(line_to_write)
            export_tts.write(line_to_write+"\n")

    # Write the end of the file
    export_tts.write("}")
    export_tts.close()

def getElemsAsDict(elems_as_string):
    elem_dict = "{"
    types_table = elems_as_string.split("/")
    for t in types_table:
        elem_dict = elem_dict + "\"" + t.strip() + "\","
    elem_dict = elem_dict[:-1]+"}"
    return elem_dict

def getTraitsAsDict(sheet_as_table,line_as_list):
    traits_dict = "{"
    for i in range(1,MAXIMUM_NUMBER_OF_TRAITS):
        trait=getValueByColIntoList(sheet_as_table,"Trait"+str(i),line_as_list)
        if trait!="" :
            trait_value=getValueByColIntoList(sheet_as_table,"TValue"+str(i),line_as_list)
            if trait_value!="" :
                traits_dict = traits_dict + "\"" + trait + " " + trait_value + "\","
            else :
                traits_dict = traits_dict + "\"" + trait + "\","
    if traits_dict=="{":
        traits_dict="{}"
    else:
        traits_dict = traits_dict[:-1]+"}"
    return traits_dict

def getTypesAsDict(types_as_string):
    types_dict = "{"
    types_table = types_as_string.split(",")
    for t in types_table:
        types_dict = types_dict + "\"" + t.strip() + "\","
    types_dict = types_dict[:-1]+"}"
    return types_dict

def finishDefaultTemplate(line_to_write):
    finished_line = line_to_write
    for k,v in TEMPLATE_DEFAULT.items():
        finished_line=finished_line.replace(k,v)
    return finished_line

def replaceTemplate(sheet_as_table,line_to_write,line_as_list,col_name,template_in_the_line):
    return line_to_write.replace(template_in_the_line,getValueByColIntoList(sheet_as_table,col_name,line_as_list).replace("\n","&#x0d;"))

def getValueByColIntoList(sheet_as_table,col_name,line_as_list):
    return line_as_list[getColNumber(sheet_as_table,col_name)]

def getColNumber(sheet_as_table,col_header):
    return sheet_as_table[0].index(col_header)



if __name__ == "__main__":
  main()