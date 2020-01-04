import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Connect_to_qa_table():
    __sheet = None
    
    @staticmethod 
    def get_sheet():
        if Connect_to_qa_table.__sheet == None:
            Connect_to_qa_table()
        return Connect_to_qa_table().__sheet
    
    def __init__(self):
        if Connect_to_qa_table.__sheet == None:
            self.__create_sheet()
            Connect_to_qa_table.__sheet = self.__sheet
        else:
			Connect_to_qa_table.__sheet = self.__sheet
			
            
    def __create_sheet(self):
        __scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        __creds = ServiceAccountCredentials.from_json_keyfile_name('LQANOTES-bd9ecdf9dc77.json', __scope)
        __client = gspread.authorize(__creds)
        self.__sheet = __client.open('test_csv_sky_map').sheet1


def find_row_in_qa_table(pointing):
    sheet = Connect_to_qa_table().get_sheet()
    pointings = [str(p).split(" ")[0].strip() for p in sheet.col_values(2)[2:len(sheet.col_values(2))]]
    #print(pointings,  pointings.index(pointing)) 
    return pointings.index(pointing) + 3
        
        
def add_qa_note(note, pointing, type_of_note):

    if type_of_note == "calibrator":
        collon_nr = 9
    elif type_of_note == "target":
        collon_nr = 11
    elif type_of_note == "Imaging":
        collon_nr == 13
    else:
        print("Wronge type of note")
        
    row_nr = find_row_in_qa_table(pointing)
    
    sheet = Connect_to_qa_table().get_sheet()
    sheet.update_cell(row_nr, collon_nr, note)
