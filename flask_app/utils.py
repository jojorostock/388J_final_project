from datetime import datetime

def current_time() -> str:
    return datetime.now().strftime('%B %d, %Y at %H:%M:%S')

def current_date_tuple():
	d = datetime.now().date
	return (datetime.now().date().year, datetime.now().date().month, datetime.now().date().day)

def extract_date_tuple(date_str):
	toks = date_str.split('-')
	year = int(toks[0])
	month = int(toks[1])
	day = int(toks[2])
	return (year, month, day)